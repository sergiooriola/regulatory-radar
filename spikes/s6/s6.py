"""Spike S6: AWS account and model access. Throwaway code, never imported by anything else.

Standard library only. Every AWS call goes through the AWS CLI v2 with the
`radar` profile (IAM Identity Center), so this script never sees a credential.
Raw CLI output is kept under cache/ (git-ignored); what goes to results/ has
every 12-digit AWS account ID replaced, because this repository is public.

    python3.14 -I s6.py profiles          # free: which Regions each EU profile uses
    python3.14 -I s6.py quotas            # free: applied tokens-per-minute quotas
    python3.14 -I s6.py invoke --calls 5  # paid: a few cents at most
    python3.14 -I s6.py probe eu.anthropic.claude-sonnet-5  # one call, to tell gates apart
    python3.14 -I s6.py trail             # free: where CloudTrail says each call ran
"""

import argparse
import csv
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
RESULTS = HERE / "results"
PROFILE = "radar"
REGION = "eu-south-2"
MODELS = {"haiku": "anthropic.claude-haiku-5-5", "sonnet": "anthropic.claude-sonnet-5-5"}
GEO_PREFIX = "eu."
MAX_CALLS = 10  # per model; a guard against a typo in --calls

# Regions in EU member states. eu-central-2 (Zurich) and eu-west-2 (London) carry
# the "eu-" prefix but are outside the European Union, so they are not here.
EU_MEMBER_STATE_REGIONS = {
    "eu-central-1": "Germany",
    "eu-north-1": "Sweden",
    "eu-south-1": "Italy",
    "eu-south-2": "Spain",
    "eu-west-1": "Ireland",
    "eu-west-3": "France",
}

# The request is deliberately tiny: S6 asks whether the account can invoke the
# models and where they run, not how well they answer.
REQUEST = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 256,
    "output_config": {"effort": "low"},
    "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
}

ACCOUNT_ID = re.compile(r"\b\d{12}\b")


def redact(text):
    return ACCOUNT_ID.sub("<account>", text)


def aws(*args, region=REGION):
    """Run an AWS CLI command and return its parsed JSON output."""
    cmd = ["aws", *args, "--profile", PROFILE, "--region", region, "--output", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        sys.exit(f"{' '.join(args[:2])} failed:\n{redact(proc.stderr.strip())}")
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def write_csv(name, rows):
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: redact(str(v)) for k, v in row.items()})
    print(f"wrote {path.relative_to(HERE)} ({len(rows)} rows)")


def append_csv(name, rows):
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / name
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        if new:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: redact(str(v)) for k, v in row.items()})
    print(f"appended to {path.relative_to(HERE)} ({len(rows)} rows)")


def region_of(arn):
    return arn.split(":")[3]


# --- commands ----------------------------------------------------------------


def cmd_profiles(_args):
    """Where each model's EU inference profile can route to, and the model's access state."""
    rows = []
    for name, model in MODELS.items():
        profile_id = GEO_PREFIX + model
        profile = aws(
            "bedrock", "get-inference-profile", "--inference-profile-identifier", profile_id
        )
        regions = sorted({region_of(m["modelArn"]) for m in profile.get("models", [])})
        outside = [r for r in regions if r not in EU_MEMBER_STATE_REGIONS]
        availability = aws("bedrock", "get-foundation-model-availability", "--model-id", model)
        rows.append(
            {
                "model": name,
                "profile_id": profile_id,
                "profile_status": profile.get("status"),
                "profile_type": profile.get("type"),
                "destination_regions": " ".join(regions),
                "regions_outside_eu": " ".join(outside) or "none",
                "agreement": availability.get("agreementAvailability", {}).get("status"),
                "authorization": availability.get("authorizationStatus"),
                "entitlement": availability.get("entitlementAvailability"),
                "checked_at": now(),
            }
        )
    write_csv("profiles.csv", rows)
    for row in rows:
        print(
            f"{row['model']}: {row['destination_regions']}"
            f" | outside EU: {row['regions_outside_eu']} | agreement {row['agreement']}"
        )


def cmd_quotas(_args):
    """Applied and AWS-default tokens-per-minute quotas for Claude via cross-Region inference."""

    def claude_tpm(command):
        page = aws(
            "service-quotas", command, "--service-code", "bedrock",
            "--query", "Quotas[?contains(QuotaName, `Claude`)"
            " && contains(QuotaName, `ross-region model inference tokens per minute`)]",
        )  # fmt: skip
        return {q["QuotaCode"]: q for q in page}

    applied = claude_tpm("list-service-quotas")
    default = claude_tpm("list-aws-default-service-quotas")
    rows = [
        {
            "quota": q["QuotaName"],
            "code": code,
            "aws_default": int(q["Value"]),
            "applied": int(applied[code]["Value"]) if code in applied else "default",
            "checked_at": now(),
        }
        for code, q in sorted(default.items(), key=lambda item: item[1]["QuotaName"])
        if re.search(r"Claude (Haiku|Sonnet|Opus) (5|4\.5)", q["QuotaName"])
    ]
    write_csv("quotas.csv", rows)
    for row in rows:
        print(f"{row['quota']}: default {row['aws_default']}, applied {row['applied']}")


def invoke_once(model_id, label, effort=True):
    """Call one model once through bedrock-runtime and return a result row; errors are recorded."""
    CACHE.mkdir(exist_ok=True)
    body = CACHE / "request.json"
    request = REQUEST if effort else {k: v for k, v in REQUEST.items() if k != "output_config"}
    body.write_text(json.dumps(request), encoding="utf-8")
    out = CACHE / f"invoke-{label}.json"
    started = now()
    t0 = time.monotonic()
    proc = subprocess.run(
        [
            "aws", "bedrock-runtime", "invoke-model",
            "--model-id", model_id,
            "--body", f"fileb://{body}",
            "--content-type", "application/json",
            "--accept", "application/json",
            "--profile", PROFILE, "--region", REGION,
            str(out),
        ],
        capture_output=True,
        text=True,
        check=False,
    )  # fmt: skip
    elapsed = time.monotonic() - t0
    row = {"model_id": model_id, "started_at": started, "seconds": f"{elapsed:.2f}"}
    if proc.returncode != 0:
        error = re.search(r"\((\w+)\) when calling", proc.stderr)
        message = proc.stderr.strip().split(" operation: ", 1)[-1]
        return row | {
            "outcome": error.group(1) if error else "error",
            "detail": message[:160],
            "response_model": "",
            "stop_reason": "",
            "input_tokens": "",
            "output_tokens": "",
        }
    response = json.loads(out.read_text(encoding="utf-8"))
    usage = response.get("usage", {})
    text = " ".join(
        b.get("text", "") for b in response.get("content", []) if b.get("type") == "text"
    )
    return row | {
        "outcome": "ok",
        "detail": text.strip()[:40],
        "response_model": response.get("model"),
        "stop_reason": response.get("stop_reason"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }


def cmd_invoke(args):
    """Invoke each model through its EU inference profile and record what came back."""
    if not 1 <= args.calls <= MAX_CALLS:
        sys.exit(f"--calls must be between 1 and {MAX_CALLS}")
    rows = []
    for name, model in MODELS.items():
        for i in range(1, args.calls + 1):
            row = invoke_once(GEO_PREFIX + model, f"{name}-{i}")
            rows.append({"model": name, "call": i} | row)
            print(f"{name} #{i}: {row['outcome']} {row['stop_reason']} {row['detail']}")
            if row["outcome"] != "ok":
                break  # the same error would repeat; one is enough to record it
    write_csv("invocations.csv", rows)


def cmd_probe(args):
    """One call to each given model or profile ID, to tell an account block from a model gate."""
    rows = []
    for model_id in args.model_ids:
        row = invoke_once(
            model_id, "probe-" + model_id.replace(":", "_"), effort=not args.no_effort
        )
        rows.append(row)
        print(f"{model_id}: {row['outcome']} {row['detail']}")
    append_csv("probes.csv", rows)


def cmd_trail(args):
    """Read the InvokeModel events from CloudTrail event history (free) and where each ran."""
    start = args.since or first_invocation()
    events = []
    token = None
    while True:
        extra = ["--next-token", token] if token else []
        page = aws(
            "cloudtrail",
            "lookup-events",
            "--lookup-attributes",
            "AttributeKey=EventName,AttributeValue=InvokeModel",
            "--start-time",
            start,
            *extra,
        )
        events.extend(page.get("Events", []))
        token = page.get("NextToken")
        if not token:
            break
    rows = []
    for event in sorted(events, key=lambda e: e["EventTime"]):
        detail = json.loads(event["CloudTrailEvent"])
        inference_region = (detail.get("additionalEventData") or {}).get("inferenceRegion", "")
        rows.append(
            {
                "event_time": detail.get("eventTime"),
                "aws_region": detail.get("awsRegion"),
                "model_id": (detail.get("requestParameters") or {}).get("modelId", ""),
                "inference_region": inference_region,
                "in_eu": in_eu(inference_region),
                "error_code": detail.get("errorCode", ""),
                "request_id": detail.get("requestID", ""),
            }
        )
    if not rows:
        sys.exit(
            "No InvokeModel events yet; CloudTrail can take up to 15 minutes. Try again later."
        )
    write_csv("trail.csv", rows)
    for row in rows:
        print(
            f"{row['event_time']} {row['model_id']} -> {row['inference_region'] or '?'}"
            f" (EU: {row['in_eu']}) {row['error_code']}"
        )


def in_eu(region):
    """yes or no for a Region that processed a call; empty when the call never reached a model."""
    if not region:
        return ""
    return "yes" if region in EU_MEMBER_STATE_REGIONS else "no"


def first_invocation():
    path = RESULTS / "invocations.csv"
    if not path.exists():
        sys.exit("Run `invoke` first, or pass --since.")
    with path.open(encoding="utf-8") as f:
        started = min(row["started_at"] for row in csv.DictReader(f))
    begin = dt.datetime.fromisoformat(started) - dt.timedelta(minutes=5)
    return begin.isoformat(timespec="seconds")


def now():
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("profiles", help="EU profile Regions and model access state (free)")
    sub.add_parser("quotas", help="Claude tokens-per-minute quotas, applied vs AWS default (free)")
    invoke = sub.add_parser("invoke", help="invoke both models through the EU profile (paid)")
    invoke.add_argument("--calls", type=int, default=5, help=f"calls per model, 1 to {MAX_CALLS}")
    probe = sub.add_parser("probe", help="one call per given model or profile ID (paid if allowed)")
    probe.add_argument("model_ids", nargs="+", help="for example eu.anthropic.claude-sonnet-5")
    probe.add_argument("--no-effort", action="store_true", help="for models without effort (4.5)")
    trail = sub.add_parser("trail", help="CloudTrail InvokeModel events (free)")
    trail.add_argument(
        "--since", help="ISO 8601 start time; defaults to 5 minutes before the first call"
    )
    args = parser.parse_args()
    {
        "profiles": cmd_profiles,
        "quotas": cmd_quotas,
        "invoke": cmd_invoke,
        "probe": cmd_probe,
        "trail": cmd_trail,
    }[args.command](args)


if __name__ == "__main__":
    main()
