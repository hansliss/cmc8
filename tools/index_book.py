"""Extract searchable OCR pages, retaining their PDF/image coordinates.

Run: python3 -m tools.index_book
The extracted text is an indexing aid. It never replaces visual evidence.
"""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    pdf = ROOT / 'Mikroprocessor_i_CMOS_ocr.pdf'
    result = subprocess.run(['pdftotext', '-layout', '-enc', 'UTF-8', str(pdf), '-'],
                            check=True, capture_output=True, text=True)
    pages = result.stdout.split('\f')
    if not pages[-1].strip():
        pages.pop()
    records = []
    for pdf_page, text in enumerate(pages, 1):
        # Verified coordinate relationship at several printed-page anchors.
        # The proposed printed number is not a visual verification of each page.
        printed = pdf_page - 7 if 8 <= pdf_page <= 225 else None
        image = f'bookpages/Page_{pdf_page - 1:03d}.jpg'
        records.append(dict(pdf_page=pdf_page, printed_page_candidate=printed,
                            image=image if (ROOT / image).exists() else None, text=text))
    document = dict(source=pdf.name, authority='OCR index only; consult page scans',
                    mapping='printed p -> PDF p+7 (1-based), image Page_(p+6).jpg',
                    pages=records)
    output = ROOT / 'specification/ocr-pages.json'
    output.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    print(f'Indexed {len(records)} PDF pages in {output.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
