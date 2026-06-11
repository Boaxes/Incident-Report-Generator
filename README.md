# Incident Report Generator

Guards write their own accounts of the same security incident; this tool produces one
supervisor-ready report — a summary of what happened, a list of likely-missing details to
follow up on, and the points where the accounts conflict. The report exports to PDF.

## Stack

- **Streamlit** UI (one page) — calls the API only.
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
| POST   | `/incidents`          | Store reports, run the pipeline, return the result |
| GET    | `/incidents/{id}`     | Return the incident, its reports, and its result   |
| GET    | `/incidents/{id}/pdf` | Return the three-section report as a PDF            |

## Deploy (GCP)

Two Cloud Run services (api, ui) plus Cloud SQL for Postgres, with the OpenAI key in
Secret Manager. Cloud Run scales to zero; stop the Cloud SQL instance when not demoing.
