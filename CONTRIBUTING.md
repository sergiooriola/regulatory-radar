# Contributing

How work gets into this repository. The rules apply to everyone, including the owner and any
coding agent working on his behalf.

## From issue to merge

1. **Every change starts with an issue** that says what is wanted and how it will be checked.
   Issues belong to the milestone of their project phase.
2. **One short-lived branch per issue**, created from an up-to-date `main` and named
   `<type>/<issue>-<slug>`, for example `docs/5-requirements` or `spike/2-boe-open-data`. The
   type is one of the commit types below.
3. **Small commits**, each one a single logical step that leaves the repository consistent.
4. **A pull request** whose title is a Conventional Commit and whose description says what
   changed, why, how it was checked and which issue it closes (`Closes #5`). Open it as a draft
   while the work is in progress.
5. **Checks pass and the owner reviews it.** Review comments are answered with new commits, not
   by rewriting the branch after review has started.
6. **Squash merge.** The pull request becomes one commit on `main`: its title is the pull
   request title, and its body lists the branch's commits. The branch is deleted on merge.

Nobody pushes to `main` directly; a ruleset enforces it.

## Commit messages

[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):
`<type>[optional scope]: <description>`, in English, imperative mood, lower case after the colon,
no full stop, about 72 characters at most. The body explains why, wrapped at 72 columns.

| Type | Use |
| --- | --- |
| `feat` | A new capability of the product |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `spike` | Throwaway feasibility code under `spikes/` |
| `test` | Tests only |
| `refactor` | Code change that neither fixes a bug nor adds a capability |
| `perf` | Performance improvement |
| `build` | Packaging, dependencies, container images |
| `ci` | Continuous integration |
| `chore` | Repository maintenance |
| `style` | Formatting only |
| `revert` | Reverts an earlier commit |

A breaking change adds `!` after the type or scope and a `BREAKING CHANGE:` footer.

Commits and pull requests carry no tool attribution lines (`Co-Authored-By` for a tool,
"Generated with ..."). The author is responsible for every line.

## Signed commits

Every commit on `main` must have a verified signature. Sign commits locally (SSH or GPG) and
upload the public key to GitHub as a signing key. Squash merges are signed by GitHub.

## Client data

Nothing that identifies a client goes in this repository: no names, addresses, domains, profiles,
maps, labelled samples or client documents. They live in the client's private repository
([ADR 0002](docs/adr/0002-keep-client-data-in-a-private-repository.md)). A CI check searches
every change for known client identifiers, which are stored as a repository secret so the list
itself is not published.

## Spikes

Spike code lives under `spikes/<id>/`, is throwaway and is never imported by the product. A
spike's threshold is fixed in [docs/spikes/README.md](docs/spikes/README.md) before it runs; its
pull request adds the report and does not change the threshold.

## Checks

| Check | What it enforces |
| --- | --- |
| Markdown lint | [markdownlint](https://github.com/DavidAnson/markdownlint) rules, configured in `.markdownlint-cli2.jsonc` |
| Pull request title | Conventional Commits format, since it becomes the commit on `main` |
| No client identifiers | No known client identifier in the tree |

Run the Markdown check locally with `npx markdownlint-cli2 "**/*.md"`.

## Dependencies of the workflows

Third-party actions are pinned to a full commit SHA, with the release tag as a comment.
Dependabot proposes updates weekly.
