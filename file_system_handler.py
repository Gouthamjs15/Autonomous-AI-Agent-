from fpdf import FPDF
import json
import os
from bs4 import BeautifulSoup
import unicodedata
import re

def sanitize_text(text):
    """Remove non-latin1 characters, emojis, and weird quotes from text."""
    if not text: return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # ASCII only (optional, extra safe)
    return text

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", "", 12)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, sanitize_text(title), ln=True)
        self.ln(2)

    def add_text(self, text):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 8, sanitize_text(text))
        self.ln(2)

    def add_image(self, image_path, max_width=160):
        if os.path.exists(image_path):
            try:
                self.image(image_path, w=max_width)
                self.ln(3)
            except RuntimeError as e:
                print(f"[Image Error] Failed to load in PDF: {e}")

    def add_list(self, items, title):
        if not items: return
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, sanitize_text(title), ln=True)
        self.set_font("Arial", "", 11)
        for item in items:
            self.cell(5)
            self.multi_cell(0, 8, f"- {sanitize_text(item)}")
        self.ln(2)

    def add_table(self, table_html):
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.find_all("tr")
        if not rows: return
        self.set_font("Arial", "I", 10)
        self.cell(0, 8, "[Embedded table below]", ln=True)
        for row in rows:
            cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
            self.multi_cell(0, 7, sanitize_text(" | ".join(cols)))
        self.ln(3)

def generate_pdf(summary_file, keyword_file, output_path="final_report.pdf"):
    with open(summary_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if keyword_file and os.path.exists(keyword_file):
        with open(keyword_file, "r", encoding="utf-8") as f:
            keyword_data = json.load(f)
    else:
        keyword_data = {}

    pdf = PDF()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="AI Summarized Report", ln=True, align="C")
    pdf.ln(10)

    for entry in data:
        url = entry.get("url", "")
        summary = entry.get("summary", entry.get("text", ""))
        images = entry.get("images", [])
        pros = entry.get("pros", [])
        cons = entry.get("cons", [])
        tables = entry.get("tables", [])

        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, sanitize_text(f"Source: {url}"))
        pdf.ln(1)

        pdf.add_text(summary)
        pdf.add_list(pros, "Pros")
        pdf.add_list(cons, "Cons")

        for img_path in images[:3]:
            pdf.add_image(img_path)

        for table_html in tables[:1]:
            pdf.add_table(table_html)

        pdf.ln(5)
        pdf.cell(0, 0, "-" * 80, ln=True)
        pdf.ln(5)

    if keyword_data:
        pdf.add_page()
        pdf.chapter_title("Keywords")
        for url, keywords in keyword_data.items():
            line = f"{url}\n- " + ", ".join(sanitize_text(k) for k in keywords)
            pdf.add_text(line)

    pdf.output(output_path)
    print(f"[✅] PDF saved as: {output_path}")
