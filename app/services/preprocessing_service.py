import cv2
import numpy as np
from PIL import Image
import io
import pdf2image
from app.core.logging import logger

class PreprocessingService:
    @staticmethod
    def process(file_bytes: bytes, filename: str) -> np.ndarray:
        logger.info(f"Preprocessing file: {filename}")
        
        # Etape 1: Conversion
        if filename.lower().endswith(".pdf"):
            logger.info("Converting PDF to image")
            pages = pdf2image.convert_from_bytes(file_bytes)
            # Take only the first page for this example
            if not pages:
                raise ValueError("PDF is empty")
            img = np.array(pages[0])
            # Convert RGB to BGR for OpenCV
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            logger.info("Loading image from bytes")
            nparr = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image")

        # Etape 2: Redressement (Deskewing)
        logger.info("Deskewing image")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Etape 3: Binarisation
        logger.info("Applying binarization")
        gray_deskewed = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(
            gray_deskewed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Etape 4: Réduction du bruit
        logger.info("Applying noise reduction")
        denoised = cv2.medianBlur(binary, 3)
        
        return denoised
