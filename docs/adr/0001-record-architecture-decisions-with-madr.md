---
status: accepted
date: 2026-10-19
decision-makers: Sergio Oriola Díaz
---

# Record architecture decisions with MADR

## Context and Problem Statement

The radar will involve decisions that are expensive to reverse and that the owner must be able
to defend: the model, the cloud services, the orchestration library, the data store, what runs
on a schedule. A design document describes the system as it is; it does not keep why one option
won over another, nor what was given up. How should those decisions be recorded?

## Decision Drivers

* The discarded options and their trade-offs must be written down, not only the choice.
* Records must live next to the code, be reviewed in pull requests and stay readable in plain
  text.
* The format should be widely recognised, so a reviewer does not need it explained.

## Considered Options

* MADR 4.0.0
* The original ADR format by Michael Nygard (context, decision, status, consequences)
* No ADRs; decisions described inside the design document

## Decision Outcome

Chosen option: "MADR 4.0.0", because it is the only option with dedicated sections for the
considered options and their pros and cons, which is the part needed to defend a trade-off,
while staying plain Markdown.

### Consequences

* Good, because each decision can be reviewed, and later superseded, on its own.
* Good, because the template asks for the alternatives every time.
* Bad, because a full record takes longer to write than a paragraph; the minimal variant of the
  template is acceptable for small decisions.

## Pros and Cons of the Options

### MADR 4.0.0

* Good, because it has sections for decision drivers, considered options and their pros and
  cons.
* Good, because its metadata (status, date, decision-makers) supports superseding records.
* Neutral, because it is longer than Nygard's format.

### Nygard's format

* Good, because it is short and the best known.
* Bad, because it has no dedicated place for discarded options.

### Decisions inside the design document

* Good, because there is one document fewer.
* Bad, because the reasoning is rewritten or lost when the design changes.

## More Information

* MADR: <https://adr.github.io/madr/>
* Michael Nygard, "Documenting Architecture Decisions" (2011):
  <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
