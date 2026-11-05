# S6. AWS account and model access

- **Status:** closed on 2026-11-05. Threshold not met: AWS refused to raise the account's quota
  of 0 for Claude Haiku 5.5 and Sonnet 5.5. The replacement pair from the
  [plan change of 2026-11-05](README.md#changes-to-the-plan), Claude Haiku 4.5 and Sonnet 4.6,
  passed the threshold set for it.
- **Run on:** 2026-10-23, and 2026-11-05 for the replacement pair
- **Code and data:** [spikes/s6/](../../spikes/s6/README.md)

## Question

Can a new AWS account invoke Claude Haiku 5.5 and Claude Sonnet 5.5 through Amazon Bedrock in
eu-south-2 with processing kept in the EU, and do the account's credits cover that usage?

## Threshold, as fixed

Quoted from [the spike plan](README.md#s6-aws-account-and-model-access), approved on 2026-10-19:

- **Method:** Open the account on the Paid plan with budget alerts, request model access,
  invoke both models through the EU inference profile, and read how the usage appears on the
  bill.
- **Threshold:** both models invoked through the EU profile. Whether credits apply is recorded
  as a fact either way and feeds S7 (risk R02).
- **Time box:** 1 day, plus up to 48 hours for the usage to appear on the bill.

Added by the [plan change of 2026-11-05](README.md#changes-to-the-plan), before the check ran:
for the replacement pair, Claude Haiku 4.5 and Sonnet 4.6, both models Active in eu-south-2,
both invoked through the EU profile, and every call processed in a Region of an EU member state
according to CloudTrail.

## Result

| Part of the question | Result | Verdict |
| --- | --- | --- |
| Account on the Paid plan with budget alerts | Done with the [setup runbook](../runbooks/aws-account-setup.md), 21 to 23 October 2026 | Done |
| Model access requested | Anthropic use-case form submitted on 2026-10-21 in eu-south-2 | Done |
| The EU profile keeps processing in the EU | The four profiles checked route only to six Regions in EU member states; all eleven calls that ran were processed in eu-north-1 | Pass |
| Claude Haiku 5.5 and Sonnet 5.5 invoked through the EU profile | `AccessDeniedException`: the account's tokens-per-minute quota for both is 0, and AWS refused on 2026-11-05 to raise it | Not met |
| Replacement pair, Claude Haiku 4.5 and Sonnet 4.6, Active and invoked through the EU profile | Both Active; 10 of 10 calls answered, all processed in eu-north-1 | Pass |
| How the usage appears on the bill, and whether credits apply | Claude is billed as AWS Marketplace usage sold by Anthropic, PBC. The only credit excluded Marketplace and ended when the organization was created | No credits apply |
| Time box of 1 day | The work took about a day in all; waiting for AWS took 13 days, from 2026-10-23 to 2026-11-05 | Exceeded |

**Decision:** the owner chose on 2026-11-05 to go on with Claude Haiku 4.5 as the small model;
the [plan change](README.md#changes-to-the-plan) records it, with Claude Sonnet 4.6 as the large
model. S3 to S5 run on that pair. S7 prices it, and also prices the 5.5 pair for when AWS opens
it; once a month the 5.x quotas and the models' lifecycle state are read again.

## Sources

All were read on 2026-10-23, except the credit terms, read on 2026-10-27, and the last two, read
on 2026-11-05.

| Source | URL |
| --- | --- |
| Request access to models (use-case form, automatic Marketplace subscription, `AccessDeniedException`) | <https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html> |
| Inference endpoints (`bedrock-runtime` and `bedrock-mantle`) | <https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html> |
| Inference using the Anthropic Messages API | <https://docs.aws.amazon.com/bedrock/latest/userguide/inference-messages-api.html> |
| Cross-Region inference | <https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html> |
| Geographic cross-Region inference | <https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html> |
| Model card, Claude Haiku 5.5 | <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-5-5.html> |
| Quotas for the `bedrock-runtime` endpoint | <https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-runtime.html> |
| AWS Support case management | <https://docs.aws.amazon.com/awssupport/latest/user/case-management.html> |
| Claude in Amazon Bedrock (Anthropic) | <https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock> |
| AWS Promotional Credit Terms and Conditions | <https://aws.amazon.com/awscredits/> |
| AWS Free Tier Terms | <https://aws.amazon.com/free/terms/> |
| Model lifecycle for models launched before 2026-09-07 (Legacy and end of life) | <https://docs.aws.amazon.com/bedrock/latest/userguide/model-lifecycle-legacy.html> |
| AWS Price List, offer `AmazonBedrockFoundationModels`, eu-south-2 | <https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/current/region_index.json> |

## What was done

Every AWS call went through [spikes/s6/s6.py](../../spikes/s6/s6.py), which runs the AWS CLI
2.38.3 with an IAM Identity Center profile on the radar's account. Account IDs are removed from
everything it writes to `results/`.

1. **Endpoint.** Bedrock serves Claude on two endpoints. AWS recommends `bedrock-runtime` for
   new applications, and only `bedrock-runtime` supports cross-Region inference profiles,
   geographic or global (endpoints page, "Inference capabilities"). Anthropic's page recommends
   its `AnthropicBedrockMantle` client, which targets `bedrock-mantle`. Requirement NFR-14 asks
   for processing in the EU, and in eu-south-2 the Claude models are reached only through
   inference profiles, so the spike used `bedrock-runtime` with `InvokeModel`. Which client the
   radar uses is for the design to decide.
2. **Profiles** (`s6.py profiles`, free). `GetInferenceProfile` for
   `eu.anthropic.claude-haiku-5-5` and `eu.anthropic.claude-sonnet-5-5` from eu-south-2.
3. **Invocation** (`s6.py invoke`, then `s6.py probe`). A one-line prompt, `max_tokens` 256, low
   effort. The first call to Claude Haiku 5.5 was denied, so the remaining calls were replaced
   by one probe per model to find out whether the block was on the account or on the model.
4. **Quotas** (`s6.py quotas`, free). The applied value of each Claude tokens-per-minute quota,
   next to the AWS default.
5. **CloudTrail** (`s6.py trail`, free). The `InvokeModel` events from CloudTrail event history,
   whose `additionalEventData.inferenceRegion` field names the Region that processed each call.
6. **Replacement pair, on 2026-11-05.** After AWS refused the quota, `s6.py models` (free) listed
   every Anthropic model in eu-south-2 with its lifecycle state and EU profile, and `s6.py
   quotas` read the quota of every Claude 4.x and 5.x model. Once the plan change named Claude
   Haiku 4.5 and Sonnet 4.6, `s6.py --pair 4.x profiles` and `--pair 4.x invoke --calls 5` ran
   steps 2 and 3 on them, without the `effort` setting, which Haiku 4.5 rejects, and `s6.py
   trail` read where every call ran.

## Results in detail

### The EU profiles stay in the EU

Both profiles, called from eu-south-2, list the same six destination Regions, which match the
"Geo: EU" table on the model card:

| Region | Country |
| --- | --- |
| eu-central-1 | Germany |
| eu-north-1 | Sweden |
| eu-south-1 | Italy |
| eu-south-2 | Spain |
| eu-west-1 | Ireland |
| eu-west-3 | France |

`eu-central-2` (Zurich) and `eu-west-2` (London) carry the `eu-` prefix but are not in the
European Union. They are not among the destinations for eu-south-2 as the source Region.
According to the model card, a call that starts in Zurich or London can be routed there. The
radar calls from eu-south-2, so neither applies, but the design must not change the source
Region without checking this again.

### The 5.x models are blocked by a quota of 0

| Model, through the EU profile | Outcome |
| --- | --- |
| Claude Haiku 5.5 | `AccessDeniedException`: "is not available for this account" |
| Claude Sonnet 5.5 | `AccessDeniedException`, same message |
| Claude Sonnet 5 | `AccessDeniedException`, same message |
| Claude Haiku 4.5 | Answered "ok", 14 input and 4 output tokens |

`GetFoundationModelAvailability` reports every one of them as `AUTHORIZED`, with entitlement and
Region `AVAILABLE`, so the use-case form and the Region are not the problem. The quotas explain
it:

| Cross-Region tokens per minute, eu-south-2 | AWS default | This account |
| --- | --- | --- |
| Claude Haiku 5.5 | 10,000,000 | 0 |
| Claude Sonnet 5.5 | 6,000,000 | 0 |
| Claude Sonnet 5 | 6,000,000 | 0 |
| Claude Opus 5 and 5.5 | 30,000,000 | 0 |
| Claude Haiku 4.5 | 5,000,000 | 5,000,000 |

The global profiles show the same pattern. AWS's model card says quotas "might change depending
on regional factors, payment history, or approval of a quota increase request". This is risk R03
coming true in a different form from the one recorded: not a refusal of Anthropic models, but no
capacity on the newest ones for a new account.

Service Quotas rejected requests for 500,000 and 200,000 tokens per minute: "You must provide a
quota value greater than the default quota value". A Service limit increase case, available on
the free Basic support plan, was opened from the radar's account on 2026-10-23 asking for those
two values on the EU profile. AWS's quota page warns that "priority will be given to customers
who generate traffic that consumes their existing quota allocation", which a quota of 0 cannot
do.

The case was still unassigned a week later, and a follow-up was added on 2026-10-30. On
2026-11-05 AWS Support answered that access to Claude Haiku 5.5 and Sonnet 5.5 "depends on
regional factors, payment history, and account usage", that it was "unable to approve your
request at this time", and that "accessibility is subject to change automatically as time
passes as your account builds its own history". It suggested Claude Haiku 4.5. The quotas read
again that day had not changed, and Opus 4.7 and 4.8 also had a quota of 0.

### Where the one successful call ran

CloudTrail recorded four `InvokeModel` events for Claude Haiku 4.5, all with eu-south-2 as the
source Region:

| Time (UTC) | Outcome | Processed in |
| --- | --- | --- |
| 08:03:11 | `ValidationException` (the probe sent `effort`, which Haiku 4.5 does not support) | none |
| 08:03:57 | `ServiceUnavailableException` | none |
| 08:04:02 | `ServiceUnavailableException` | none |
| 08:04:08 | Success | eu-north-1 (Sweden) |

The two `ServiceUnavailableException` events are the AWS CLI retrying while the AWS Marketplace
subscription was being set up; the probe took 16 seconds in all. The first, invalid request was
enough to start the subscription: AWS emailed that the Anthropic offer for Claude Haiku 4.5 had
been accepted at 08:03 UTC. The denied calls to the 5.x models did not appear in event history.

### The replacement pair, 2026-11-05

`s6.py models` lists fourteen Claude models in eu-south-2. All are Active except Claude Sonnet 4.5,
which is Legacy, and all but Fable 5 and 5.1 have an EU profile
([models.csv](../../spikes/s6/results/models.csv)). The lifecycle states and the quotas that
decided the pair are in the table of the [plan change](README.md#changes-to-the-plan); the raw
figures are in [quotas.csv](../../spikes/s6/results/quotas.csv).

From eu-south-2, the EU profiles of Claude Haiku 4.5 and Sonnet 4.6 list the same six
destination Regions as the 5.5 pair, all in EU member states, and both models are Active
([profiles-4.x.csv](../../spikes/s6/results/profiles-4.x.csv)). Sonnet 4.6's AWS Marketplace
agreement was `NOT_AVAILABLE` before its first call, as expected.

All ten calls answered "ok" with `end_turn`, 14 input and 4 output tokens each, in about one
second ([invocations-4.x.csv](../../spikes/s6/results/invocations-4.x.csv)). Unlike Haiku 4.5's
first call on 2026-10-23, Sonnet 4.6's first call did not fail while its subscription was set
up. CloudTrail recorded all ten, from 16:50:18 to 16:50:27 UTC, each processed in eu-north-1
(Sweden), with no errors ([trail.csv](../../spikes/s6/results/trail.csv)). At the eu-south-2
prices the ten calls cost about 0.0008 USD.

### How Claude is billed, and the credits

The October bill, read in the console on 2026-10-27, does not list the Claude Haiku 4.5 call under
Amazon Bedrock. It lists it in a separate section, "Amazon Web Services, Inc. - Marketplace", as
"Claude Haiku 4.5 (Amazon Bedrock Edition)" sold by Anthropic, PBC, with the usage types
`EUS2-MP:EUS2_InputTokenCount-Units` and `EUS2-MP:EUS2_OutputTokenCount-Units`. The amount rounds
to 0.00 USD. The bill places the usage in Europe (Spain), the source Region, although CloudTrail
shows the call ran in eu-north-1.

The account received one credit, the 100 USD AWS Free Tier sign-up credit:

- **It would not have paid for Claude.** Its list of applicable products includes Amazon Bedrock
  but not AWS Marketplace, and the AWS Promotional Credit Terms exclude AWS Marketplace unless AWS
  authorises otherwise.
- **It no longer exists.** The console shows it expired on the day it was issued, 2026-10-21, with
  nothing used. Asked through a support case, AWS Support answered on 2026-10-28: "Upon creating
  an AWS Organization, Free Tier eligibility is automatically terminated. This applies to all Free
  Tier credits and benefits associated with your account." The organization was created that day,
  when IAM Identity Center was enabled (step 5 of the
  [setup runbook](../runbooks/aws-account-setup.md)). The published Free Tier Terms state this
  only for accounts on the Free plan, and this account was opened on the Paid plan.

No credits apply to the radar. The cost estimate already counted Claude at list price, so nothing
changes, and risk R02 is closed.

## What the design must know

- **Endpoint.** Only `bedrock-runtime` keeps processing in the EU, through `eu.` inference
  profiles. `bedrock-mantle`, the endpoint behind Anthropic's recommended client, does not
  support inference profiles.
- **Source Region.** Calls must start in eu-south-2 (or another source Region whose EU profile
  excludes Zurich and London).
- **Evidence of EU processing.** CloudTrail's `inferenceRegion` names the Region of each call,
  for free, which is enough to check NFR-14 in operation.
- **First call per model.** It starts an AWS Marketplace subscription, takes several seconds and
  may fail with `ServiceUnavailableException` while it is set up. Retries with backoff cover it.
- **Credits.** None apply. Claude is billed as AWS Marketplace usage, and the sign-up credit ended
  when the organization was created. Every estimate counts Claude at list price.
- **Models.** Claude Haiku 4.5 (`eu.anthropic.claude-haiku-4-5-20251001-v1:0`) and Sonnet 4.6
  (`eu.anthropic.claude-sonnet-4-6`) until AWS opens the 5.5 pair. Haiku 4.5 rejects the
  `effort` setting.
- **Quotas.** The radar's account has a quota of 0 on the 5.x models and on Opus 4.7 and 4.8,
  and AWS will not raise it for a new account; it may open as the account builds history. Any
  later account (a test or a second client) should expect the same.
- **Requests per minute.** Besides tokens, the account's cross-Region quota allows 50 requests a
  minute each to Haiku 4.5 and Sonnet 4.6. S3 sends about 2,000 items, so it must put several
  items in each request or pace the calls.
- **Model lifecycle.** Claude Sonnet 4.5 went Legacy on 2026-10-08, five weeks before this
  report, and new customers cannot use a Legacy model. The model ID belongs in configuration,
  and the lifecycle state is read once a month (risk R23).

## After the refusal

The threshold could not be met without Claude Haiku 5.5 and Sonnet 5.5, and the cost estimate of
2 to 8 USD a month assumed Haiku 5.5 does most of the work. In eu-south-2, through the EU
profile, Claude Haiku 4.5 costs 1.10 USD per million input tokens and 5.50 USD per million
output tokens, exactly ten times Haiku 5.5. Switching models changed the threshold, the cost
outlook and S7, so it took the owner's decision and the
[plan change of 2026-11-05](README.md#changes-to-the-plan), recorded before anything ran on the
new pair. Risk R07 (running cost over the ceiling) rose to high likelihood, and R23 (model end of
life) was added.

## Deviations from the method

- **Fewer calls.** Five calls per model were planned. After the first denial, one probe per model
  replaced them, because more calls would only have repeated the same error.
- **Models outside the threshold.** Claude Sonnet 5 and Haiku 4.5 were probed to tell an
  account-wide block from a model-specific one. The Haiku 4.5 call accepted that model's AWS
  Marketplace offer from Anthropic.
- **Replacement pair.** Not in the plan approved on 2026-10-19. The plan change of 2026-11-05
  added it, with its threshold, before any call to it ran. Its calls went without the `effort`
  setting, because Haiku 4.5 rejects it.
- **Time box.** One day was planned; the spike stayed open 13 days waiting for AWS.
