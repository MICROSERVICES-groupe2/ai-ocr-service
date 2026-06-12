import pytesseract
import easyocr
import numpy as np
import cv2
from app.services.preprocessing_service import PreprocessingService
from app.core.config import settings
from app.core.logging import logger

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

class OCRService:
    def __init__(self):
        # Initialise EasyOCR reader (langues fr et en)
        logger.info("Initializing EasyOCR reader...")
        self.reader = easyocr.Reader(['fr', 'en'], gpu=False)

    def extract(self, file_bytes: bytes, filename: str) -> dict:
        logger.info(f"Extracting text from {filename}")
        
        # 1. Preprocessing
        processed_img = PreprocessingService.process(file_bytes, filename)
        
        # 2. Tesseract OCR
        logger.info("Attempting Tesseract OCR")
        ocr_data = pytesseract.image_to_data(processed_img, lang=settings.OCR_LANGUAGES, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence
        confidences = [int(c) for c in ocr_data['conf'] if int(c) != -1]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Reconstruct text
        text = " ".join([word for word, conf in zip(ocr_data['text'], ocr_data['conf']) if int(conf) != -1 and word.strip()])
        
        logger.info(f"Tesseract confidence: {avg_confidence}%")
        
        # 3. Fallback EasyOCR
        if avg_confidence < 60:
            logger.warning("Tesseract confidence low (<60%), falling back to EasyOCR")
            result = self.reader.readtext(processed_img, detail=1)
            # result is a list of tuples: (bbox, text, prob)
            texts = []
            probs = []
            for (bbox, t, prob) in result:
                texts.append(t)
                probs.append(prob)
                
            text = " ".join(texts)
            avg_confidence = (sum(probs) / len(probs)) * 100 if probs else 0
            logger.info(f"EasyOCR extraction complete, confidence: {avg_confidence}%")
            
        return {
            "text": text,
            "confidence": avg_confidence
        }

ocr_service = OCRService()
