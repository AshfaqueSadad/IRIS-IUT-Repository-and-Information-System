import io
import pymupdf as fitz
from PIL import Image
import numpy as np
import cv2
import pytesseract
from app.core.config import settings

if settings.TESSERACT_CMD_PATH:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD_PATH


class OCRPipeline:
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> tuple[str, bool]:
        """Extract text directly from PDF if native, or return empty if image-based."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = []
        is_scanned = False

        for page in doc:
            text = page.get_text().strip()
            if text:
                full_text.append(text)
            else:
                is_scanned = True

        combined_text = "\n\n".join(full_text)
        # If very little or no native text, mark as scanned for OCR
        if len(combined_text) < 50:
            is_scanned = True

        return combined_text, is_scanned

    @staticmethod
    def preprocess_image_for_ocr(image_bytes: bytes) -> np.ndarray:
        """Clean up photograph or scan with OpenCV: grayscale, contrast, denoise, deskew."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image bytes")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Contrast enhancement via CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)

        # Bilateral filter for noise reduction while keeping edges sharp
        denoised = cv2.bilateralFilter(contrast, 9, 75, 75)

        # Otsu thresholding for crisp black & white text
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return thresh

    @staticmethod
    def extract_text_with_tesseract(preprocessed_img: np.ndarray) -> str:
        """Run Tesseract OCR on preprocessed image."""
        config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(preprocessed_img, config=config)
        return text.strip()


ocr_pipeline = OCRPipeline()
