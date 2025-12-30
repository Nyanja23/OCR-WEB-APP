import sys

from app.ocr.service import extract_text_from_pdf
from pathlib import Path

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

if __name__ == '__main__':
    if(len(sys.argv)) != 2:
        print("Usage: python test_ocr.py <pdf_path>")
        sys.exit(1)


    pdf_path = sys.argv[1]
    text = extract_text_from_pdf(pdf_path)

    # print('\n=== OCR OUTPUT ===\n')
    # print(text)

    with open(output_dir / "output.txt", "w", encoding="utf-8") as f:
        f.write(text)