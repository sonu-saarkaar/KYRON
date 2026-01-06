"""
KYRON OCR Service
Extracts text from uploaded documents (PDFs, Images) using OCR
"""

import os
# Make pytesseract optional
try:
    import pytesseract  # type: ignore
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    pytesseract = None  # type: ignore

# Make PIL (Pillow) optional
try:
    from PIL import Image  # type: ignore
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # type: ignore

# Make pdf2image optional
try:
    from pdf2image import convert_from_path  # type: ignore
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    convert_from_path = None  # type: ignore

# Make PyPDF2 optional
try:
    from PyPDF2 import PdfReader  # type: ignore
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    PdfReader = None  # type: ignore
import io
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """OCR service for extracting text from documents"""
    
    def __init__(self):
        """Initialize OCR service"""
        if not PYTESSERACT_AVAILABLE:
            logger.warning("pytesseract not available. OCR features will be limited.")
            return
        
        # Set Tesseract path if needed (Windows)
        if os.name == 'nt':  # Windows
            # Try common Tesseract installation paths
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, any]:
        """
        Extract text from an image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not PYTESSERACT_AVAILABLE or not PIL_AVAILABLE:
            return {
                "success": False,
                "error": "OCR dependencies not installed. Install with: pip install pytesseract pillow",
                "text": "",
                "confidence": 0
            }
        
        try:
            image = Image.open(image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Get detailed data (bounding boxes, confidence, etc.)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": avg_confidence,
                "word_count": len(text.split()),
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0
            }
    
    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = True) -> Dict[str, any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            use_ocr: If True, use OCR for scanned PDFs. If False, extract text directly.
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not PYPDF2_AVAILABLE:
            return {
                "success": False,
                "error": "PyPDF2 not installed. Install with: pip install PyPDF2",
                "text": "",
                "confidence": 0
            }
        
        try:
            # First, try to extract text directly (for text-based PDFs)
            reader = PdfReader(pdf_path)
            direct_text = ""
            
            for page in reader.pages:
                direct_text += page.extract_text() + "\n"
            
            # If we got substantial text, return it
            if len(direct_text.strip()) > 100:
                return {
                    "success": True,
                    "text": direct_text.strip(),
                    "method": "direct_extraction",
                    "confidence": 100,
                    "word_count": len(direct_text.split())
                }
            
            # If not, use OCR (for scanned PDFs)
            if use_ocr:
                if not PYTESSERACT_AVAILABLE or not PDF2IMAGE_AVAILABLE or not PIL_AVAILABLE:
                    return {
                        "success": True,
                        "text": direct_text.strip(),
                        "method": "direct_extraction",
                        "confidence": 0,
                        "word_count": len(direct_text.split()),
                        "warning": "OCR not available. Install: pip install pytesseract pillow pdf2image"
                    }
                
                logger.info(f"Using OCR for PDF: {pdf_path}")
                
                # Convert PDF pages to images
                images = convert_from_path(pdf_path, dpi=300)
                
                all_text = []
                total_confidence = 0
                page_count = 0
                
                for image in images:
                    page_text = pytesseract.image_to_string(image)
                    all_text.append(page_text)
                    
                    # Get confidence for this page
                    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    if confidences:
                        total_confidence += sum(confidences) / len(confidences)
                        page_count += 1
                
                combined_text = "\n\n".join(all_text)
                avg_confidence = total_confidence / page_count if page_count > 0 else 0
                
                return {
                    "success": True,
                    "text": combined_text.strip(),
                    "method": "ocr",
                    "confidence": avg_confidence,
                    "word_count": len(combined_text.split()),
                    "pages": len(images)
                }
            else:
                # No OCR requested and no text extracted
                return {
                    "success": True,
                    "text": direct_text.strip(),
                    "method": "direct_extraction",
                    "confidence": 0,
                    "word_count": 0,
                    "warning": "PDF appears to be scanned. Enable OCR for better results."
                }
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0
            }
    
    def extract_text(self, file_path: str) -> Dict[str, any]:
        """
        Extract text from a file (auto-detect type)
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
            return self.extract_text_from_image(file_path)
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_extension}"
            }
    
    def extract_structured_data(self, text: str, document_type: str) -> Dict[str, any]:
        """
        Extract structured data from OCR text based on document type
        
        Args:
            text: Extracted text from OCR
            document_type: Type of document (e.g., "PAN", "Aadhaar", "Passport", etc.)
            
        Returns:
            Dictionary with structured data
        """
        structured_data = {
            "document_type": document_type,
            "fields": {}
        }
        
        text_lower = text.lower()
        
        # Common field extraction patterns
        patterns = {
            "PAN": {
                "pan_number": r"[A-Z]{5}[0-9]{4}[A-Z]",
                "name": r"(?i)name[:\s]+([A-Z\s]+)",
                "father_name": r"(?i)father['']?s?\s+name[:\s]+([A-Z\s]+)"
            },
            "Aadhaar": {
                "aadhaar_number": r"\d{4}\s?\d{4}\s?\d{4}",
                "name": r"(?i)name[:\s]+([A-Z\s]+)",
                "dob": r"(?i)(?:dob|date of birth)[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})"
            },
            "Passport": {
                "passport_number": r"[A-Z][0-9]{7,9}",
                "name": r"(?i)surname[:\s]+([A-Z\s]+)",
                "dob": r"(?i)date of birth[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})"
            }
        }
        
        import re
        
        if document_type in patterns:
            for field_name, pattern in patterns[document_type].items():
                matches = re.findall(pattern, text)
                if matches:
                    structured_data["fields"][field_name] = matches[0] if isinstance(matches[0], str) else matches
        
        return structured_data


# Global instance
_ocr_service: Optional[OCRService] = None

def get_ocr_service() -> Optional[OCRService]:
    """Get or create global OCR service instance"""
    global _ocr_service
    if not PYTESSERACT_AVAILABLE or not PIL_AVAILABLE:
        logger.warning("OCR dependencies not available. OCR service disabled.")
        return None
    if _ocr_service is None:
        try:
            _ocr_service = OCRService()
        except Exception as e:
            logger.warning(f"Failed to initialize OCR service: {e}")
            return None
    return _ocr_service

