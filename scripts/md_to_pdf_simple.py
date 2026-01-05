from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from pathlib import Path

MD_PATH = Path("reports/note_analyse_macro.md")
PDF_PATH = Path("reports/note_analyse_macro.pdf")

def wrap_text(text, max_chars=95):
    words = text.split()
    lines, line = [], []
    n = 0
    for w in words:
        if n + len(w) + (1 if line else 0) <= max_chars:
            line.append(w)
            n += len(w) + (1 if line else 0)
        else:
            lines.append(" ".join(line))
            line = [w]
            n = len(w)
    if line:
        lines.append(" ".join(line))
    return lines

def main():
    c = canvas.Canvas(str(PDF_PATH), pagesize=A4)
    width, height = A4

    x = 2.0 * cm
    y = height - 2.0 * cm

    font_body = ("Helvetica", 11)
    font_h1 = ("Helvetica-Bold", 18)
    font_h2 = ("Helvetica-Bold", 14)

    c.setTitle("Note d’analyse macroéconomique")

    md = MD_PATH.read_text(encoding="utf-8").splitlines()

    def new_page():
        nonlocal y
        c.showPage()
        y = height - 2.0 * cm

    for raw in md:
        line = raw.rstrip()

        # Saut de ligne
        if not line.strip():
            y -= 10
            if y < 2.0 * cm:
                new_page()
            continue

        # Titres
        if line.startswith("# "):
            c.setFont(*font_h1)
            y -= 8
            c.drawString(x, y, line[2:].strip())
            y -= 18
            c.setFont(*font_body)
            if y < 2.0 * cm:
                new_page()
            continue

        if line.startswith("## "):
            c.setFont(*font_h2)
            y -= 6
            c.drawString(x, y, line[3:].strip())
            y -= 14
            c.setFont(*font_body)
            if y < 2.0 * cm:
                new_page()
            continue

        # Listes
        if line.lstrip().startswith(("-", "*")):
            text = "• " + line.lstrip()[1:].strip()
            c.setFont(*font_body)
            for wline in wrap_text(text):
                c.drawString(x, y, wline)
                y -= 14
                if y < 2.0 * cm:
                    new_page()
            continue

        # Texte normal
        c.setFont(*font_body)
        for wline in wrap_text(line):
            c.drawString(x, y, wline)
            y -= 14
            if y < 2.0 * cm:
                new_page()

    c.save()
    print(f"✅ PDF créé : {PDF_PATH}")

if __name__ == "__main__":
    main()
