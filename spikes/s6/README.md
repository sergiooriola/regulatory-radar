# Spike S6: AWS account and model access

Throwaway code for [spike S6](../../docs/spikes/README.md#s6-aws-account-and-model-access).
Nothing here is imported by anything else. The report is
[docs/spikes/s6-aws-account-and-model-access.md](../../docs/spikes/s6-aws-account-and-model-access.md).

| File | What it is |
| --- | --- |
| `s6.py` | The script (Python 3.14, standard library only, AWS CLI v2 for every AWS call); `python3.14 -I s6.py --help` |
| `results/` | What each command found, with AWS account IDs replaced by `<account>`; raw CLI output stays in `cache/`, which git ignores |

## How it runs

The script calls the AWS CLI with the `radar` profile, which signs in through IAM Identity
Center (`aws sso login --profile radar`), so the script never reads or stores a credential. It
uses the `bedrock-runtime` endpoint in `eu-south-2`, because the `bedrock-mantle` endpoint does
not support cross-Region inference profiles and the radar must keep processing in the EU
(requirement NFR-14).

1. `models` (free): every Anthropic model offered in the Region, its lifecycle state (Active or
   Legacy) and whether it has an `eu.` inference profile.
2. `profiles` (free): for each model of the pair, its lifecycle state, the Regions its `eu.`
   inference profile can route to, checked against a fixed list of Regions in EU member states,
   and the model's access state.
3. `invoke` (paid, a few cents at most): calls each model of the pair through its `eu.` profile
   with a one-line prompt and `max_tokens` 256 (low effort for the 5.5 pair; the 4.x pair runs
   without it, because Claude Haiku 4.5 rejects it), and records the stop reason and the token
   counts.
4. `probe` (paid if the call is allowed): one call to each model or profile ID given, to tell a
   block on the account from a block on one model. `--no-effort` drops the `effort` setting
   for models that reject it, such as Claude Haiku 4.5.
5. `quotas` (free): the applied tokens-per-minute quota of each Claude model, next to the AWS
   default.
6. `trail` (free): reads the `InvokeModel` events from CloudTrail event history, whose
   `additionalEventData.inferenceRegion` field says which Region processed each call.

`--pair` picks the models for `profiles` and `invoke`: `5.5` (the default) is the pair the spike
plan names, Claude Haiku 5.5 and Sonnet 5.5; `4.x` is the replacement from the
[plan change of 2026-11-05](../../docs/spikes/README.md#changes-to-the-plan), Claude Haiku 4.5
and Sonnet 4.6. Results for the `4.x` pair go to files ending in `-4.x.csv`.

The Region list leaves out `eu-central-2` (Zurich) and `eu-west-2` (London): they carry the
`eu-` prefix but are not in the European Union, and the proposal promises processing in the EU.
