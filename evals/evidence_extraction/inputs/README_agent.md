# AI Job Search Agent

Local portfolio/personal-tool backend for discovering job-alert opportunities, verifying public postings, deduplicating them, comparing job requirements with grounded candidate evidence, and persisting a human-review queue.

This package is an integrated update built from the uploaded `ai_job_search_agent.zip` as the source of truth. It keeps the existing job-discovery/resolution/matching architecture and adds the product-state contracts needed by the finalized UI.

## Product boundary

The V1 workflow stops at human review:

`job alerts -> verified public posting -> exact posting URL dedupe -> analysis -> persistence -> Pass / Save for later / Pursue`

There is no automatic resume customization or application flow in this package.

## UI-facing backend services

The UI should call high-level product actions rather than orchestrating pipeline internals itself.

### Agent run

```python
from job_agent.services.agent_run_service import run_agent

result = run_agent(
    email_source=my_email_source,
    progress_callback=on_progress,
)
```

`run_agent()` owns the execution order for metadata triage, body-on-demand retrieval, candidate extraction, posting resolution/verification, exact URL dedupe, analysis, persistence, and processed-email commit behavior.

Meaningful progress phases are exposed through `AgentRunProgress`:

- `FINDING_JOB_ALERTS`
- `VERIFYING_JOB_POSTINGS`
- `ANALYZING_OPPORTUNITIES`
- `SAVING_RESULTS`
- `COMPLETE`

The local UI now uses the built-in `GmailEmailSource`. `run_agent()` also retains the earlier `email_loader` / explicit `emails` inputs for tests and custom local diagnostics.

### UI service

`job_agent.services.ui_service` exposes the main UI-facing actions:

```python
list_needs_review()
list_reviewed()
get_opportunity_detail(opportunity_id)
set_user_decision(opportunity_id, decision)

get_background_state()
replace_resume(filename=..., content=...)
add_supporting_material(filename=..., content=...)

get_preferences()
save_preferences(preferences)

get_setup_completed()
mark_setup_completed()
finish_setup_and_run_agent(...)
```

## Durable product-state rules

### Opportunity analysis

A completed `JobOpportunity` analysis is created once and treated as a historical snapshot. Agent reruns only analyze NEW exact-posting-URL opportunities. Human decisions are independently mutable through `set_user_decision()` and do not rewrite analysis fields.

### Candidate background

- Resume is a singleton active source.
- Replacing Resume never physically deletes the previous Resume evidence.
- A new Resume is extracted and validated before the active Resume switch occurs.
- If replacement fails, the previous Resume remains active.
- Supporting Materials are append-only and remain active.
- Future matching uses only active managed sources.
- Historical Job Detail hydration can still load inactive old Resume evidence by durable `evidence_id`.
- Durable `E###` evidence IDs are never reused.

The uploaded database contains legacy source-less candidate evidence. It is preserved. Until a managed Resume is uploaded, it remains usable for compatibility; after the first managed active Resume exists, future matching excludes those source-less legacy rows while historical references remain resolvable.

### Onboarding state

`app_state.setup_completed` is the only onboarding-completion flag. There is no `first_run_completed` flag.

`finish_setup_and_run_agent()` commits `setup_completed = true` before starting the first Agent Run. If the run is interrupted afterward, onboarding is not repeated; the UI can return to Opportunities and offer `Run Agent` again.

### Preferences

V1 persists five optional categories only:

- Location
- Work Mode
- Industry
- Company Size
- Employment Type

Compensation is intentionally excluded from V1 UI/persistence. Per-opportunity preference results are historical snapshots and are not recomputed when settings later change.

### Job Detail evidence contract

The backend aggregate detail service returns the data the finalized UI needs:

`Requirement -> Support Level -> Match Reason -> Evidence Claim -> Source Document -> Original Source Text`

`source_section` and the internal `DIRECT / ADJACENT` evidence relationship are not exposed in the UI detail DTO. The relationship remains available internally to matching logic; the user-facing `Match Reason` should communicate direct support versus adjacent/gap support in natural language.

## Database migration

`initialize_database()` migrates the schema in place from the uploaded posting-URL schema. It adds:

- `candidate_sources`
- `candidate_evidence.source_id`
- `app_state`
- `candidate_preferences`
- `job_opportunities.job_attributes_json`
- `job_opportunities.created_at`
- `job_resolution_attempts` (required by the existing resolution repository)

The `evidence_matches -> candidate_evidence` foreign key is rebuilt with `ON DELETE RESTRICT` so a referenced historical evidence row cannot be accidentally deleted.

The package keeps the original `data/job_agent.db` unchanged. Migration occurs when `initialize_database()` first runs locally.

## Tests

Normal unit suite:

```bash
python -m pytest -q
```

The package includes `pytest.ini` with `testpaths = tests` so normal unit testing does not accidentally execute root-level live/network diagnostic scripts during collection.

At packaging time the unit suite passed:

`40 passed`

The migration was also tested against a copy of the database from the uploaded ZIP; existing candidate evidence, the existing opportunity, and historical evidence matches were preserved.

Live LLM/network tests were not executed in the packaging environment because it has no external network access and the `openai` package is not installed there. `job_agent.llm.client` now imports the OpenAI client lazily so non-live tests can run without that dependency; actual LLM calls still require the dependency and credentials in the user's local environment.

## One explicit sorting assumption

For Needs Review, the locked ordering is Priority -> Requirement Fit -> Preference Match -> newer `created_at`.

When two jobs reach the Preference Match tie-break with different configured denominators, this implementation compares the match rate (`matched / configured`). `0 / 0` receives no positive tie-break advantage. This denominator rule was the one remaining implementation-level detail that had not been explicitly locked in product discussion and can be changed independently if desired.

## Local UI

The finalized local UI is implemented in `app.py` with Streamlit. It uses the
high-level backend services described above; it does not call the internal
email / resolution / matching pipeline modules directly.

Python 3.11+ is required by the project (`StrEnum` and modern type syntax are
used throughout the codebase).

Install dependencies and start the app:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The UI implements:

- first-time onboarding: Resume -> Supporting Materials -> Preferences -> Ready
- persistent navigation: Opportunities / Background & Evidence / Preferences
- Needs Review and Reviewed opportunity lists
- Job Detail with Overview and Requirement Analysis tabs
- Pass / Save for later / Pursue decisions inside Job Detail only
- collapsed requirement-level evidence with Evidence Claim, Source Document,
  and Original Source Text
- safe Resume replacement error behavior
- append-only Supporting Materials
- meaningful Agent Run phase updates without fake percentage progress

### Gmail connection

The local UI includes a real Gmail adapter using Google's installed-app OAuth
flow and the read-only Gmail scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```

One-time local setup:

1. Create or choose a Google Cloud project and enable the Gmail API.
2. Configure the OAuth consent screen for the Google account that will use this
   local tool.
3. Create an OAuth client with application type **Desktop app**.
4. Download the OAuth client JSON and save it locally as:

   `data/private/google_credentials.json`

5. Start the Streamlit app and select **Connect Gmail** during onboarding (or
   from the Gmail recovery banner for an already-configured local database).

After authorization, the user token is stored locally at:

`data/private/gmail_token.json`

Both the OAuth client file and user token live under `data/private/`, which is
ignored by Git. They are not stored in the application database and are never
sent to the LLM. Expired access tokens are refreshed automatically when a
refresh token remains valid; the UI asks the user to reconnect only when normal
refresh cannot recover access.

The product keeps exactly one active Gmail account at a time. During normal
daily use no Gmail-connected indicator is shown. A low-frequency overflow menu
next to **Run Agent** exposes **Change Gmail account**; the replacement OAuth
flow preserves the old token until the new account has successfully authorized
and its Gmail identity has been verified. Existing opportunities, preferences,
and background evidence are unchanged; only future Agent Runs use the new
inbox.

Processed-email dedupe is scoped by `account_key + message_id`, so changing to a
different Gmail account cannot cause one inbox's message IDs to suppress another
inbox. Existing pre-account-aware processed-email markers are retained under a
legacy account key during automatic database migration.

If authorization is missing, revoked, or otherwise unusable, Opportunities
shows an inline recovery banner and disables **Run Agent** until Gmail is
connected again.

The Gmail ingestion boundary is metadata-first:

```text
Gmail messages.list (bounded recent window)
-> messages.get(format=metadata)
-> Qwen job-related classification
-> messages.get(format=full) only for related messages
-> body + extracted HTML links
-> Qwen JobCandidate extraction
```

By default the adapter looks back 14 days and inspects at most 200 messages.
These limits can be changed locally without code changes:

```bash
export JOB_AGENT_GMAIL_LOOKBACK_DAYS=14
export JOB_AGENT_GMAIL_MAX_MESSAGES=200
```

Optional path overrides are also supported:

```bash
export JOB_AGENT_GMAIL_CREDENTIALS_PATH="/path/to/google_credentials.json"
export JOB_AGENT_GMAIL_TOKEN_PATH="/path/to/gmail_token.json"
```

The older `JOB_AGENT_EMAIL_LOADER="module:function"` mechanism remains in the
codebase only as a compatibility hook for custom local adapters/tests; the
Streamlit product UI uses `GmailEmailSource` directly.

`EmailSource.account_key()` is part of the provider-neutral ingestion contract.
Gmail uses a normalized `gmail:<email-address>` key; legacy diagnostic loaders
use `legacy:default`.
