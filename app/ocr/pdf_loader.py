from pdf2image import convert_from_path
import numpy as np

def load_pdf_as_images(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300) 
    # Pages is a py list of OpenCv-compatible images of each Page of the Provided PDF
    return [np.array(page) for page in pages]