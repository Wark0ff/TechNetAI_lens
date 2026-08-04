#!/usr/bin/env python3
# OCR графических PDF (без текстового слоя) → sources_text/<base>.txt.
# Требует: pymupdf (рендер страниц) + Tesseract с языковыми данными rus+eng.
# Запуск: python scripts/ocr_reports.py file1.pdf file2.pdf ...
import sys, os, json, subprocess, tempfile, shutil, glob
import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_tesseract():
    for p in [
        r"C:/Program Files/Tesseract-OCR/tesseract.exe",
        r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe",
        os.path.expanduser(r"~/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"),
    ]:
        if os.path.exists(p):
            return p
    return shutil.which("tesseract")

def ocr_pdf(pdf_path, tess, lang="rus+eng", dpi=300):
    doc = fitz.open(pdf_path)
    parts = []
    with tempfile.TemporaryDirectory() as td:
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            img = os.path.join(td, f"p{i}.png")
            pix.save(img)
            base = os.path.join(td, f"p{i}")
            r = subprocess.run([tess, img, base, "-l", lang, "--psm", "3"],
                               capture_output=True, text=True)
            txtf = base + ".txt"
            if os.path.exists(txtf):
                parts.append(open(txtf, encoding="utf-8", errors="ignore").read())
    return "\n".join(parts)

def main():
    tess = find_tesseract()
    if not tess:
        print("ОШИБКА: tesseract не найден"); sys.exit(2)
    print("tesseract:", tess)
    files = sys.argv[1:]
    if not files:
        # по умолчанию — все image_based из индекса
        d = json.load(open(os.path.join(ROOT, "data/reports_index.json"), encoding="utf-8"))
        files = [r["file"] for r in d["reports"] if r["image_based"]]
    for f in files:
        pdf = os.path.join(ROOT, "sources", f)
        base = os.path.splitext(f)[0]
        txt = ocr_pdf(pdf, tess)
        outp = os.path.join(ROOT, "sources_text", base + ".txt")
        open(outp, "w", encoding="utf-8").write(txt)
        print(f"OCR done: {f} -> {len(txt)} симв.")

if __name__ == "__main__":
    main()
