# S6. AWS account and model access

- **Status:** in progress, blocked by an AWS quota. A support case asking AWS to raise it was
  opened on 2026-10-23.
- **Run on:** 2026-10-23
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

## Result so far

| Part of the question | Result | Verdict |
| --- | --- | --- |
| Account on the Paid plan with budget alerts | Done with the [setup runbook](../runbooks/aws-account-setup.md), 21 to 23 October 2026 | Done |
| Model access requested | Anthropic use-case form submitted on 2026-10-21 in eu-south-2 | Done |
| The EU profile keeps processing in the EU | Both profiles route only to six Regions in EU member states; the one call that ran was processed in eu-north-1 | Pass |
| Claude Haiku 5.5 and Sonnet 5.5 invoked through the EU profile | `AccessDeniedException`: the account's tokens-per-minute quota for both is 0 | Blocked |
| How the usage appears on the bill, and whether credits apply | Waiting for the bill (one call to Claude Haiku 4.5, about 0.00004 USD) | Pending |
| Time box of 1 day | The work itself took less than half a day; the quota waits on AWS | Exceeded if AWS takes longer |

**Decision so far:** none. The threshold names Claude Haiku 5.5 and Sonnet 5.5, and neither can
be invoked yet. The spike resumes when AWS answers the support case. If AWS refuses, the
fallback is a decision for the owner, not for this spike: see
[If the quota is not raised](#if-the-quota-is-not-raised).

## Sources

All were read on 2026-10-23.

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
- **Quotas.** The radar's account starts with a quota of 0 on the 5.x models. Any later account
  (a test or a second client) will need the same support case before it can run.

## If the quota is not raised

The threshold cannot be met without Claude Haiku 5.5 and Sonnet 5.5, and the cost estimate of 2
to 8 USD a month assumes Haiku 5.5 does most of the work. Claude Haiku 4.5 works on this account
today, but at 1 USD per million input tokens and 5 USD per million output tokens on Anthropic's
list it costs ten times as much per token as Haiku 5.5. Switching models would change the
threshold, the cost estimate and probably S7, so it needs the owner's decision and an entry in
the spike plan before anything runs on it.

## Deviations from the method

- **Fewer calls.** Five calls per model were planned. After the first denial, one probe per model
  replaced them, because more calls would only have repeated the same error.
- **Models outside the threshold.** Claude Sonnet 5 and Haiku 4.5 were probed to tell an
  account-wide block from a model-specific one. The Haiku 4.5 call accepted that model's AWS
  Marketplace offer from Anthropic.
