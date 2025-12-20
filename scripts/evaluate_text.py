import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from difflib import Differ
import jiwer
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Assumes scripts/ folder structure
pdf_path = os.path.join(PROJECT_ROOT, "sample.pdf")

# ------------------ Your original preprocessing (the bad one) ------------------
def original_preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # Correct flag!
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )
    return thresh

# ------------------ No preprocessing (just grayscale) ------------------
def no_preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return gray

# ------------------ Ground truth text (from your <DOCUMENT>) ------------------
GROUND_TRUTH = """21st January 2023

NYANJA, Joseph

RE: SCHOLARSHIP AWARD LETTER

Dear Mr. Nyanja,

Reference is made to your admission letter dated 24th January 2023.

On behalf of Uganda Technology and Management University (UTAMU), it is my pleasure to notify you that you have been selected for our prestigious 2023 January Intake Annual Scholarship award for Bachelor of Science in Software Engineering you applied for. The semester will commence on 23rd January 2023. Our scholarship scheme was highly competitive, so I extend my congratulations to you on this scholarship award. In accepting this offer, you will become part of an institution that is focused on academic excellence, research, innovation, and delivery of an outstanding student experience.

On completion of your studies, you are expected to obtain either a First Class Degree or Second Class (Upper Division). The degree is classified according to the Cumulative Grade Point Average (CGPA). The First Class Degree is from a CGPA of 4.40 to 5.00 whereas a Second Class (Upper Division) is from a CGPA of 3.60 to 4.39. The pass mark for each course on this program is 50% and all students who score less than 50% in a course have to retake that course when it is next offered.

For purposes of this scholarship, an academic year runs from January to December of each year. The scholarship covers only tuition and functional fees and you are required to pay the National Council for Higher Education (NCHE) and Student Guild Fees that are paid annually and also meet your other expenses like stationery, transport, accommodation and meals.

Your scholarship will be for a duration of four (4) years and "renewable every academic year" upon your fulfilment of the terms and conditions of this scholarship award highlighted herein. Your continued eligibility for this scholarship will be based upon your scholastic performance. You must remain in Good Academic Standing in order to renew your scholarship annually (next academic year). If you do not remain in Good Academic Standing, the university has the option of withdrawing your scholarship award for the next academic year.

Upon completion of an academic year, the University will make an assessment of your general performance in the previous academic year to establish whether you are of good academic standing in order to be eligible for a scholarship for the next academic year.

For avoidance of doubt, you shall lose the scholarship if you fail to fulfil any of the following conditions:

(i) If your CGPA at the end of an academic year is less than 3.60, you will lose your scholarship for the next academic year but you still stand a chance to redeem your scholarship if in the academic year in which you lost your scholarship, you are able to raise your CGPA to at least 3.60.

(ii) If you happen to get a retake in any of the course units (scoring less than 50%), you will automatically lose the scholarship in the next academic year. Please note that even if you score less than 50% in the first semester of the academic year of study, you shall continue being on the scholarship until when you are assessed at the end of the academic year. This means that scoring less than 50% in any course unit makes you lose the continuity of your scholarship in the next academic year.

(iii) If you happen to miss any sitting for an examination in an academic year without obtaining authorization from the university upon providing genuine evidence of your inability to seat for the examination, you will automatically lose your scholarship in the next academic year.

If you happen to lose your scholarship, you will have to pay tuition and functional fees for the next academic year. However, upon providing genuine grounds of your inability to pay full tuition fees, the university will offer you a partial scholarship in order to enable you to continue with your academic programme.

This scholarship is for starting your studies in the January 2023 intake and cannot be deferred to the next intake.

We hope this scholarship will help you to concentrate on your studies without any financial burden.

Welcome to the MIT of Africa. Congratulations again!

Yours Faithfully,

Ms. Grace Nakawunde

ACADEMIC REGISTRAR

c.c. Chairperson, Board of Directors, UTAMU Chairperson, University Council, UTAMU Vice Chancellor, UTAMU University Secretary, UTAMU University Controller, UTAMU Internal Auditor, UTAMU Dean, School of Computing and Engineering

SCHOLARSHIP AWARD ACCEPTANCE AGREEMENT

Please consider my signature on this scholarship acceptance agreement as official acceptance of the scholarship offered to me to study the Bachelor of Science in Software Engineering at Uganda Technology and Management University (UTAMU) under the terms and conditions stated in the Scholarship Award letter addressed to me. My signature indicates that I understand and agree to comply with the scholarship terms and conditions.

As evidenced by my signature below, I agree to the terms and conditions of the scholarship award.

Name of Student: NYANJA JOSEPH

Signature of Student: Date: 29/01/2023

In the presence of:

Name of UTAMU Staff: ATAN ESTHER

Signature: Date and Stamp: 29/01/2023

UGANDA TECHNOLOGY & MANAGEMENT UNIVERSITY
UTAMU
Tel: (+256) 778 055 710, 750 599 736, 790 914 427, 702 646 093, 414 696887
Email: info@utamu.ac.ug / Website: www.utamu.ac.ug"""

# ------------------ Main evaluation ------------------
def evaluate_preprocessing(pdf_path, preprocess_func, name):
    pages = convert_from_path(pdf_path, dpi=400)  # higher DPI helps
    extracted = []

    for i, page in enumerate(pages):
        img = np.array(page)  # RGB
        processed = preprocess_func(img)
        text = pytesseract.image_to_string(processed, config='--psm 6 --oem 3')
        extracted.append(text)

    full_text = "\n".join(extracted).strip()

    # Normalize whitespace for fair comparison
    ground = " ".join(GROUND_TRUTH.split())
    pred = " ".join(full_text.split())

    # Metrics
    wer = jiwer.wer(ground, pred)
    cer = jiwer.cer(ground, pred)

    print(f"\n=== {name} ===")
    print(f"Word Error Rate (WER): {wer:.2%}")
    print(f"Character Error Rate (CER): {cer:.2%}")
    print("Sample extracted text (first 500 chars):")
    print(full_text[:500])

    # Optional: show diff
    differ = Differ()
    diff = list(differ.compare(ground.splitlines(), full_text.splitlines()))
    print("\nDiff (first 20 lines):")
    for line in diff[:20]:
        print(line)

    return wer, cer, full_text

if __name__ == "__main__":
    pdf_path = "sample.pdf"  # change if needed

    print("Evaluating original (bad) preprocessing...")
    original_wer, original_cer, _ = evaluate_preprocessing(pdf_path, original_preprocess, "Original Adaptive Thresholding")

    print("\nEvaluating no preprocessing (just grayscale)...")
    no_wer, no_cer, _ = evaluate_preprocessing(pdf_path, no_preprocess, "No Preprocessing (Grayscale)")

    print("\nSummary:")
    print(f"Original preprocessing → WER: {original_wer:.2%} | CER: {original_cer:.2%}")
    print(f"No preprocessing       → WER: {no_wer:.2%} | CER: {no_cer:.2%}")