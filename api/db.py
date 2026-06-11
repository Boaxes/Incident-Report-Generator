import os
import psycopg


def get_connection():
    instance = os.getenv("INSTANCE_CONNECTION_NAME")
    if instance:
        # Cloud SQL connects over a unix socket mounted by Cloud Run.
        host = f"/cloudsql/{instance}"
    else:
        host = os.getenv("DB_HOST", "localhost")
    return psycopg.connect(
        host=host,
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "incidents"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def init_db():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id serial PRIMARY KEY,
                title text,
                created_at timestamptz DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS reports (
                id serial PRIMARY KEY,
                incident_id int REFERENCES incidents(id),
                label text,
                body text
            );

            CREATE TABLE IF NOT EXISTS results (
                id serial PRIMARY KEY,
                incident_id int REFERENCES incidents(id),
                summary text,
                omissions jsonb,
                conflicts jsonb,
                created_at timestamptz DEFAULT now()
            );
            """
        )
        conn.commit()
