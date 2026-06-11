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
    st.session_state.pop("confirm_delete", None)


def go_detail(incident_id):
    st.session_state.view = "detail"
    st.session_state.selected_id = incident_id
    st.session_state.pop("confirm_delete", None)


def go_new():
    # Start the form fresh: reset the guard rows and clear any prior input.
    st.session_state.view = "new"
    st.session_state.guard_count = 2
    for key in [k for k in st.session_state if k.startswith(("gname_", "gbody_"))]:
        del st.session_state[key]
    st.session_state.pop("new_title", None)


def add_guard():
    st.session_state.guard_count += 1


def ask_delete(incident_id):
    st.session_state.confirm_delete = incident_id


def cancel_delete():
    st.session_state.pop("confirm_delete", None)


def delete_incident(incident_id):
    try:
        httpx.delete(f"{API_URL}/incidents/{incident_id}", timeout=30)
    except Exception:
        st.session_state.delete_error = True
        return
    # Drop cached detail/PDF for the removed incident and return to the list.
    fetch_incident.clear()
    fetch_pdf.clear()
    st.session_state.pop("confirm_delete", None)
    if st.session_state.get("selected_id") == incident_id:
        go_list()


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
        st.button("New incident", on_click=go_new, type="primary", use_container_width=True)

    try:
        response = httpx.get(f"{API_URL}/incidents", timeout=30)
        incidents = response.json() if response.status_code == 200 else []
    except Exception:
        incidents = []
        st.error("Could not reach the API.")

    if not incidents:
        st.info("No incidents yet. Click **New incident** to create one.")
        return

    # The list is newest-first, so number them so the oldest reads as #1.
    total = len(incidents)
    for i, inc in enumerate(incidents):
        seq = total - i
        with st.container(border=True):
            info, action = st.columns([5, 1])
            with info:
                st.subheader(inc["title"] or "Untitled incident")
                st.caption(f"Incident #{seq}  ·  Created {format_date(inc['created_at'])}")
            with action:
                st.write("")
                st.button(
                    "Open",
                    key=f"open_{inc['incident_id']}",
                    on_click=go_detail,
                    args=(inc["incident_id"],),
                    use_container_width=True,
                )


@st.cache_data(ttl=300, show_spinner=False)
def fetch_incident(incident_id):
    response = httpx.get(f"{API_URL}/incidents/{incident_id}", timeout=60)
    if response.status_code != 200:
        return None
    return response.json()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_pdf(incident_id):
    response = httpx.get(f"{API_URL}/incidents/{incident_id}/pdf", timeout=60)
    if response.status_code != 200:
        return None
    return response.content


def detail():
    st.button("← Back to dashboard", on_click=go_list)
    incident_id = st.session_state.selected_id

    with st.spinner("Loading incident..."):
        try:
            data = fetch_incident(incident_id)
        except Exception:
            st.error("Could not reach the API.")
            return
        if data is None:
            st.error(f"Could not load incident #{incident_id}.")
            return
        try:
            pdf_bytes = fetch_pdf(incident_id)
        except Exception:
            pdf_bytes = None

    st.title(data["title"] or "Untitled incident")

    st.subheader("Guard accounts")
    for report in data["reports"]:
        with st.expander(report["label"]):
            st.write(report["body"])

    if pdf_bytes is not None:
        st.download_button(
            "Download Report PDF",
            data=pdf_bytes,
            file_name=f"incident_{incident_id}.pdf",
            mime="application/pdf",
            type="primary",
        )
    else:
        st.error("Report PDF is not available yet.")

    st.divider()
    if st.session_state.get("confirm_delete") == incident_id:
        st.warning("Delete this incident permanently? This cannot be undone.")
        c1, c2, _ = st.columns([1, 1, 4])
        c1.button(
            "Confirm delete",
            on_click=delete_incident,
            args=(incident_id,),
            type="primary",
            use_container_width=True,
        )
        c2.button("Cancel", on_click=cancel_delete, use_container_width=True)
    else:
        st.button("Delete incident", on_click=ask_delete, args=(incident_id,))


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
