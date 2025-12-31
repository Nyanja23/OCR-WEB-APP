from pdf2image import convert_from_path
import numpy as np

def load_pdf_as_images(file_path):
    if file_path.lower().endswith('.pdf'):
        pages = convert_from_path(file_path, dpi=300)
    else:
        pages = convert_from_path(file_path)  # Single image as "page"

    # Pages is a py list of OpenCv-compatible images of each Page of the Provided PDF
    return [np.array(page) for page in pages] # An image represented as numbers instead of pixels on screen best for OpenCv to process