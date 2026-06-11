# Incident Report Generator

Guards write their own accounts of the same security incident; this tool produces one
supervisor-ready report — a summary of what happened, a list of likely-missing details to
follow up on, and the points where the accounts conflict. The report exports to PDF.

The UI is a dashboard: it lists every incident, each opens to its saved report, and
**Add new incident** posts fresh guard accounts to the pipeline. The report is generated
once when the incident is created and stored — opening an incident reads the saved report
rather than re-running the analysis. A few sample incidents are seeded into an empty
database on first startup so the dashboard is not blank.

**Live demo:** https://incident-ui-328698967588.us-central1.run.app
(Open a seeded sample incident, or click **Add new incident** to enter your own.)

## Stack

- **Streamlit** UI (dashboard, always light theme) — calls the API only.
- **FastAPI** — three endpoints, the LangGraph analysis pipeline, and the PDF builder.
- **Postgres** — stores incidents, reports, and results.
- **OpenAI** — the LLM behind the pipeline.

## Run locally

1. Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
2. `docker compose up --build`
3. Open the UI at http://localhost:8501 (the API is at http://localhost:8000).

## The pipeline

A LangGraph graph in `api/pipeline.py` with four nodes:

1. `summarize` — writes the summary from the reports only.
2. `find_omissions` — flags standard incident dimensions that no report covered.
3. `detect_conflicts` — proposes candidate conflicts with exact quotes.
4. `verify_conflicts` — drops wording-only differences, keeps real contradictions.

`detect_conflicts` and `verify_conflicts` form a bounded loop (max two iterations): if
verification discards candidates, detection runs again told not to re-propose them.

## API

| Method | Path                  | Purpose                                            |
|--------|-----------------------|----------------------------------------------------|
| GET    | `/incidents`          | List incidents (id, title, created_at) for the dashboard |
| POST   | `/incidents`          | Store reports, run the pipeline, return the result |
| GET    | `/incidents/{id}`     | Return the incident, its reports, and its result   |
| GET    | `/incidents/{id}/pdf` | Return the three-section report as a PDF            |

## Deploy (GCP)

Two Cloud Run services (api, ui) plus Cloud SQL for Postgres, with the OpenAI key in
Secret Manager. Cloud Run scales to zero; stop the Cloud SQL instance when not demoing.

Current deployment (project `project-d481c97a-382d-4d71-9f4`, region `us-central1`):

- API: https://incident-api-328698967588.us-central1.run.app
- UI:  https://incident-ui-328698967588.us-central1.run.app
- Cloud SQL instance `incident-db`, database `incidents`
- Secret Manager: `openai-api-key`, `db-password`

## Continuous deployment (GitHub Actions)

`.github/workflows/deploy.yml` redeploys both services on every push to `main`. Wire it
up by adding these to the GitHub repository:

Repository **Variables**:

- `GCP_PROJECT` = `project-d481c97a-382d-4d71-9f4`
- `GCP_REGION` = `us-central1`
- `CLOUD_SQL_CONNECTION` = `project-d481c97a-382d-4d71-9f4:us-central1:incident-db`
- `DB_NAME` = `incidents`
- `DB_USER` = `postgres`

Repository **Secrets**:

- `GCP_SA_KEY` = JSON key of a service account with roles: Cloud Run Admin, Cloud Build
  Editor, Service Account User, Artifact Registry Writer, Secret Manager Secret Accessor.

The OpenAI key and DB password are read from Secret Manager (`openai-api-key`,
`db-password`) — they are never stored in GitHub.

## Operations

Stop Cloud SQL when not demoing (it does not scale to zero):

```
gcloud sql instances patch incident-db --activation-policy NEVER
```

Start it again before a demo:

```
gcloud sql instances patch incident-db --activation-policy ALWAYS
```
