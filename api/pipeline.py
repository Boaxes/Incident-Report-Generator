import os
import json
from typing import TypedDict

from openai import OpenAI
from langgraph.graph import StateGraph, START, END

client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# The fixed dimensions a complete incident account should cover (spec section 3).
DIMENSIONS = [
    "subject / person description",
    "time of the incident",
    "location",
    "what happened (the action)",
    "actions the guards took",
    "outcome / how it ended",
    "witnesses",
]


class State(TypedDict):
    reports: list
    summary: str
    omissions: list
    candidates: list
    conflicts: list
    discarded: list
    iteration: int


def reports_block(reports):
    return "\n\n".join(f"[{r['label']}]\n{r['body']}" for r in reports)


def complete(system, user, json_mode=False):
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **kwargs,
    )
    return response.choices[0].message.content


def summarize(state: State) -> State:
    system = (
        "You write factual incident summaries for a security supervisor. Use ONLY "
        "information explicitly stated in the guard reports. Do not invent, infer, or "
        "add any detail that is not written in a report. Where the guards agree, state "
        "the fact plainly; where only some mention something, you may still include it. "
        "Write one or two short plain-language paragraphs. Do not list missing "
        "information or disagreements here."
    )
    user = f"Guard reports:\n\n{reports_block(state['reports'])}\n\nWrite the summary."
    try:
        summary = complete(system, user)
    except Exception as exc:
        summary = f"Summary unavailable ({exc})."
    return {"summary": summary}


def find_omissions(state: State) -> State:
    system = (
        "You check security incident reports for missing information. You are given a "
        "fixed list of dimensions a complete account should cover. Go through the "
        "dimensions one at a time and, for each, decide whether ANY report addresses it "
        "even partially. Flag a dimension ONLY if NONE of the reports addresses it at "
        "all; if even one report covers it, it is not missing. Be precise: a specific "
        "time of the incident, a location, or a description of the subject counts as "
        "covered only if a report actually states it. Respond with JSON of the form "
        '{"omissions": [{"dimension": "<one of the listed dimensions>", "note": '
        '"<short note on what is missing>"}]}. Return an empty list if every dimension '
        "is addressed by at least one report."
    )
    user = (
        "Dimensions:\n- " + "\n- ".join(DIMENSIONS) + "\n\n"
        f"Guard reports:\n\n{reports_block(state['reports'])}"
    )
    try:
        data = json.loads(complete(system, user, json_mode=True))
        omissions = data.get("omissions", [])
    except Exception:
        omissions = []
    return {"omissions": omissions}


def detect_conflicts(state: State) -> State:
    system = (
        "You find genuine factual conflicts between security incident reports. A "
        "conflict is where two reports state different, incompatible facts about the "
        "same thing (different times, different descriptions, different sequence of "
        "events). Quote each side exactly as written. Frame conflicts as points for the "
        "team to review, never as accusations of wrongdoing. Respond with JSON of the "
        'form {"conflicts": [{"topic": "<short topic>", "explanation": "<one line>", '
        '"claims": [{"label": "<report label>", "quote": "<exact quote>"}]}]}.'
    )
    avoid = ""
    if state.get("conflicts"):
        confirmed = "; ".join(c["topic"] for c in state["conflicts"])
        avoid += f"\n\nAlready confirmed (do NOT repeat these topics): {confirmed}."
    if state.get("discarded"):
        rejected = "; ".join(c["topic"] for c in state["discarded"])
        avoid += (
            f"\n\nPreviously rejected as wording-only (do NOT propose these again): "
            f"{rejected}."
        )
    user = f"Guard reports:\n\n{reports_block(state['reports'])}{avoid}"
    try:
        data = json.loads(complete(system, user, json_mode=True))
        candidates = data.get("conflicts", [])
    except Exception:
        candidates = []
    return {"candidates": candidates}


def verify_conflicts(state: State) -> State:
    candidates = state.get("candidates", [])
    if not candidates:
        return {"conflicts": state.get("conflicts", []), "discarded": state.get("discarded", [])}
    system = (
        "You verify proposed conflicts between incident reports. For each proposed "
        "conflict, decide whether the quotes describe genuinely incompatible facts, or "
        "are merely the same fact worded differently. Keep only real contradictions; "
        "discard wording-only differences. Respond with JSON of the form "
        '{"verified": [<the kept conflict objects, unchanged>], "discarded": [<the '
        "dropped conflict objects, unchanged>]}."
    )
    user = "Proposed conflicts:\n\n" + json.dumps({"conflicts": candidates}, indent=2)
    try:
        data = json.loads(complete(system, user, json_mode=True))
        newly_verified = data.get("verified", [])
        newly_discarded = data.get("discarded", [])
    except Exception:
        newly_verified = candidates
        newly_discarded = []
    conflicts = state.get("conflicts", []) + newly_verified
    discarded = state.get("discarded", []) + newly_discarded
    return {"conflicts": conflicts, "discarded": discarded, "_dropped_this_pass": len(newly_discarded)}


def should_loop(state: State) -> str:
    if state.get("_dropped_this_pass", 0) > 0 and state["iteration"] < 2:
        return "again"
    return "done"


def bump_iteration(state: State) -> State:
    return {"iteration": state["iteration"] + 1}


def build_graph():
    graph = StateGraph(State)
    graph.add_node("summarize", summarize)
    graph.add_node("find_omissions", find_omissions)
    graph.add_node("detect_conflicts", detect_conflicts)
    graph.add_node("verify_conflicts", verify_conflicts)
    graph.add_node("bump_iteration", bump_iteration)

    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", "find_omissions")
    graph.add_edge("find_omissions", "detect_conflicts")
    graph.add_edge("detect_conflicts", "verify_conflicts")
    graph.add_conditional_edges(
        "verify_conflicts", should_loop, {"again": "bump_iteration", "done": END}
    )
    graph.add_edge("bump_iteration", "detect_conflicts")
    return graph.compile()


_app = build_graph()


def run_pipeline(reports):
    state = {
        "reports": reports,
        "summary": "",
        "omissions": [],
        "candidates": [],
        "conflicts": [],
        "discarded": [],
        "iteration": 0,
    }
    final = _app.invoke(state)
    return {
        "summary": final["summary"],
        "omissions": final["omissions"],
        "conflicts": final["conflicts"],
    }
