import fitz
import pytesseract
import cv2
import numpy as np

def ocr_from_pdf(path):
    """
    Performs OCR on a PDF by rendering pages to images using PyMuPDF (fitz)
    and then processing them with Tesseract.
    """
    doc = fitz.open(path)
    full_text = ""

    for page in doc:
        # Render page to a high-res image (zoom=2.0 for better OCR)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert pixmap to numpy array
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # Convert to BGR for OpenCV
        if pix.n == 4: # RGBA
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        else: # RGB
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Preprocessing for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        # Extract text
        text = pytesseract.image_to_string(thresh)
        full_text += text + "\n"

    doc.close()
    return full_text