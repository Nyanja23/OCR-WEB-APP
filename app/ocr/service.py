from .pdf_loader import load_pdf_as_images
from .preprocessing import preprocess_image, improved_preprocess
from .ocr_engine import extract_text_from_image

def extract_text_from_file(file_path, use_improved=True,lang='eng'):

    images = load_pdf_as_images(file_path)

    page_texts = []

    for image in images:
        if use_improved:
            processed = improved_preprocess(image)
        else:
            processed = preprocess_image(image)
        
        text = extract_text_from_image(processed, lang=lang).strip()
        
        page_texts.append(text)
    
    full_text = '\n\n'.join(page_texts)
    
    return full_text, page_texts