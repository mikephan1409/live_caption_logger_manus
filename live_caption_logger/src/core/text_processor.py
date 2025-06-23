# Module xử lý văn bản cho Live Caption Logger

import re
import difflib
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

class TextProcessor:
    """
    Lớp chịu trách nhiệm xử lý và lọc văn bản từ OCR
    """
    
    def __init__(self, duplicate_threshold: float = 0.8, min_confidence: float = 30):
        """
        Khởi tạo text processor
        
        Args:
            duplicate_threshold: Ngưỡng để phát hiện văn bản trùng lặp (0-1)
            min_confidence: Độ tin cậy tối thiểu để chấp nhận văn bản
        """
        self.duplicate_threshold = duplicate_threshold
        self.min_confidence = min_confidence
        self.previous_texts = []  # Lưu trữ các văn bản trước đó
        self.current_session_text = ""  # Văn bản của phiên hiện tại
        self.session_start_time = None
        
    def clean_text(self, text: str) -> str:
        """
        Làm sạch văn bản từ OCR
        
        Args:
            text: Văn bản thô từ OCR
            
        Returns:
            Văn bản đã được làm sạch
        """
        if not text:
            return ""
        
        # Loại bỏ ký tự không mong muốn
        cleaned = re.sub(r'[^\w\s\.,!?;:\-\'"()áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]', '', text, flags=re.IGNORECASE)
        
        # Loại bỏ khoảng trắng thừa
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Loại bỏ khoảng trắng đầu và cuối
        cleaned = cleaned.strip()
        
        return cleaned
    
    def is_duplicate(self, new_text: str, previous_texts: List[str]) -> bool:
        """
        Kiểm tra xem văn bản có trùng lặp với các văn bản trước đó không
        
        Args:
            new_text: Văn bản mới
            previous_texts: Danh sách văn bản trước đó
            
        Returns:
            True nếu trùng lặp
        """
        if not new_text or not previous_texts:
            return False
        
        # So sánh với các văn bản gần đây nhất (10 văn bản cuối)
        recent_texts = previous_texts[-10:]
        
        for prev_text in recent_texts:
            similarity = difflib.SequenceMatcher(None, new_text.lower(), prev_text.lower()).ratio()
            if similarity >= self.duplicate_threshold:
                return True
        
        return False
    
    def is_incremental_update(self, new_text: str, previous_text: str) -> bool:
        """
        Kiểm tra xem văn bản mới có phải là cập nhật tăng dần của văn bản trước không
        
        Args:
            new_text: Văn bản mới
            previous_text: Văn bản trước đó
            
        Returns:
            True nếu là cập nhật tăng dần
        """
        if not previous_text or not new_text:
            return False
        
        # Kiểm tra xem văn bản mới có chứa văn bản cũ không
        if previous_text.lower() in new_text.lower():
            # Kiểm tra xem phần thêm vào có đáng kể không
            additional_text = new_text.lower().replace(previous_text.lower(), "").strip()
            if len(additional_text) > 3:  # Ít nhất 3 ký tự mới
                return True
        
        return False
    
    def extract_meaningful_text(self, ocr_result: Dict) -> Optional[str]:
        """
        Trích xuất văn bản có ý nghĩa từ kết quả OCR
        
        Args:
            ocr_result: Kết quả từ OCR processor
            
        Returns:
            Văn bản có ý nghĩa hoặc None
        """
        text = ocr_result.get('text', '')
        confidence = ocr_result.get('confidence', 0)
        
        # Kiểm tra độ tin cậy
        if confidence < self.min_confidence:
            return None
        
        # Làm sạch văn bản
        cleaned_text = self.clean_text(text)
        
        # Kiểm tra độ dài tối thiểu
        if len(cleaned_text) < 3:
            return None
        
        # Kiểm tra tỷ lệ từ hợp lệ
        words = cleaned_text.split()
        valid_words = [word for word in words if len(word) > 1 and word.isalnum()]
        
        if len(valid_words) / len(words) < 0.5:  # Ít nhất 50% từ hợp lệ
            return None
        
        return cleaned_text
    
    def process_new_text(self, ocr_result: Dict) -> Optional[Dict]:
        """
        Xử lý văn bản mới từ OCR
        
        Args:
            ocr_result: Kết quả từ OCR processor
            
        Returns:
            Dictionary chứa thông tin văn bản đã xử lý hoặc None
        """
        meaningful_text = self.extract_meaningful_text(ocr_result)
        
        if not meaningful_text:
            return None
        
        # Kiểm tra trùng lặp
        if self.is_duplicate(meaningful_text, self.previous_texts):
            return None
        
        # Kiểm tra cập nhật tăng dần
        is_incremental = False
        if self.previous_texts:
            last_text = self.previous_texts[-1]
            is_incremental = self.is_incremental_update(meaningful_text, last_text)
        
        # Tạo timestamp
        timestamp = datetime.now()
        
        # Tạo ID duy nhất cho văn bản
        text_id = hashlib.md5(f"{meaningful_text}{timestamp}".encode()).hexdigest()[:8]
        
        # Thêm vào danh sách văn bản trước đó
        self.previous_texts.append(meaningful_text)
        
        # Giới hạn số lượng văn bản lưu trữ
        if len(self.previous_texts) > 100:
            self.previous_texts = self.previous_texts[-50:]  # Giữ lại 50 văn bản gần nhất
        
        # Cập nhật văn bản phiên hiện tại
        if not is_incremental:
            if self.current_session_text:
                self.current_session_text += " " + meaningful_text
            else:
                self.current_session_text = meaningful_text
                self.session_start_time = timestamp
        else:
            # Thay thế văn bản cũ bằng văn bản mới (cập nhật tăng dần)
            self.current_session_text = meaningful_text
        
        return {
            'id': text_id,
            'text': meaningful_text,
            'timestamp': timestamp,
            'confidence': ocr_result.get('confidence', 0),
            'is_incremental': is_incremental,
            'session_text': self.current_session_text
        }
    
    def finalize_session(self) -> Optional[Dict]:
        """
        Hoàn thiện phiên ghi chép hiện tại
        
        Returns:
            Dictionary chứa thông tin phiên hoàn chỉnh
        """
        if not self.current_session_text or not self.session_start_time:
            return None
        
        session_data = {
            'text': self.current_session_text,
            'start_time': self.session_start_time,
            'end_time': datetime.now(),
            'word_count': len(self.current_session_text.split()),
            'character_count': len(self.current_session_text)
        }
        
        # Reset phiên hiện tại
        self.current_session_text = ""
        self.session_start_time = None
        
        return session_data
    
    def get_session_summary(self) -> Dict:
        """
        Lấy tóm tắt phiên hiện tại
        
        Returns:
            Dictionary chứa thông tin tóm tắt
        """
        return {
            'current_text': self.current_session_text,
            'start_time': self.session_start_time,
            'word_count': len(self.current_session_text.split()) if self.current_session_text else 0,
            'character_count': len(self.current_session_text) if self.current_session_text else 0,
            'total_processed': len(self.previous_texts)
        }
    
    def reset_session(self):
        """
        Reset phiên ghi chép hiện tại
        """
        self.current_session_text = ""
        self.session_start_time = None
        self.previous_texts = []

