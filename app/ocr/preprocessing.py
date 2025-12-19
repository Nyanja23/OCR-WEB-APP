import cv2
import numpy as np

def preprocess_image(image):
    # 1. Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Upscale for better text resolution (Tesseract likes >20px char height)
    #    Factor of 1.5-2x; adjust based on your DPI (300 is base)
    upscale_factor = 1.5
    gray = cv2.resize(gray, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_LINEAR)
    
    # 3. Contrast enhancement with CLAHE (handles uneven lighting in photos)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 4. Denoising: Bilateral filter preserves edges better for text
    denoised = cv2.bilateralFilter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)
    # Alternative: Median blur if bilateral is too slow
    # denoised = cv2.medianBlur(enhanced, 3)
    
    # 5. Deskew: Correct rotation (place early to align before threshold)
    coords = np.column_stack(np.where(denoised > 0))
    if len(coords) == 0:
        deskewed = denoised
    else:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) > 0.5:  # Only if skew >0.5 degrees
            (h, w) = denoised.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            deskewed = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        else:
            deskewed = denoised
    
    # 6. Adaptive thresholding: Use MEAN_C for photos; larger block for less noise
    thresh = cv2.adaptiveThreshold(
        deskewed,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,  # Or GAUSSIAN_C; MEAN often smoother for uneven light
        cv2.THRESH_BINARY,
        41,  # Larger block (31-51) for photos; try 21 if text is small
        10   # Higher C (5-15) subtracts more; reduces artifacts
    )
    
    # Optional: Skip binarization, use enhanced grayscale (often better for Tesseract v4+)
    # return deskewed  # Uncomment to test grayscale only
    
    # 7. Morphology: Light erosion to remove noise, dilation to connect broken text
    kernel = np.ones((2, 2), np.uint8)  # Small kernel to avoid over-thickening
    thresh = cv2.erode(thresh, kernel, iterations=1)
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    
    # 8. Optional invert check (ensure black text on white)
    if np.mean(thresh) < 128:  # Mostly black → invert
        thresh = cv2.bitwise_not(thresh)
    
    return thresh