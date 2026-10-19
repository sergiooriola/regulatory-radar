# Project plan

- **Owner:** Sergio Oriola Díaz
- **Phase:** 0, proposal
- **Last updated:** 2026-10-19

## Problem

The first client is a private school in the Comunidad de Madrid that follows a foreign
education system. Asked what costs most in dealing with regulation, the school answered:
keeping up with rules as they are published or repealed, "and above all, being clear about
which rules apply". Much of the regulation written for Spanish schools does not apply to a
foreign-system school, some of it does, and the boundary is not obvious.

The radar addresses that problem in three parts, described in the [README](../README.md): an
applicability map, a daily watch of the official bulletins and a weekly notice.

## Principles

- **No product code before the gate.** Feasibility spikes produce throwaway code under
  `spikes/`, which is not reused in the product.
- **Thresholds before results.** Every spike states its pass threshold before it runs
  ([spikes](spikes/README.md)).
- **Decisions are recorded with their alternatives** as ADRs in [MADR](adr/README.md) format.
- **Cost is designed, not discovered.** The design is reviewed against the cost pillar of the
  AWS Well-Architected Generative AI Lens (model right-sizing, fewer tokens, prompt caching,
  stop conditions for agents) before the gate.
- **Nothing about the client lives in this repository.** The client's profile, its map, the
  labelled samples and every client document are kept in a separate private repository
  ([ADR 0002](adr/0002-keep-client-data-in-a-private-repository.md)).

## Constraints

The owner builds the radar partly to demonstrate a specific set of tools: Python, Claude on
Amazon Bedrock in an EU region, LangChain and LangGraph, retrieval over the bulletin stream,
PostgreSQL, Terraform, an MCP server and a TypeScript review page. Each of these still gets an
ADR that weighs the alternatives and says when it would not be the right choice.

Kubernetes is learning scope, not part of the client's product: a local cluster for
development and CI, and an EKS cluster created with Terraform, demonstrated and destroyed within
hours in a separate sandbox account. A job that runs once a day does not justify a cluster that
runs all day; production uses pay-per-use services.

## Phases

Durations are indicative. The work is part-time with variable hours, so each phase's dates are
set when the previous phase closes.

| Phase | Question it answers | Exit criterion | Indicative duration |
| --- | --- | --- | --- |
| 0. Proposal | Is this worth doing, and on what terms? | The client accepts the proposal | 1 week |
| 1. Discovery | What exactly is the problem, for whom, and what counts as success? | Profile confirmed; success criteria and cost ceiling agreed | 1–2 weeks |
| 2. Feasibility | Can it be built to the bar, within the cost? | Every spike passes its threshold, or a decision is recorded | 2–3 weeks |
| 3. Design | How will it be built, run and paid for? | Design documents complete and self-reviewed | 1–2 weeks |
| Gate | Go or no-go | Independent audit, owner's go and the client's review of the draft map | 1 week |
| 4. Build | — | Acceptance tests pass | 6–10 weeks |
| 5. Pilot | Does it work in real use? | Four weeks of real notices; the client signs acceptance | 4 weeks |
| 6. Production and operation | — | Closure report delivered | Ongoing |
| 7. SaaS decision | Should it become a product for other organisations? | Decision recorded, on evidence from the pilot | Later |

## Deliverables

Client documents are written in Spanish, generated as Word and PDF from Markdown in the private
repository, and sent in the owner's name. Technical documents are written in English and live
here as Markdown, unless they contain client data.

| Phase | For the client (private repository) | Technical (this repository unless noted) |
| --- | --- | --- |
| 0. Proposal | Proposal and scope | Project plan, risk register |
| 1. Discovery | Discovery report | Requirements |
| 2. Feasibility | A short note only if a spike fails and changes the scope | One report per spike; labelled data stays private |
| 3. Design | Solution summary and running-cost budget | Architecture document, ADRs, data protection note, test plan, cost estimate |
| Gate | Regulatory map for review; go-ahead record | Independent audit |
| 4. Build | Short progress note per delivery | Changelog |
| 5. Pilot | Acceptance tests to sign; user guide | Test results |
| 6. Production | Closure report | Operations runbook |

The client's load is kept to three moments: accepting the proposal, reviewing the map once, and
signing acceptance. Everything else is available to read but never required.

## Roles

| Role | Who | Responsibility |
| --- | --- | --- |
| Owner and engineer | Sergio Oriola Díaz | Everything not listed below |
| Client sponsor | The school's CEO | Accepts the proposal, reviews the map, signs acceptance |
| Labour adviser | The school's external adviser | Questions about the collective agreement |
| Independent reviewer | A second AI model (Codex) | Audits the design and the spike reports at the gate |

## Status log

| Date | Event |
| --- | --- |
| 2026-10-19 | Project started. Proposal drafted; spike thresholds proposed. |
