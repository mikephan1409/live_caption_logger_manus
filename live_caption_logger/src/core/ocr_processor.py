# Module xử lý OCR cho Live Caption Logger

import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional, Dict, List
import re

class OCRProcessor:
    """
    Lớp chịu trách nhiệm xử lý OCR để trích xuất văn bản từ ảnh
    """
    
    def __init__(self, language: str = 'eng', psm: int = 6, oem: int = 3):
        """
        Khởi tạo OCR processor
        
        Args:
            language: Ngôn ngữ OCR (eng, vie, etc.)
            psm: Page Segmentation Mode
            oem: OCR Engine Mode
        """
        self.language = language
        self.psm = psm
        self.oem = oem
        self.config = f'--psm {psm} --oem {oem}'
        
        # Kiểm tra xem Tesseract có được cài đặt không
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            print(f"Lỗi: Tesseract chưa được cài đặt hoặc không tìm thấy: {e}")
            print("Vui lòng cài đặt Tesseract OCR")
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Tiền xử lý ảnh để cải thiện độ chính xác OCR
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Ảnh đã được tiền xử lý
        """
        # Chuyển PIL Image sang OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Chuyển sang grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Tăng độ tương phản
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Khử nhiễu
        denoised = cv2.medianBlur(enhanced, 3)
        
        # Threshold để tạo ảnh đen trắng rõ nét
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Chuyển lại sang PIL Image
        processed_image = Image.fromarray(thresh)
        
        return processed_image
    
    def extract_text(self, image: Image.Image, preprocess: bool = True) -> Dict:
        """
        Trích xuất văn bản từ ảnh
        
        Args:
            image: Ảnh đầu vào
            preprocess: Có tiền xử lý ảnh không
            
        Returns:
            Dictionary chứa text và confidence
        """
        try:
            # Tiền xử lý ảnh nếu cần
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image
            
            # Trích xuất văn bản với confidence
            data = pytesseract.image_to_data(
                processed_image, 
                lang=self.language,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Lọc và ghép các từ có confidence cao
            words = []
            confidences = []
            
            for i in range(len(data['text'])):
                word = data['text'][i].strip()
                conf = int(data['conf'][i])
                
                if word and conf > 0:  # Chỉ lấy từ có confidence > 0
                    words.append(word)
                    confidences.append(conf)
            
            # Ghép thành câu
            text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text,
                'confidence': avg_confidence,
                'word_count': len(words),
                'raw_data': data
            }
            
        except Exception as e:
            print(f"Lỗi khi xử lý OCR: {e}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'raw_data': None
            }
    
    def extract_text_simple(self, image: Image.Image) -> str:
        """
        Trích xuất văn bản đơn giản từ ảnh
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Văn bản được trích xuất
        """
        try:
            processed_image = self.preprocess_image(image)
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config=self.config
            )
            return text.strip()
        except Exception as e:
            print(f"Lỗi khi xử lý OCR đơn giản: {e}")
            return ""
    
    def detect_language(self, image: Image.Image) -> str:
        """
        Phát hiện ngôn ngữ trong ảnh
        
        Args:
            image: Ảnh đầu vào
            
        Returns:
            Mã ngôn ngữ được phát hiện
        """
        try:
            processed_image = self.preprocess_image(image)
            languages = pytesseract.image_to_osd(processed_image)
            
            # Parse kết quả để lấy ngôn ngữ
            for line in languages.split('\n'):
                if 'Script:' in line:
                    script = line.split(':')[1].strip()
                    # Mapping một số script phổ biến
                    script_mapping = {
                        'Latin': 'eng',
                        'Han': 'chi_sim',
                        'Hiragana': 'jpn',
                        'Katakana': 'jpn'
                    }
                    return script_mapping.get(script, 'eng')
            
            return 'eng'  # Mặc định là tiếng Anh
            
        except Exception as e:
            print(f"Lỗi khi phát hiện ngôn ngữ: {e}")
            return 'eng'
    
    def set_language(self, language: str):
        """
        Thiết lập ngôn ngữ OCR
        
        Args:
            language: Mã ngôn ngữ (eng, vie, chi_sim, etc.)
        """
        self.language = language
    
    def get_available_languages(self) -> List[str]:
        """
        Lấy danh sách ngôn ngữ có sẵn
        
        Returns:
            Danh sách mã ngôn ngữ
        """
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            print(f"Lỗi khi lấy danh sách ngôn ngữ: {e}")
            return ['eng']
    
    def validate_text(self, text: str, min_confidence: float = 30) -> bool:
        """
        Kiểm tra tính hợp lệ của văn bản được trích xuất
        
        Args:
            text: Văn bản cần kiểm tra
            min_confidence: Độ tin cậy tối thiểu
            
        Returns:
            True nếu văn bản hợp lệ
        """
        if not text or len(text.strip()) < 3:
            return False
        
        # Kiểm tra tỷ lệ ký tự đặc biệt
        special_chars = re.findall(r'[^a-zA-Z0-9\s\.,!?;:\-\'"()]', text)
        if len(special_chars) / len(text) > 0.3:  # Quá nhiều ký tự đặc biệt
            return False
        
        return True

