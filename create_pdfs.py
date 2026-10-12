from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT


# Folder containing our text documents
documents_folder = Path("documents")

# PDF formatting
styles = getSampleStyleSheet()
body_style = styles["BodyText"]
body_style.alignment = TA_LEFT
body_style.leading = 14

heading_style = styles["Heading1"]

# Text files we want to convert
files = [
    "home_loan",
    "personal_loan",
    "debit_card_policy",
    "banking_faq"
]


for file_name in files:

    txt_path = documents_folder / f"{file_name}.txt"
    pdf_path = documents_folder / f"{file_name}.pdf"

    # Read the text file
    text = txt_path.read_text(encoding="utf-8")

    # Create PDF
    pdf = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    story = []

    # Add each line to the PDF
    for line in text.splitlines():

        line = line.strip()

        if not line:
            story.append(Spacer(1, 8))
            continue

        # Main title
        if line.startswith("NOVABANK"):
            story.append(
                Paragraph(line, heading_style)
            )

        else:
            # Escape special characters for ReportLab
            safe_line = (
                line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            story.append(
                Paragraph(safe_line, body_style)
            )

    pdf.build(story)

    print(f"Created: {pdf_path}")


print("\nAll banking PDFs created successfully!")