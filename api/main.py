import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from psycopg.types.json import Json

from db import get_connection, init_db
from models import IncidentCreate, IncidentResult, IncidentDetail, IncidentSummary
from pipeline import run_pipeline
from report_pdf import build_pdf
from seed import SAMPLES


def store_incident(title, reports, result):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO incidents (title) VALUES (%s) RETURNING id", (title,)
        )
        incident_id = cur.fetchone()[0]
        for r in reports:
            cur.execute(
                "INSERT INTO reports (incident_id, label, body) VALUES (%s, %s, %s)",
                (incident_id, r["label"], r["body"]),
            )
        cur.execute(
            "INSERT INTO results (incident_id, summary, omissions, conflicts) "
            "VALUES (%s, %s, %s, %s)",
            (incident_id, result["summary"], Json(result["omissions"]), Json(result["conflicts"])),
        )
        conn.commit()
    return incident_id


def seed_samples():
    # Generate and store the sample incidents once, only if the database is empty.
    # Runs in a background thread so it never blocks the server from coming up.
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM incidents")
            if cur.fetchone()[0] > 0:
                return
    except Exception:
        return
    for sample in SAMPLES:
        try:
            result = run_pipeline(sample["reports"])
            store_incident(sample["title"], sample["reports"], result)
        except Exception:
            continue


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    threading.Thread(target=seed_samples, daemon=True).start()
    yield


app = FastAPI(title="Incident Report Generator", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/incidents", response_model=list[IncidentSummary])
def list_incidents():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, created_at FROM incidents ORDER BY created_at DESC, id DESC"
        )
        rows = cur.fetchall()
    return [
        IncidentSummary(incident_id=id, title=title, created_at=created_at.isoformat())
        for id, title, created_at in rows
    ]


@app.post("/incidents", response_model=IncidentResult)
def create_incident(incident: IncidentCreate):
    reports = [{"label": r.label, "body": r.body} for r in incident.reports]
    result = run_pipeline(reports)
    incident_id = store_incident(incident.title, reports, result)
    return IncidentResult(incident_id=incident_id, **result)


@app.get("/incidents/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT title FROM incidents WHERE id = %s", (incident_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        title = row[0]
        cur.execute(
            "SELECT label, body FROM reports WHERE incident_id = %s ORDER BY id",
            (incident_id,),
        )
        reports = [{"label": label, "body": body} for label, body in cur.fetchall()]
        cur.execute(
            "SELECT summary, omissions, conflicts FROM results WHERE incident_id = %s "
            "ORDER BY id DESC LIMIT 1",
            (incident_id,),
        )
        result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    summary, omissions, conflicts = result
    return IncidentDetail(
        incident_id=incident_id,
        title=title,
        reports=reports,
        summary=summary,
        omissions=omissions,
        conflicts=conflicts,
    )


@app.get("/incidents/{incident_id}/pdf")
def get_incident_pdf(incident_id: int):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT title, created_at FROM incidents WHERE id = %s", (incident_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        title, created_at = row
        cur.execute("SELECT count(*) FROM reports WHERE incident_id = %s", (incident_id,))
        account_count = cur.fetchone()[0]
        cur.execute(
            "SELECT summary, omissions, conflicts FROM results WHERE incident_id = %s "
            "ORDER BY id DESC LIMIT 1",
            (incident_id,),
        )
        result = cur.fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    summary, omissions, conflicts = result
    pdf_bytes = build_pdf(
        title,
        summary,
        omissions,
        conflicts,
        incident_id=incident_id,
        created_at=created_at.strftime("%b %d, %Y") if created_at else None,
        account_count=account_count,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="incident_{incident_id}.pdf"'},
    )
