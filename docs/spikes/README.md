# Feasibility spikes

A spike is a short, time-boxed experiment that answers one question the design depends on.
Each one states its pass threshold **before** it runs, so the result cannot bend the bar. Spike
code is throwaway and lives under `spikes/<id>/`; labelled data and anything about the client
stay in the private repository.

- **Status of this plan:** approved on 2026-10-19. The owner delegated the approval of the
  thresholds to the engineer writing this plan; any later change to a threshold is recorded
  here with its date and reason, before the spike it affects runs.
- **Last updated:** 2026-11-05, see [Changes to the plan](#changes-to-the-plan)

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
- **Changed on 2026-11-05:** the models, see [Changes to the plan](#changes-to-the-plan).

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
- **Threshold:** projected monthly cost at or below the ceiling agreed with the client: 15 USD a
  month, agreed on 2026-10-19, against an estimate of 2 to 8 USD made from list prices and the
  BOE volume of 13 to 17 October 2026.
- **Time box:** 1 day.

## Changes to the plan

### 2026-11-05: Claude Haiku 4.5 instead of Haiku 5.5

- **Why:** AWS refused to raise the radar account's tokens-per-minute quota for Claude Haiku 5.5
  and Sonnet 5.5 from 0 (S6). Its answer: access depends on the Region, payment history and
  usage, and may open as the account builds history. It gave no date.
- **Decision:** the owner chose on 2026-11-05 to go on with Claude Haiku 4.5, which works on
  the account through its EU profile, rather than wait.
- **Large model:** Claude Sonnet 4.6. It is Active in eu-south-2, has an EU profile and its
  default quota of 6 million tokens per minute on the account, and costs three times as much
  per token as Haiku 4.5. The other candidates do worse: Claude Sonnet 4.5 is Legacy since
  2026-10-08, with end of life on 2027-04-08, and new customers cannot use Legacy models
  ([model lifecycle](https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle-legacy.html));
  Opus 4.7 and 4.8 have a quota of 0; Opus 4.5 and 4.6 cost five times as much as Haiku 4.5.
- **Corrected the same day, before the check spent anything:** the first version of this entry
  said the price list had no Sonnet besides 5 and 5.5 and chose an Opus 4.x. The price list does
  list Sonnet 4.6, under a usage type the first reading missed ("Regional CRIS"), and the
  account's free checks (`s6.py models` and `quotas`) show it Active with its quota.
- **S6:** the threshold is not met for Claude Haiku 5.5 and Sonnet 5.5. Before S3 runs, the
  same method checks the replacement pair, with this threshold: both models Active in
  eu-south-2, both invoked through the EU profile, and every call processed in a Region of an
  EU member state according to CloudTrail.
- **S3 to S5:** Claude Haiku 4.5 is the small model and Claude Sonnet 4.6 the large one. The
  thresholds do not change. In S4 the large model costs three times as much per token as the
  small one, not twenty.
- **S7:** the ceiling does not change: 15 USD a month. The 2 to 8 USD estimate used 5.5 prices,
  and Claude Haiku 4.5 costs ten times as much per token as Haiku 5.5, so passing the ceiling
  is now likely (risk R07). S7 prices the measured tokens at 4.5 prices and at 5.5 prices, and
  lists the levers the design can weigh: the price list has batch inference at half price and
  cached input at a tenth.
- **Spending on the client's account:** at 4.5 prices, S3 to S5 no longer cost cents. Each
  spike states its expected model spend before it runs, and one expected to spend more than
  1 USD waits for the owner's approval.
- **Watch:** once a month, read the 5.x quotas and the lifecycle state of the models in use
  (both free; risk R23). If the 5.5 quotas open, S4 runs again on Haiku 5.5 and Sonnet 5.5
  before the design fixes the model.

On-demand prices through the EU profile in eu-south-2, from the AWS Price List
(`AmazonBedrockFoundationModels`, the "Regional" usage types), and each model's lifecycle state
and applied cross-Region quota on the account, read on 2026-11-05:

| Model | Input, USD per million tokens | Output, USD per million tokens | Lifecycle | Quota, tokens per minute |
| --- | --- | --- | --- | --- |
| Claude Haiku 5.5 | 0.11 | 0.55 | Active | 0 |
| Claude Haiku 4.5 | 1.10 | 5.50 | Active | 5,000,000 |
| Claude Sonnet 5.5 | 2.20 | 11.00 | Active | 0 |
| Claude Sonnet 4.6 | 3.30 | 16.50 | Active | 6,000,000 |
| Claude Sonnet 4.5 | 3.30 | 16.50 | Legacy | 5,000,000 |
| Claude Opus 4.5 and 4.6 | 5.50 | 27.50 | Active | 2,000,000 and 3,000,000 |
| Claude Opus 4.7 and 4.8 | 5.50 | 27.50 | Active | 0 |

## Reports

Each spike gets a report in this folder, named `s<n>-<slug>.md`, with the question, the
threshold as fixed here, what was done, the result, and the decision that follows.

| Spike | Report | Result |
| --- | --- | --- |
| S1 | [s1-boe-open-data.md](s1-boe-open-data.md) | Passed on 2026-10-20 |
| S2 | [s2-bocm-access-and-reuse.md](s2-bocm-access-and-reuse.md) | Passed on 2026-10-20 on the engineer's checks; the owner's spot check of one summary PDF is pending |
| S6 | [s6-aws-account-and-model-access.md](s6-aws-account-and-model-access.md) | In progress: the EU profile keeps processing in the EU, but AWS refused on 2026-11-05 to raise the account's quota of 0 for Claude Haiku 5.5 and Sonnet 5.5; the check of the replacement models is next |
