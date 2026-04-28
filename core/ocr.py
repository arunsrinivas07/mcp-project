from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np

def ocr_from_pdf(path):
    pages = convert_from_path(path)
    full_text = ""

    for page in pages:
        img = np.array(page)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(thresh)
        full_text += text

    return full_text