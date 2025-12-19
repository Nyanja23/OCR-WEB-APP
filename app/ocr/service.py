from .pdf_loader import load_pdf_as_images
from .preprocessing import preprocess_image
from .ocr_engine import extract_text_from_image

def extract_text_from_pdf(pdf_path):

    images = load_pdf_as_images(pdf_path)

    all_text = []

    for page in images:
        processed = preprocess_image(page)
        text = extract_text_from_image(processed)
        all_text.append(text)
    
    return "\n".join(all_text)