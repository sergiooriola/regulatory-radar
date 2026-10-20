"""Polite cached HTTP GET for spike S2. Throwaway; not imported by the product.

Usage: python3.14 fetch.py URL [URL ...]   prints the cache path of each response.

- At most one request per second per host (across runs, via a timestamp file), or the
  host's robots.txt Crawl-delay if longer (www.bocm.es asks for 10 seconds).
- A User-Agent naming the project.
- robots.txt is honoured for every host, with RFC 9309 matching (longest rule wins, Allow
  wins a tie, `*` and `$` supported); the standard library's robotparser does not support
  wildcards, which BOCM's rules use.
- Each response is cached under .cache/ (git-ignored) and never fetched twice. Server errors
  and network failures are not cached; they are retried up to three times, a minute apart.
- A lock file per host keeps two processes from fetching from the same host at once.
"""

import fcntl
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = (
    "regulatory-radar-spike/0.1 (+https://github.com/sergiooriola/regulatory-radar)"
)
HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache"
MIN_INTERVAL = 1.0
RETRIES = 3
RETRY_WAIT = 60.0


class Robots:
    """The group of a robots.txt that applies to every user agent (`*`)."""

    def __init__(self, text: str) -> None:
        self.rules: list[tuple[bool, str]] = []
        self.crawl_delay = 0.0
        applies = False
        in_agents = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            key = key.lower()
            if key == "user-agent":
                if not in_agents:
                    applies = False
                in_agents = True
                applies = applies or value == "*"
                continue
            in_agents = False
            if not applies:
                continue
            if key in ("allow", "disallow") and value:
                self.rules.append((key == "allow", value))
            elif key == "crawl-delay":
                self.crawl_delay = float(value)

    @staticmethod
    def _matches(pattern: str, path: str) -> bool:
        regex = re.escape(pattern).replace(r"\*", ".*")
        if regex.endswith(r"\$"):
            regex = regex[:-2] + "$"
        return re.match(regex, path) is not None

    def can_fetch(self, url: str) -> bool:
        parts = urllib.parse.urlsplit(url)
        path = parts.path or "/"
        if parts.query:
            path += "?" + parts.query
        best: tuple[int, bool] = (-1, True)
        for allow, pattern in self.rules:
            if self._matches(pattern, path):
                candidate = (len(pattern), allow)
                if candidate > best:
                    best = candidate
        return best[1]


_robots: dict[str, Robots] = {}


def _cache_path(url: str) -> Path:
    digest = hashlib.sha256(url.encode()).hexdigest()[:24]
    return CACHE / urllib.parse.urlsplit(url).netloc / digest


def _download_once(url: str, interval: float) -> tuple[int, dict[str, str], bytes]:
    host_dir = CACHE / urllib.parse.urlsplit(url).netloc
    host_dir.mkdir(parents=True, exist_ok=True)
    stamp = host_dir / ".last-request"
    with open(host_dir / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            last = float(stamp.read_text())
        except (FileNotFoundError, ValueError):
            last = 0.0
        delay = last + interval - time.time()
        if delay > 0:
            time.sleep(delay)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.status, dict(response.headers), response.read()
        except urllib.error.HTTPError as error:
            return error.code, dict(error.headers), error.read()
        finally:
            stamp.write_text(str(time.time()))


def _download(url: str, interval: float) -> tuple[int, dict[str, str], bytes]:
    for attempt in range(RETRIES + 1):
        try:
            status, headers, body = _download_once(url, interval)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            status, headers, body = 0, {}, str(error).encode()
        if 0 < status < 500:
            return status, headers, body
        if attempt < RETRIES:
            print(f"retrying {url} after status {status}", file=sys.stderr)
            time.sleep(RETRY_WAIT)
    raise RuntimeError(f"{url} failed after {RETRIES + 1} attempts: {status}")


def robots_for(url: str) -> Robots:
    parts = urllib.parse.urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots:
        status, _, body = fetch_raw(origin + "/robots.txt", check_robots=False)
        text = "" if status >= 400 else body.decode("utf-8", "replace")
        _robots[origin] = Robots(text)
    return _robots[origin]


def fetch_raw(url: str, check_robots: bool = True) -> tuple[int, dict[str, str], bytes]:
    """Return (status, headers, body), from the cache when possible."""
    path = _cache_path(url)
    meta = path.with_suffix(".json")
    if meta.exists():
        info = json.loads(meta.read_text())
        return info["status"], info["headers"], path.read_bytes()
    interval = MIN_INTERVAL
    if check_robots:
        robots = robots_for(url)
        if not robots.can_fetch(url):
            raise PermissionError(f"robots.txt disallows {url}")
        interval = max(interval, robots.crawl_delay)
    status, headers, body = _download(url, interval)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    meta.write_text(
        json.dumps(
            {
                "url": url,
                "status": status,
                "headers": headers,
                "fetched": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            },
            indent=1,
        )
    )
    return status, headers, body


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        status, headers, body = fetch_raw(arg)
        print(status, headers.get("Content-Type"), len(body), _cache_path(arg), arg)
