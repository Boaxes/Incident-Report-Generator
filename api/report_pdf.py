from fpdf import FPDF
from fpdf.enums import XPos, YPos


def build_pdf(title, summary, omissions, conflicts):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # fpdf2 core fonts are latin-1; replace anything outside it so output never fails.
    def text(value):
        return str(value).encode("latin-1", "replace").decode("latin-1")

    # Every block returns the cursor to the left margin so consecutive blocks have room.
    def line(value, size=11, style=""):
        pdf.set_font("Helvetica", style, size)
        pdf.multi_cell(0, 6, text(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "B", 18)
    pdf.multi_cell(0, 10, text(title or "Incident Report"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    line("Summary", size=14, style="B")
    line(summary or "No summary available.")
    pdf.ln(4)

    line("Follow-ups: likely missing information", size=14, style="B")
    if omissions:
        for item in omissions:
            dimension = item.get("dimension", "")
            note = item.get("note", "")
            line(f"- {dimension}: {note}" if note else f"- {dimension}")
    else:
        line("The reports covered all of the standard incident details.")
    pdf.ln(4)

    line("Conflicts", size=14, style="B")
    line("These are points for the team to review, not findings of wrongdoing.", size=10, style="I")
    pdf.ln(2)
    if conflicts:
        for conflict in conflicts:
            line(conflict.get("topic", ""), style="B")
            explanation = conflict.get("explanation", "")
            if explanation:
                line(explanation)
            for claim in conflict.get("claims", []):
                line(f'   {claim.get("label", "")}: "{claim.get("quote", "")}"')
            pdf.ln(2)
    else:
        line("No genuine conflicts were found between the reports.")

    return bytes(pdf.output())
