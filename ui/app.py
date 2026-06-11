import os

import httpx
import streamlit as st

from samples import SAMPLES

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Incident Report Generator", layout="centered")
st.title("Incident Report Generator")
st.write(
    "Upload each guard's account of the same incident. The tool produces one "
    "supervisor-ready report: a summary, likely-missing details to follow up on, and the "
    "points where the accounts conflict."
)

sample_titles = ["- none -"] + [s["title"] for s in SAMPLES]
chosen_sample = st.selectbox("Try a sample incident", sample_titles)
sample = next((s for s in SAMPLES if s["title"] == chosen_sample), None)

if sample:
    st.caption("Sample reports loaded below. Just click Generate report.")
    for r in sample["reports"]:
        with st.expander(r["label"]):
            st.write(r["body"])

title = st.text_input("Incident title", value=sample["title"] if sample else "")
uploaded = st.file_uploader(
    "Or upload your own reports (.txt, one per guard)",
    type="txt",
    accept_multiple_files=True,
)

if st.button("Generate report"):
    if uploaded:
        reports = [
            {"label": f.name, "body": f.read().decode("utf-8", "replace")}
            for f in uploaded
        ]
    elif sample:
        reports = sample["reports"]
    else:
        reports = []

    if not title:
        st.warning("Give the incident a title first.")
    elif not reports:
        st.warning("Upload at least one report or pick a sample.")
    else:
        with st.spinner("Analyzing reports..."):
            response = httpx.post(
                f"{API_URL}/incidents",
                json={"title": title, "reports": reports},
                timeout=120,
            )
        if response.status_code != 200:
            st.error(f"Analysis failed ({response.status_code}).")
        else:
            st.session_state["result"] = response.json()

result = st.session_state.get("result")
if result:
    st.header("Summary")
    st.write(result["summary"])

    st.header("Follow-ups: likely missing information")
    if result["omissions"]:
        for item in result["omissions"]:
            note = item.get("note", "")
            st.markdown(f"- **{item.get('dimension', '')}**" + (f": {note}" if note else ""))
    else:
        st.write("The reports covered all of the standard incident details.")

    st.header("Conflicts")
    st.caption("These are points for the team to review, not findings of wrongdoing.")
    if result["conflicts"]:
        for conflict in result["conflicts"]:
            st.subheader(conflict.get("topic", ""))
            if conflict.get("explanation"):
                st.write(conflict["explanation"])
            for claim in conflict.get("claims", []):
                st.markdown(f'> **{claim.get("label", "")}:** "{claim.get("quote", "")}"')
    else:
        st.write("No genuine conflicts were found between the reports.")

    incident_id = result["incident_id"]
    pdf_response = httpx.get(f"{API_URL}/incidents/{incident_id}/pdf", timeout=60)
    if pdf_response.status_code == 200:
        st.download_button(
            "Download PDF",
            data=pdf_response.content,
            file_name=f"incident_{incident_id}.pdf",
            mime="application/pdf",
        )
