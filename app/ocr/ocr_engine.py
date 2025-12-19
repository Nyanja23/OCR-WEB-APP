import pytesseract

TESSERACT_CONFIG = '--oem 1 --psm 6'

def extract_text_from_image(image):
    # Here, We run OCR on a processed Image with a config for better results

    return pytesseract.image_to_string(image, config=TESSERACT_CONFIG)

