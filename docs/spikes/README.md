# Feasibility spikes

A spike is a short, time-boxed experiment that answers one question the design depends on.
Each one states its pass threshold **before** it runs, so the result cannot bend the bar. Spike
code is throwaway and lives under `spikes/<id>/`; labelled data and anything about the client
stay in the private repository.

- **Status of this plan:** approved on 2026-10-19. The owner delegated the approval of the
  thresholds to the engineer writing this plan; any later change to a threshold is recorded
  here with its date and reason, before the spike it affects runs.
- **Last updated:** 2026-10-19

## Order

S6 goes first, because model access on a new AWS account can take time and every model spike
depends on it. S1 and S2 run alongside it. S3, S4 and S5 need S1 and S6. S7 uses the
measurements from S3 to S5.

## Spikes

### S1. BOE open data

- **Question:** Do the BOE open-data APIs return, for every publication day, every item with
  the metadata the radar needs, and do they expose which rules amend or repeal a given rule?
- **Method:** Fetch the daily summary (`/datosabiertos/api/boe/sumario/{yyyymmdd}`) for 60
  consecutive publication days. For ten amendment or repeal relations chosen and recorded before
  the run, query the consolidated-legislation API for the affected rule and check its
  references.
- **Threshold:** 60 of 60 days retrieved (retries allowed); every item has an identifier,
  title, section, department and a link to the official text; 10 of 10 relations found.
- **Time box:** 2 days.

### S2. BOCM access and reuse

- **Question:** Can the Comunidad de Madrid's official bulletin be read by a program every
  publication day, and do its terms allow automated reuse?
- **Method:** Look for an official machine-readable source first, then a stable HTML one.
  Retrieve 20 consecutive publication days and compare three of them by hand with the
  published summary. Read the reuse terms.
- **Threshold:** 20 of 20 days retrieved, the three hand checks match item for item, and the
  terms allow automated reuse. Otherwise BOCM is left out of the first version and every notice
  says so (risk R04).
- **Time box:** 2 days.

### S3. Triage recall

- **Question:** From an item's title, section and department alone, does a small model flag
  every item that affects or may affect the profile, while passing few enough on to make
  deeper analysis affordable?
- **Method:** All items from 10 publication days (about 2,000), plus past items known to be
  relevant (seeded, because ten days will contain few or none). The owner labels each one
  *affects*, *may affect* or *does not affect* before the model runs.
- **Threshold:** recall of 100 % on *affects* and at least 95 % on *may affect*; no more than
  10 % of all items passed on to deep analysis. Precision is reported, not gated.
- **Time box:** 3 days.

### S4. Deep analysis

- **Question:** For a flagged item, does the model give a correct classification with the
  article that makes it apply, the obligation and the deadline?
- **Method:** Run the analysis on the flagged items from S3 with their full text, first with
  Claude Haiku 5.5 and then with Claude Sonnet 5.5, which costs twenty times as much per token.
  Check every cited article against the text. The cheapest model, or combination (the small
  model analyses, the large one only reviews what the small one marks as doubtful), that passes
  the threshold is the one the design uses.
- **Threshold:** zero invented citations; no item labelled *affects* classified as *does not
  affect*; agreement with the owner's label on at least 90 % of items.
- **Time box:** 3 days.

### S5. Map discovery

- **Question:** From the profile alone, does the system find the rules that apply, citing the
  provision that makes each one apply?
- **Method:** Before the run, the owner builds a reference list of applicable rules from
  independent sources (official guidance, sector associations, the school's own documents).
  The system proposes its list; each citation is checked against the BOE consolidated text.
- **Threshold:** at least 90 % of the reference list found; zero invented citations. Rules the
  system finds that are not on the reference list are reviewed one by one and may enter it.
- **Time box:** 3 days.

### S6. AWS account and model access

- **Question:** Can a new AWS account invoke Claude Haiku 5.5 and Claude Sonnet 5.5 through
  Amazon Bedrock in eu-south-2 with processing kept in the EU, and do the account's credits
  cover that usage?
- **Method:** Open the account on the Paid plan with budget alerts, request model access,
  invoke both models through the EU inference profile, and read how the usage appears on the
  bill.
- **Threshold:** both models invoked through the EU profile. Whether credits apply is recorded
  as a fact either way and feeds S7 (risk R02).
- **Time box:** 1 day, plus up to 48 hours for the usage to appear on the bill.

### S7. Running cost

- **Question:** What does the radar cost per day and per month at the observed volume?
- **Method:** Use the token counts measured in S3 to S5 and the bulletin volume measured in S1,
  priced with the AWS Price List API for eu-south-2; add the infrastructure from the AWS
  Pricing Calculator.
- **Threshold:** projected monthly cost at or below the ceiling agreed with the client in
  discovery. The proposal suggests 15 USD a month, against an estimate of 2 to 8 USD made from
  list prices and the BOE volume of 13 to 17 October 2026.
- **Time box:** 1 day.

## Reports

Each spike gets a report in this folder, named `s<n>-<slug>.md`, with the question, the
threshold as fixed here, what was done, the result, and the decision that follows.
