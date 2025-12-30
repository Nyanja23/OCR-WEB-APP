import cv2

def preprocess_image(image):

    #Here, We apply grayscale and adaptive thresholding.

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return thresh

def improved_preprocess(image):
    # image is RGB from np.array(PIL_page)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Light edge-preserving denoising
    denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Contrast Limited Adaptive Histogram Equalization — great for photos
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Optional: very mild upscale if text appears small (helps Tesseract)
    # enhanced = cv2.resize(enhanced, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_LINEAR)
    
    return enhanced  # Grayscale — no binarization!