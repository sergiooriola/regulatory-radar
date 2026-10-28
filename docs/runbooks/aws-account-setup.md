# Runbook: set up the client's AWS accounts

- **For:** the owner, who opens and administers the accounts on the client's behalf.
- **Related:** spike S6, risks R02, R03 and R07.
- **Sources read on:** 2026-10-20, and again on 2026-10-21 when the structure changed to an
  organization. Each step links to the AWS page it comes from; if the console differs from what
  is written here, the linked page wins and this runbook is corrected.

The accounts belong to the client and are paid by the client. Nothing here creates a resource
that costs money; the only spend before S6 is zero.

## Account structure

An AWS account is a container for resources with its own bill and its own security boundary. An
AWS Organizations organization groups several accounts under one **management account**, which
pays the single combined bill and manages users and policies; the others are **member
accounts**.

AWS recommends using the management account only for tasks that require it and keeping every
workload in member accounts: organization policies (SCPs) do not restrict the management
account, and separate accounts make the bill easier to read
([management account best practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices_mgmt-acct.html)).
The client may use AWS for more than the radar, so:

| Account | Name | Holds |
| --- | --- | --- |
| Management | `<client>-management` | The bill, IAM Identity Center, the organization, budgets. No workloads. |
| Member | `<client>-regulatory-radar-prod` | Everything the radar runs |
| Future members | `<client>-<purpose>-prod` | One account per future workload |

Names follow AWS's *organization-purpose-environment* convention
([sign-up](https://docs.aws.amazon.com/accounts/latest/reference/getting-started.html)) and can be
changed later
([update account name](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-update-acct-name.html)).
Member accounts cost nothing in themselves.

## What you need before starting

- **Two group email addresses on the client's domain**, one per account, each used for nothing
  else and read by more than one person. AWS recommends an address that forwards to a group so
  the client keeps access when people change jobs, and says the root user's address should not
  be used for other purposes
  ([sign-up](https://docs.aws.amazon.com/accounts/latest/reference/getting-started.html),
  [root user best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html#ru-bp-group)).
  Each AWS account needs its own address, because the address is the root user's sign-in name.
  On Google Workspace, a group in the Admin console works: no mailbox and no licence, and every
  message is copied to each member
  ([create a group](https://knowledge.workspace.google.com/admin/groups/create-a-group-in-your-organization)).
  Two settings are needed for AWS's mail to reach it, because AWS is outside the organization
  ([fix group settings](https://knowledge.workspace.google.com/admin/support/troubleshooting/fix-common-issues-with-group-settings)):
  in the Admin console, **Groups for Business > Sharing settings > Group owners can allow
  incoming email from outside the organization**; in Google Groups, the group's **Who can post**
  set to **Anyone on the web**. The Admin console's create-group page already shows an access
  table: tick **External** in the **Who can post** row there, and keep **Who can contact group
  owners** to owners, managers and members. Send a test message from an address outside the
  domain. In October 2026 the test reached the member's inbox but in Spam, so each member adds
  a Gmail filter on the group address with **Never send it to Spam**.
- **A company phone number** that can receive SMS and calls, for identity verification and
  account recovery.
- **The client's payment card.**
- **Two MFA devices** for the root user, held if possible by two different people, for example
  an authenticator app on the owner's phone and another on the client sponsor's phone. AWS
  recommends registering more than one
  ([MFA](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html#ru-bp-mfa)).
- **A password manager**, with a database that belongs to the client, not the owner's personal
  one, so it can be handed over. Do not store the MFA secret in the same database as the
  password: whoever opened it would hold both factors.
- About two hours, plus waiting time for activation and Region enablement.

## 1. Create the management account with "Sign up for AWS (advanced)"

AWS is rolling out a second, newer sign-up to a limited number of customers. It cannot use
opt-in Regions such as Europe (Spain), cannot use AWS Marketplace, through which Claude on
Amazon Bedrock is billed, and cannot choose the Region where content is stored
([compare sign-up options](https://docs.aws.amazon.com/accounts/latest/reference/sign-up-for-aws.html)).
There is no button that names either sign-up: the advanced one is the one whose first page
asks for **Root user email address** and **AWS account name**; the newer one asks you to sign in
with an existing login instead.

1. Open <https://signin.aws.amazon.com/signup?request_type=register>.
2. Root user email: the first group address. Account name: `<client>-management`.
3. Root password: generated by the password manager and saved there before it is pasted.
4. **Account plan: Paid.** Both plans get the same sign-up credits, which end anyway when step 5
   creates the organization (see step 9). The Free plan also blocks some AWS Marketplace offers,
   and the account closes when the plan ends
   ([plans](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html)).
   Community reports say Free-plan accounts are denied Anthropic models (risk R03).
5. Contact information: the client's legal representative as full name, the client's company
   name, the company phone and the client's address. Accepting the AWS Customer Agreement
   accepts it on the client's behalf.
6. Billing: the client's card. The bank may ask to authorise a small verification charge.
7. When this runbook was used, in October 2026, the console opened as soon as the card was
   verified: there was no phone check and no support plan page, and the welcome email ("Your
   account is ready") arrived minutes later. If the pages do appear, verify by SMS with the
   company phone and choose the **Basic** support plan, which is free.

## 2. Secure the root user

The root user can do everything, including closing the account. After this step it is used
only for the few tasks that require it
([root user tasks](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html#root-user-tasks)).

1. Account name (top right) > **Security credentials** > **Multi-Factor Authentication (MFA)** >
   **Assign MFA device**. Register both devices
   ([virtual MFA for root](https://docs.aws.amazon.com/IAM/latest/UserGuide/enable-virt-mfa-for-root.html),
   [FIDO key for root](https://docs.aws.amazon.com/IAM/latest/UserGuide/enable-fido-mfa-for-root.html)).
   Name each device after its holder, for example `root-<holder>-phone`.
2. Do not create access keys for the root user.
3. Record, in the client's private records and not here, the account ID, who holds the
   password, who holds each MFA device, and who can read the root email inbox and the phone.
   AWS recommends that no single person controls both the email inbox and the phone, because
   both can recover the root password
   ([recovery](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html#ru-bp-recovery)).

## 3. Enable the Europe (Spain) Region in the management account

`eu-south-2` is an opt-in Region: it is off until it is enabled, enabling it is free, and it can
take from a few minutes to several hours
([Regions](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-regions.html)).
IAM Identity Center will live there, and AWS requires the Region to be enabled in every account
whose access it manages
([Identity Center in opt-in Regions](https://docs.aws.amazon.com/singlesignon/latest/userguide/regions.html#manually-enabled-regions)).

1. Account name (top right) > **Account**.
2. Section **AWS Regions** > **Europe (Spain)** > **Enable** > **Enable region**.
3. Wait until its status is **Enabled** before step 5. In October 2026 it was already enabled
   right after sign-up: AWS suggests the opt-in Region of the contact address's country during
   sign-up.

## 4. Let IAM identities see billing

By default only the root user can open the Billing and Cost Management console
([setting up](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started-account-iam.html)).

1. Still as root: account name > **Account**.
2. Section **IAM User and Role Access to Billing Information** > **Edit** > **Activate IAM
   Access** > **Update**.

## 5. Create your everyday administrator in IAM Identity Center

AWS recommends identity federation through IAM Identity Center instead of long-lived IAM users:
you sign in with a username, password and MFA, and every session gets temporary credentials.
On a standalone account, enabling it creates the AWS Organizations organization, with this
account as its management account
([enable](https://docs.aws.amazon.com/singlesignon/latest/userguide/enable-identity-center.html)).
Creating the organization ends the account's Free Tier sign-up credits (step 9).
IAM Identity Center is offered at no extra charge
([FAQ](https://aws.amazon.com/iam/identity-center/faqs/)).

1. Switch the console to **Europe (Spain)**. The instance stores its users and settings in the
   Region where it is enabled and cannot be moved later without deleting it
   ([data storage](https://docs.aws.amazon.com/singlesignon/latest/userguide/regions.html)).
   Its emails (invitation, one-time codes) are sent through Europe (Paris).
2. Open the IAM Identity Center console > **Enable** > **Enable IAM Identity Center with AWS
   Organizations** > **Enable**. If asked for an instance configuration, choose
   **Single-Region instance**: the multi-Region option creates a KMS key, which costs money.
3. Follow the official tutorial
   ([administrative user](https://docs.aws.amazon.com/singlesignon/latest/userguide/get-started-assign-account-access-admin-user.html)):
   - User: one per person who administers the account, with the client email address that
     person works with and **Send an email to this user with password setup instructions**.
     The owner chose to name the user after the role (for example `it`) rather than after
     himself; that is fine while one person uses it, and anyone who joins later gets their own
     user so CloudTrail keeps showing who did what.
   - Group: `admins`, with you in it.
   - Assign the group to the management account with a new predefined permission set,
     **AdministratorAccess**, keeping the default one-hour session.
4. Accept the invitation email, set the password and register an MFA device at the first
   sign-in. The email comes from `no-reply@login.awsapps.com` and its link goes to
   `<region>.signin.aws`. The link carries a one-time token: whoever opens it first sets the
   password, so do not forward or paste it anywhere.
5. Save the **AWS access portal URL** from the email. Sign out of the root user. From now on you
   sign in through the portal.

## 6. Centralize root access before creating member accounts

AWS recommends removing root user credentials from member accounts; accounts created in an
organization after this feature is enabled have none by default, and the management account
can still perform the few root-only tasks on them or allow a password recovery when needed
([centralize root access](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-enable-root-access.html),
[root user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html#id_root-user-access-management)).

1. IAM console > **Root access management** > **Enable**. If it says **Root access management
   is disabled**, first enable trusted access for IAM in AWS Organizations, as the message
   explains.
2. Select **Root credentials management** and **Privileged root actions in member accounts**.
   No delegated administrator. **Enable**.
3. After step 7, check that the radar's account has no root credentials. If a member account
   was created before this step and has any, delete them with a privileged task
   ([perform a privileged task](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user-privileged-task.html)).

Member accounts still need their own group address: it receives AWS's notices for that
account, and a password recovery, if one is ever allowed, goes to it.

## 7. Create the radar's member account

Signed in through the access portal to the management account
([create a member account](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_accounts_create.html)):

1. AWS Organizations console > **AWS accounts** > **Add an AWS account** > **Create an AWS
   account**.
2. **AWS account name:** `<client>-regulatory-radar-prod`. **Email address of the account's
   owner:** the second group address. Leave the IAM role name empty, so it gets the default
   `OrganizationAccountAccessRole`, which AWS recommends keeping the same in every account.
3. **Create AWS account**. If the organization is still initialising, wait an hour and retry.
   The member account copies the management account's phone, company name and address.

## 8. Enable Europe (Spain) in the member account and give yourself access

1. AWS Organizations console > **AWS accounts** > the radar's account > **Account settings** >
   **Regions** > **Europe (Spain)** > **Actions** > **Enable** > **Enable region**. If the tab
   asks for it, first enable trusted access for **AWS Account Management** in AWS Organizations
   ([Regions in an organization](https://docs.aws.amazon.com/accounts/latest/reference/manage-acct-regions.html#manage-acct-regions-enable-organization)).
   Repeat this for every future member account, or the access portal cannot reach it.
2. IAM Identity Center > **AWS accounts** > the radar's account > **Assign users or groups** >
   group `admins` > permission set **AdministratorAccess**.
3. Sign in through the access portal and check that both accounts appear.

## 9. Credits and budget alerts

**Credits.** Expect none. When this runbook was used, the 100 USD sign-up credit showed as
expired on the day it was issued, and AWS Support confirmed in October 2026 that creating an
organization ends all Free Tier credits and benefits. The published
[Free Tier Terms](https://aws.amazon.com/free/terms/) say so only for Free-plan accounts. Those
credits would not have paid for Claude anyway, which is billed as AWS Marketplace usage (spike
S6, risk R02). Any credit that arrives later belongs to the management account and reaches
member accounts only through credit sharing
([applying credits](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/useconsolidatedbilling-credits.html)).
In the management account: Billing and Cost Management > **Billing preferences** > **Credit
sharing preferences** > **Edit**, activate the radar's account and select **Default sharing for
newly created member accounts**. AWS builds the shared pool only from accounts that were in the
organization on the first day of the month.

**Budgets.** The ceiling agreed with the client is 15 USD a month. Alerts warn; they do not stop
spending (risk R07). Budgets without actions are free
([pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/)). Create two, in the
management account, following
[creating a cost budget](https://docs.aws.amazon.com/cost-management/latest/userguide/create-cost-budget.html):

| Name | Scope | Why |
| --- | --- | --- |
| `organization-monthly` | No filter | Any spend anywhere, including the management account, which should be close to zero |
| `regulatory-radar-monthly` | Filter **Linked account** = the radar's account | The radar against its own ceiling |

Create `organization-monthly` first and `regulatory-radar-monthly` the next day. The values of
the **Linked account** filter come from Cost Explorer, which AWS enables when Billing and Cost
Management is first opened and which has the current month's data about 24 hours later
([enabling Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-enable.html)).
Until then the list is empty and shows "Data is not available"; typing the account ID does not
help. The radar spends nothing before S6, so the day's wait leaves nothing uncovered.

For each one:

1. Billing and Cost Management > **Budgets** > **Create budget** > **Customize (advanced)** >
   **Cost budget** > **Next**. The simplified template cannot filter by account. Leave
   **Billing view** empty, so the budget uses the primary view, which covers the whole
   organization.
2. Period **Monthly**, **Recurring budget**, starting this month, budgeting method **Fixed**,
   amount **15** (USD).
3. Scope as in the table. Leave the cost aggregation at its default, unblended costs. Do not
   choose a "net" option: those subtract credits, and the alert must show what the radar really
   costs, so it stays useful when the credits run out.
4. Alerts, each as **% of budgeted amount**, sent to the first group address:
   - 50 % **Actual**
   - 80 % **Actual**
   - 100 % **Actual**
   - 100 % **Forecasted**
   Leave the Amazon SNS and chat alerts closed: email is enough.
5. No actions. **Create budget**.
6. Confirm the verification email AWS sends to the recipient
   ([email recipients](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-email-recipients.html)).
   It comes from AWS User Notifications, its link expires after 12 hours, and it only works
   while signed in to the management account.

**Cost Anomaly Detection.** Enabling Cost Explorer also sets up Cost Anomaly Detection, free,
with a monitor for AWS services and a daily email summary when unexpected spend exceeds 100 USD
and 40 % of what was expected ([enabling Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-enable.html)).
Keep it. At this project's scale that threshold never fires, so lower it once the radar has a
few weeks of normal spend to compare against; before then the budgets are the real guard.

## 10. Install the AWS CLI and sign in from the terminal

1. Install or update AWS CLI version 2
   ([install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)).
   On Linux the recommended method is now AWS's install script. It installs for the current
   user, without `sudo`, into `~/.local/share/aws-cli` with the command in `~/.local/bin`, and
   verifies the installer's PGP signature itself. It needs `unzip`, which some distributions
   lack (`sudo apt install unzip` on Ubuntu). To check the script before running it, download
   `install.sh` and `install.sh.sig` and verify them with `gpg` against the AWS CLI key from the
   install page, whose fingerprint is `FB5D B77F D5C1 18B8 0511 ADA8 A631 0ACC 4672 475C`.
2. Configure a profile for IAM Identity Center that points at the radar's account
   ([configure SSO](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)),
   either with the interactive `aws configure sso --profile radar` or by writing
   `~/.aws/config` directly. The result is the same; the file holds no secrets:

   ```ini
   [profile radar]
   sso_session = <client>
   sso_account_id = <radar account ID>
   sso_role_name = AdministratorAccess
   region = eu-south-2
   output = json

   [sso-session <client>]
   sso_start_url = <access portal URL from step 5>
   sso_region = eu-south-2
   sso_registration_scopes = sso:account:access
   ```

3. Sign in, in a terminal of your own, because the command waits for the browser:

   ```sh
   aws sso login --profile radar
   ```

   Sign in as your Identity Center user and allow the client named `botocore-client-...`,
   which is the CLI. Under WSL the CLI often cannot open the browser: open the URL it prints in
   the Windows browser. If the return to `localhost` fails, use `--use-device-code` and enter
   the code it shows.
4. Check it:

   ```sh
   aws sts get-caller-identity --profile radar
   ```

   The answer shows the radar's account ID and the **AdministratorAccess** role you chose.

No access keys are created at any point.

## 11. Prepare model access for Anthropic models in the radar's account

In commercial Regions there is no longer an access request page. Most models are enabled on
first use, but Anthropic models first need a one-time use-case form, and in opt-in Regions the
form must be filled in again even if it was submitted elsewhere
([model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)). Models
reached through the `bedrock-mantle` endpoint do not need the form; spike S6 decides which
endpoint the radar uses, so filling it in keeps both options open.

1. Signed in to the radar's account, in **Europe (Spain)**, open Amazon Bedrock > **Model
   catalog** > an Anthropic model, or the Anthropic providers page, and complete the use-case
   form: company name, the client's public website (check which domain actually serves it;
   it may differ from the email domain), intended users internal, industry, and the use case.
   The console takes at most 500 characters for the use case: say what the model reads
   (public official bulletins), what it does (classify and summarise), that no personal data
   is processed, and the volume. If you open the playground, do not send a prompt.
2. Read the submission back:

   ```sh
   aws bedrock get-use-case-for-model-access --profile radar --region eu-south-2 \
     --query formData --output text | base64 -d | base64 -d
   ```

   The CLI prints the stored form base64-encoded once more, hence the two decodes.
3. Do not invoke any model yet. Invoking it accepts the model's licence and starts billing;
   that happens in S6, with the budgets already in place. Until then,
   `aws bedrock get-foundation-model-availability` shows the agreement as `NOT_AVAILABLE`,
   which is expected: the per-model agreement is created on the first invocation. `PENDING`
   after that invocation means AWS is still setting it up and emails when it is done.

In Europe (Spain) the Anthropic models list only `INFERENCE_PROFILE` as their inference type:
they are reached through inference profiles, which route requests across several Regions. S6
checks that both models are invoked through the EU inference profile (requirement NFR-14).

## 12. Hand over to S6

Write in the client's private repository, as a living internal document rather than an
append-only record, the date, both account IDs, the access portal URL, who holds each
credential, the status of each step above and what is still pending. They are not secret, but
they identify the client, so they do not go in this repository. No passwords, MFA secrets or
invitation links go there either. Then tell the engineer running S6.
