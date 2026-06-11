from html import escape

from weasyprint import HTML

# Corporate-banded navy report. The whole document is one HTML string rendered by
# WeasyPrint; the styling lives in the STYLE block below.

STYLE = """
@page {
    size: A4;
    margin: 1.6cm 1.5cm 1.9cm 1.5cm;
    @bottom-left {
        content: "CONFIDENTIAL \\2014 For internal review";
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

body {
    font-family: "Liberation Sans", Arial, sans-serif;
    color: #1f2733;
    font-size: 10.5pt;
    line-height: 1.5;
    margin: 0;
}

.banner {
    background: #16335c;
    background: linear-gradient(105deg, #16335c 0%, #234a86 100%);
    color: #ffffff;
    padding: 20px 24px;
    border-radius: 8px;
    margin-bottom: 26px;
}
.banner .eyebrow {
    font-size: 8.5pt;
    letter-spacing: 2.4px;
    text-transform: uppercase;
    color: #aebfdc;
    margin: 0 0 6px 0;
    font-weight: 700;
}
.banner h1 {
    font-size: 19pt;
    line-height: 1.2;
    margin: 0;
    font-weight: 700;
}
.banner .meta {
    margin-top: 10px;
    font-size: 9.5pt;
    color: #d6e0f2;
}
.banner .meta span { white-space: nowrap; }
.banner .dot { color: #6f8bc0; padding: 0 7px; }

h2.section {
    font-size: 11.5pt;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: #16335c;
    font-weight: 700;
    margin: 26px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #16335c;
}
section { break-inside: auto; }

.summary p { margin: 0 0 10px 0; text-align: justify; }

ul.followups { list-style: none; margin: 0; padding: 0; }
ul.followups li {
    position: relative;
    padding: 8px 10px 8px 30px;
    margin-bottom: 6px;
    background: #f4f6fa;
    border-left: 3px solid #234a86;
    border-radius: 0 4px 4px 0;
}
ul.followups li::before {
    content: "";
    position: absolute;
    left: 12px; top: 12px;
    width: 8px; height: 8px;
    background: #234a86;
    border-radius: 2px;
}
ul.followups .dim { font-weight: 700; color: #16335c; }
.allgood { color: #4a5566; font-style: italic; }

.review-note {
    font-size: 9pt;
    color: #6b7588;
    font-style: italic;
    margin: -6px 0 14px 0;
}

.conflict {
    border: 1px solid #d4dbe7;
    border-radius: 7px;
    margin-bottom: 16px;
    overflow: hidden;
    break-inside: avoid;
}
.conflict .topic {
    background: #16335c;
    color: #ffffff;
    font-weight: 700;
    font-size: 10.5pt;
    padding: 9px 14px;
}
.conflict .body { padding: 12px 14px; }
.conflict .explanation { color: #43506a; margin: 0 0 10px 0; }
.claim {
    border-left: 3px solid #234a86;
    background: #f4f6fa;
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 0 4px 4px 0;
}
.claim:last-child { margin-bottom: 0; }
.claim .who { font-weight: 700; color: #16335c; display: block; margin-bottom: 2px; }
.claim .quote { color: #2a3342; font-style: italic; }
"""


def build_pdf(title, summary, omissions, conflicts, incident_id=None, created_at=None, account_count=None):
    meta_bits = []
    if incident_id is not None:
        meta_bits.append(f"Incident #{escape(str(incident_id))}")
    if created_at:
        meta_bits.append(escape(created_at))
    if account_count is not None:
        plural = "account" if account_count == 1 else "accounts"
        meta_bits.append(f"{account_count} {plural}")
    meta = '<span class="dot">&middot;</span>'.join(f"<span>{b}</span>" for b in meta_bits)

    summary_html = "".join(
        f"<p>{escape(p.strip())}</p>"
        for p in (summary or "").split("\n")
        if p.strip()
    ) or "<p>No summary available.</p>"

    if omissions:
        items = []
        for item in omissions:
            dimension = escape(item.get("dimension", ""))
            note = escape(item.get("note", ""))
            note_html = f" &mdash; {note}" if note else ""
            items.append(f'<li><span class="dim">{dimension}</span>{note_html}</li>')
        followups_html = '<ul class="followups">' + "".join(items) + "</ul>"
    else:
        followups_html = '<p class="allgood">The reports covered all of the standard incident details.</p>'

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
        conflicts_html = '<p class="allgood">No genuine conflicts were found between the reports.</p>'

    document = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><style>{STYLE}</style></head>
<body>
    <div class="banner">
        <p class="eyebrow">Security Incident Report</p>
        <h1>{escape(title or "Incident Report")}</h1>
        <div class="meta">{meta}</div>
    </div>

    <section>
        <h2 class="section">Summary</h2>
        <div class="summary">{summary_html}</div>
    </section>

    <section>
        <h2 class="section">Follow-ups &middot; Missing Information</h2>
        {followups_html}
    </section>

    <section>
        <h2 class="section">Conflicts</h2>
        <p class="review-note">These are points for the team to review, not findings of wrongdoing.</p>
        {conflicts_html}
    </section>
</body>
</html>"""

    return HTML(string=document).write_pdf()
