import os
from datetime import datetime

import httpx
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Incident Report Generator", layout="wide")

if "view" not in st.session_state:
    st.session_state.view = "list"
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "guard_count" not in st.session_state:
    st.session_state.guard_count = 2


def go_list():
    st.session_state.view = "list"
    st.session_state.selected_id = None


def go_detail(incident_id):
    st.session_state.view = "detail"
    st.session_state.selected_id = incident_id


def go_new():
    # Start the form fresh: reset the guard rows and clear any prior input.
    st.session_state.view = "new"
    st.session_state.guard_count = 2
    for key in [k for k in st.session_state if k.startswith(("gname_", "gbody_"))]:
        del st.session_state[key]
    st.session_state.pop("new_title", None)


def add_guard():
    st.session_state.guard_count += 1


def format_date(value):
    try:
        return datetime.fromisoformat(value).strftime("%b %d, %Y at %I:%M %p")
    except Exception:
        return value


def dashboard():
    left, right = st.columns([6, 1])
    with left:
        st.title("Incident Reports")
    with right:
        st.write("")
        st.button("➕ Add new incident", on_click=go_new, type="primary", use_container_width=True)

    st.caption(
        "Each incident bundles the guards' accounts and one supervisor-ready report: a "
        "summary, likely-missing details to follow up on, and where the accounts conflict."
    )

    try:
        response = httpx.get(f"{API_URL}/incidents", timeout=30)
        incidents = response.json() if response.status_code == 200 else []
    except Exception:
        incidents = []
        st.error("Could not reach the API.")

    if not incidents:
        st.info("No incidents yet. Click **Add new incident** to create one.")
        return

    for inc in incidents:
        with st.container(border=True):
            info, action = st.columns([5, 1])
            with info:
                st.subheader(inc["title"] or "Untitled incident")
                st.caption(f"Incident #{inc['incident_id']}  ·  Created {format_date(inc['created_at'])}")
            with action:
                st.write("")
                st.button(
                    "Open",
                    key=f"open_{inc['incident_id']}",
                    on_click=go_detail,
                    args=(inc["incident_id"],),
                    use_container_width=True,
                )


def detail():
    st.button("← Back to dashboard", on_click=go_list)
    incident_id = st.session_state.selected_id
    try:
        response = httpx.get(f"{API_URL}/incidents/{incident_id}", timeout=60)
    except Exception:
        st.error("Could not reach the API.")
        return
    if response.status_code != 200:
        st.error(f"Could not load incident #{incident_id}.")
        return

    data = response.json()
    st.title(data["title"] or "Untitled incident")

    try:
        pdf_response = httpx.get(f"{API_URL}/incidents/{incident_id}/pdf", timeout=60)
    except Exception:
        pdf_response = None
    if pdf_response is not None and pdf_response.status_code == 200:
        st.download_button(
            "⬇ Download report PDF",
            data=pdf_response.content,
            file_name=f"incident_{incident_id}.pdf",
            mime="application/pdf",
            type="primary",
        )
    else:
        st.error("Report PDF is not available yet.")

    st.subheader("Guard accounts")
    for report in data["reports"]:
        with st.expander(report["label"]):
            st.write(report["body"])


def new_incident():
    st.button("← Cancel", on_click=go_list)
    st.title("New incident")

    title = st.text_input("Incident title", key="new_title")

    st.subheader("Guard accounts")
    st.caption("Enter each guard's name and their account of the incident.")
    for i in range(st.session_state.guard_count):
        st.text_input("Guard name", key=f"gname_{i}", placeholder=f"e.g. Officer J. Smith")
        st.text_area("Account", key=f"gbody_{i}", height=180)
        st.divider()

    st.button("Add another guard", on_click=add_guard)

    if st.button("Generate report", type="primary"):
        reports = []
        incomplete = False
        for i in range(st.session_state.guard_count):
            name = st.session_state.get(f"gname_{i}", "").strip()
            body = st.session_state.get(f"gbody_{i}", "").strip()
            if not name and not body:
                continue
            if not name or not body:
                incomplete = True
                continue
            reports.append({"label": name, "body": body})

        if not title.strip():
            st.warning("Give the incident a title first.")
        elif incomplete:
            st.warning("Each guard account needs both a name and a written account.")
        elif not reports:
            st.warning("Add at least one guard account.")
        else:
            with st.spinner("Analyzing reports..."):
                try:
                    response = httpx.post(
                        f"{API_URL}/incidents",
                        json={"title": title.strip(), "reports": reports},
                        timeout=120,
                    )
                except Exception:
                    response = None
            if response is None or response.status_code != 200:
                st.error("Analysis failed.")
            else:
                go_detail(response.json()["incident_id"])
                st.rerun()


if st.session_state.view == "detail":
    detail()
elif st.session_state.view == "new":
    new_incident()
else:
    dashboard()
