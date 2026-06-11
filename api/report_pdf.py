from html import escape

from weasyprint import HTML

# Black-and-white report. The whole document is one HTML string rendered by WeasyPrint;
# the styling lives in the STYLE block below. Color appears in exactly one place: the
# six who/what/where/why/when/how categories in the missing-information section.

# Category key -> (ALL-CAPS label, muted color). The pipeline returns the key.
CATEGORY_STYLE = {
    "who": ("SUBJECT / PERSON DESCRIPTION", "#B0564A"),
    "what": ("WHAT HAPPENED", "#C07A3E"),
    "where": ("LOCATION", "#9A8A3C"),
    "why": ("REASON / MOTIVE", "#4F7A5A"),
    "when": ("TIME OF INCIDENT", "#4A6E92"),
    "how": ("RESPONSE & OUTCOME", "#6E5A82"),
}


def omission_key(dimension):
    """Canonicalize a returned dimension to one of the six category keys, or None."""
    key = (dimension or "").strip().lower()
    if key in CATEGORY_STYLE:
        return key
    for k, (label, _color) in CATEGORY_STYLE.items():
        if label.lower() == key:
            return k
    return None


STYLE = """
@page {
    size: A4;
    margin: 1.6cm 1.5cm 1.9cm 1.5cm;
    @bottom-left {
        content: "CONFIDENTIAL - For internal review";
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 8pt;
        color: #8a93a3;
    }
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: "Liberation Sans", Arial, sans-serif;
        font-size: 8pt;
        color: #8a93a3;
    }
}
/* The cover page carries no footer or page number. */
@page cover {
    @bottom-left { content: none; }
    @bottom-right { content: none; }
}

body {
    font-family: "Liberation Sans", Arial, sans-serif;
    color: #1f2733;
    font-size: 10.5pt;
    line-height: 1.5;
    margin: 0;
}

/* --- Cover page --- */
.cover {
    page: cover;
    page-break-after: always;
    padding-top: 5cm;
}
.cover .eyebrow {
    font-size: 9pt;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #6b7280;
    font-weight: 700;
    margin: 0 0 14px 0;
}
.cover h1 {
    font-size: 30pt;
    line-height: 1.15;
    margin: 0;
    font-weight: 700;
    color: #111111;
}
.cover .cover-meta {
    margin-top: 16px;
    font-size: 10pt;
    color: #4a5566;
}
.cover .cover-meta .dot { color: #9aa3b2; padding: 0 7px; }
.cover .rule {
    border: 0;
    border-top: 2px solid #111111;
    margin: 26px 0 30px 0;
}
.cover .toc-heading {
    font-size: 11pt;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #111111;
    font-weight: 700;
    margin: 0 0 12px 0;
}
ol.toc {
    list-style: decimal;
    padding-left: 22px;
    margin: 0;
    font-size: 11pt;
    color: #111111;
}
ol.toc li { margin-bottom: 10px; padding-left: 6px; }
ol.toc a {
    color: #111111;
    text-decoration: none;
}
ol.toc a::after {
    content: leader('.') target-counter(attr(href), page);
    color: #6b7280;
}
ol.toc-sub {
    list-style: none;
    padding-left: 16px;
    margin: 9px 0 2px 0;
    font-size: 10pt;
    color: #4a5566;
}
ol.toc-sub li { margin-bottom: 7px; padding-left: 0; }
ol.toc-sub a { color: #4a5566; }

/* --- Section headings --- */
h2.section {
    font-size: 11.5pt;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: #111111;
    font-weight: 700;
    margin: 0 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #111111;
}
section { break-inside: auto; }
.page-break { page-break-before: always; }

.summary p { margin: 0 0 10px 0; text-align: justify; }

/* --- Missing information (the only color in the document) --- */
ul.followups { list-style: none; margin: 0; padding: 0; }
ul.followups li {
    padding: 9px 12px 9px 14px;
    margin-bottom: 8px;
    background: #f6f6f6;
    border-left: 4px solid #555555;
    border-radius: 0 4px 4px 0;
}
ul.followups .dim {
    display: block;
    font-weight: 700;
    font-size: 9.5pt;
    letter-spacing: 0.6px;
}
ul.followups li.missing .dim { margin-bottom: 3px; }
ul.followups li.covered {
    background: #fafafa;
    padding-top: 7px;
    padding-bottom: 7px;
}
/* A covered category is left blank; de-emphasize it so the gaps stand out. */
ul.followups li.covered .dim { opacity: 0.5; }
ul.followups .note { display: block; color: #2a3342; }
.allgood { color: #4a5566; font-style: italic; }

/* --- Account discrepancies --- */
.conflict {
    border: 1px solid #cccccc;
    border-radius: 7px;
    margin-bottom: 16px;
    overflow: hidden;
    break-inside: avoid;
}
.conflict .topic {
    background: #222222;
    color: #ffffff;
    font-weight: 700;
    font-size: 10.5pt;
    padding: 9px 14px;
}
.conflict .body { padding: 12px 14px; }
.conflict .explanation { color: #43506a; margin: 0 0 10px 0; }
.claim {
    border-left: 3px solid #444444;
    background: #f6f6f6;
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
}
.claim:last-child { margin-bottom: 0; }
.claim .who { font-weight: 700; color: #111111; display: block; margin-bottom: 2px; }
.claim .quote { color: #2a3342; font-style: italic; }

/* --- Officer reports --- */
.report { margin-bottom: 22px; }
.report .label {
    font-weight: 700;
    font-size: 11pt;
    color: #111111;
    margin: 0 0 6px 0;
    padding-bottom: 4px;
    border-bottom: 1px solid #cccccc;
}
.report p { margin: 0 0 9px 0; text-align: justify; }
"""


def _paragraphs(text):
    return "".join(
        f"<p>{escape(p.strip())}</p>"
        for p in (text or "").split("\n")
        if p.strip()
    )


def build_pdf(title, summary, omissions, conflicts, incident_id=None, created_at=None,
              account_count=None, reports=None):
    meta_bits = []
    if incident_id is not None:
        meta_bits.append(f"Incident #{escape(str(incident_id))}")
    if created_at:
        meta_bits.append(escape(created_at))
    if account_count is not None:
        plural = "account" if account_count == 1 else "accounts"
        meta_bits.append(f"{account_count} {plural}")
    meta = '<span class="dot">&middot;</span>'.join(f"<span>{b}</span>" for b in meta_bits)

    summary_html = _paragraphs(summary) or "<p>No summary available.</p>"

    # Always show all six categories in fixed order; a category the reports covered is
    # left blank, a category nothing covered carries its follow-up note.
    notes_by_key = {}
    for item in omissions or []:
        k = omission_key(item.get("dimension", ""))
        if k and k not in notes_by_key:
            notes_by_key[k] = (item.get("note") or "").strip()
    rows = []
    for key, (label, color) in CATEGORY_STYLE.items():
        note = notes_by_key.get(key)
        if note:
            note_html = f'<span class="note">{escape(note)}</span>'
            row_cls = "followup missing"
        else:
            note_html = ""
            row_cls = "followup covered"
        rows.append(
            f'<li class="{row_cls}" style="border-left-color: {color};">'
            f'<span class="dim" style="color: {color};">{label}</span>'
            f'{note_html}</li>'
        )
    followups_html = '<ul class="followups">' + "".join(rows) + "</ul>"

    if conflicts:
        cards = []
        for conflict in conflicts:
            topic = escape(conflict.get("topic", ""))
            explanation = escape(conflict.get("explanation", ""))
            explanation_html = f'<p class="explanation">{explanation}</p>' if explanation else ""
            claims = "".join(
                f'<div class="claim"><span class="who">{escape(c.get("label", ""))}</span>'
                f'<span class="quote">&ldquo;{escape(c.get("quote", ""))}&rdquo;</span></div>'
                for c in conflict.get("claims", [])
            )
            cards.append(
                f'<div class="conflict"><div class="topic">{topic}</div>'
                f'<div class="body">{explanation_html}{claims}</div></div>'
            )
        conflicts_html = "".join(cards)
    else:
        conflicts_html = '<p class="allgood">No discrepancies were found between the accounts.</p>'

    # Each officer report gets a stable anchor and starts on its own page (except the first,
    # which shares the page with the section heading). The cover TOC sub-list reuses the
    # same labels and order.
    toc_reports = ""
    if reports:
        blocks = []
        toc_items = []
        for i, report in enumerate(reports):
            label = escape(report.get("label", "") or "Unnamed officer")
            body = _paragraphs(report.get("body", "")) or "<p>No account provided.</p>"
            cls = "report page-break" if i > 0 else "report"
            blocks.append(
                f'<div class="{cls}" id="report-{i}">'
                f'<p class="label">{label}</p>{body}</div>'
            )
            toc_items.append(f'<li><a href="#report-{i}">{label}</a></li>')
        reports_html = "".join(blocks)
        toc_reports = '<ol class="toc-sub">' + "".join(toc_items) + "</ol>"
    else:
        reports_html = '<p class="allgood">No officer reports are on file for this incident.</p>'

    document = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><style>{STYLE}</style></head>
<body>
    <div class="cover">
        <p class="eyebrow">Security Incident Report</p>
        <h1>{escape(title or "Incident Report")}</h1>
        <div class="cover-meta">{meta}</div>
        <hr class="rule">
        <p class="toc-heading">Contents</p>
        <ol class="toc">
            <li><a href="#summary">Summary</a></li>
            <li><a href="#followups">Follow-ups / Missing Information</a></li>
            <li><a href="#conflicts">Account Discrepancies</a></li>
            <li><a href="#reports">Officer Reports</a>{toc_reports}</li>
        </ol>
    </div>

    <section id="summary">
        <h2 class="section">Summary</h2>
        <div class="summary">{summary_html}</div>
    </section>

    <section id="followups" class="page-break">
        <h2 class="section">Follow-ups &middot; Missing Information</h2>
        {followups_html}
    </section>

    <section id="conflicts" class="page-break">
        <h2 class="section">Account Discrepancies</h2>
        {conflicts_html}
    </section>

    <section id="reports" class="page-break">
        <h2 class="section">Officer Reports</h2>
        {reports_html}
    </section>
</body>
</html>"""

    return HTML(string=document).write_pdf()
