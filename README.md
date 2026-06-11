# Incident Report Generator

Guards write their own accounts of the same security incident; this tool produces one
supervisor-ready report - a summary of what happened, a list of likely-missing details to
follow up on, and the points where the accounts conflict. The report exports to PDF.

The UI is a dashboard: it lists every incident, each opens to its guard accounts and a
**Download Report PDF** button, and **New incident** posts fresh guard accounts to the
pipeline. The report itself is delivered as the PDF - there is no on-screen rendering of
it. Analysis is generated once when the incident is created and stored; opening an incident
reuses the saved result rather than re-running the pipeline. A few sample incidents are
seeded into an empty database on first startup so the dashboard is not blank.

The PDF is a clean, black-and-white document rendered from HTML/CSS by **WeasyPrint**
(see `api/report_pdf.py`): a cover page with a table of contents, then the summary,
follow-ups, account discrepancies, and the raw officer reports, each on its own page. The only color is
in the missing-information section, where the six categories are color-coded. The API
Docker image installs the Pango/Cairo libraries and fonts WeasyPrint needs.

**Live demo:** https://incident-ui-328698967588.us-central1.run.app
(Open a seeded sample incident, or click **New incident** to enter your own.)

## Stack

- **Streamlit** UI (dashboard, always light theme) - calls the API only.
- **FastAPI** - the endpoints, the LangGraph analysis pipeline, and the WeasyPrint PDF builder.
- **Postgres** - stores incidents, reports, and results.
- **OpenAI** - the LLM behind the pipeline.

## Run locally

1. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
2. `docker compose up --build`
3. Open the UI at http://localhost:8501 (the API is at http://localhost:8000).

## The pipeline

A LangGraph graph in `api/pipeline.py` with four nodes:

1. `summarize` - writes the summary from the reports only.
2. `find_omissions` - flags which of the six fixed categories (below) no report covered.
3. `detect_conflicts` - proposes candidate conflicts with exact quotes.
4. `verify_conflicts` - drops wording-only differences, keeps real contradictions.

`detect_conflicts` and `verify_conflicts` form a bounded loop (max two iterations): if
verification discards candidates, detection runs again told not to re-propose them.

### Missing-information categories

`find_omissions` checks the reports against a fixed set of six categories, one per
question in the who/what/where/why/when/how convention. The report lists only the
categories that no report covered, each shown with its own muted color:

| Category | Label                          | Color     |
|----------|--------------------------------|-----------|
| who      | SUBJECT / PERSON DESCRIPTION    | `#B0564A` |
| what     | WHAT HAPPENED                   | `#C07A3E` |
| where    | LOCATION                        | `#9A8A3C` |
| why      | REASON / MOTIVE                 | `#4F7A5A` |
| when     | TIME OF INCIDENT                | `#4A6E92` |
| how      | RESPONSE & OUTCOME              | `#6E5A82` |

Witnesses fold into WHO. The category keys, labels, and colors are fixed in code
(`api/pipeline.py` and `api/report_pdf.py`), so the section is deterministic.

## API

| Method | Path                  | Purpose                                            |
|--------|-----------------------|----------------------------------------------------|
| GET    | `/incidents`          | List incidents (id, title, created_at) for the dashboard |
| POST   | `/incidents`          | Store reports, run the pipeline, return the result |
| GET    | `/incidents/{id}`     | Return the incident, its reports, and its result   |
| GET    | `/incidents/{id}/pdf` | Return the full report PDF (cover, summary, follow-ups, account discrepancies, officer reports) |

## Deploy (GCP)

Two Cloud Run services (api, ui) plus Cloud SQL for Postgres, with the OpenAI key in
Secret Manager. Cloud Run scales to zero; stop the Cloud SQL instance when not demoing.

Current deployment (project `project-d481c97a-382d-4d71-9f4`, region `us-central1`):

- API: https://incident-api-328698967588.us-central1.run.app
- UI:  https://incident-ui-328698967588.us-central1.run.app
- Cloud SQL instance `incident-db`, database `incidents`
- Secret Manager: `openai-api-key`, `db-password`

## Continuous deployment (GitHub Actions)

`.github/workflows/deploy.yml` redeploys both services on every push to `main`. Auth is
**keyless** via Workload Identity Federation - no service-account key is stored in GitHub
(the project disables SA-key creation by org policy). Wire it up by adding these to the
GitHub repository:

Repository **Variables**:

- `GCP_PROJECT` = `project-d481c97a-382d-4d71-9f4`
- `GCP_REGION` = `us-central1`
- `CLOUD_SQL_CONNECTION` = `project-d481c97a-382d-4d71-9f4:us-central1:incident-db`
- `DB_NAME` = `incidents`
- `DB_USER` = `postgres`
- `WIF_PROVIDER` = full resource name of the workload identity provider, e.g.
  `projects/328698967588/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
- `DEPLOY_SA` = deployer service account email
  (`github-cloud-run-deployer@project-d481c97a-382d-4d71-9f4.iam.gserviceaccount.com`),
  with roles: Cloud Run Admin, Cloud Build Editor, Service Account User, Artifact Registry
  Writer, Storage Admin, Cloud SQL Client.

No repository secrets are required. The workflow requests an OIDC token (`id-token: write`)
and federates into the deployer SA; the provider is scoped to this repo by an attribute
condition, and the SA grants `roles/iam.workloadIdentityUser` only to this repo's
principalSet. The OpenAI key and DB password are read from Secret Manager
(`openai-api-key`, `db-password`) - they are never stored in GitHub.

One-time WIF setup (already provisioned for this project):

```
gcloud iam workload-identity-pools create github-pool --location=global
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global --workload-identity-pool=github-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository=='Boaxes/Incident-Report-Generator'"
gcloud iam service-accounts add-iam-policy-binding "$DEPLOY_SA" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/328698967588/locations/global/workloadIdentityPools/github-pool/attribute.repository/Boaxes/Incident-Report-Generator"
```

## Operations

Stop Cloud SQL when not demoing (it does not scale to zero):

```
gcloud sql instances patch incident-db --activation-policy NEVER
```

Start it again before a demo:

```
gcloud sql instances patch incident-db --activation-policy ALWAYS
```
