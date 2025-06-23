# Module chụp màn hình cho Live Caption Logger

import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageGrab
import time
from typing import Optional, Tuple
import threading
import queue

class ScreenCapture:
    """
    Lớp chịu trách nhiệm chụp màn hình và quản lý vùng chụp
    """
    
    def __init__(self):
        self.capture_region = None  # (x, y, width, height)
        self.is_capturing = False
        self.capture_thread = None
        self.image_queue = queue.Queue(maxsize=10)
        
        # Tắt fail-safe của pyautogui để tránh lỗi khi chạy trong môi trường headless
        pyautogui.FAILSAFE = False
    
    def set_capture_region(self, x: int, y: int, width: int, height: int):
        """
        Thiết lập vùng chụp màn hình
        
        Args:
            x, y: Tọa độ góc trên trái
            width, height: Kích thước vùng chụp
        """
        self.capture_region = (x, y, width, height)
    
    def auto_detect_live_caption_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Tự động phát hiện vùng Live Caption trên màn hình
        
        Returns:
            Tuple (x, y, width, height) nếu tìm thấy, None nếu không
        """
        # Chụp toàn màn hình
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Chuyển sang grayscale để dễ xử lý
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # Tìm các vùng có thể là Live Caption (thường có nền đen hoặc tối)
        # Đây là một heuristic đơn giản, có thể cần tinh chỉnh
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        
        # Tìm contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Lọc các contour có kích thước phù hợp với Live Caption
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Live Caption thường có tỷ lệ rộng/cao khoảng 3:1 đến 6:1
            if 100 < w < 800 and 30 < h < 150 and 2 < w/h < 8:
                return (x, y, w, h)
        
        return None
    
    def capture_screenshot(self) -> Optional[Image.Image]:
        """
        Chụp ảnh màn hình theo vùng đã thiết lập
        
        Returns:
            PIL Image nếu thành công, None nếu thất bại
        """
        try:
            if self.capture_region:
                x, y, width, height = self.capture_region
                # Sử dụng ImageGrab để chụp vùng cụ thể
                bbox = (x, y, x + width, y + height)
                screenshot = ImageGrab.grab(bbox)
            else:
                # Chụp toàn màn hình
                screenshot = pyautogui.screenshot()
            
            return screenshot
        except Exception as e:
            print(f"Lỗi khi chụp màn hình: {e}")
            return None
    
    def start_continuous_capture(self, interval: float = 1.0):
        """
        Bắt đầu chụp màn hình liên tục
        
        Args:
            interval: Khoảng thời gian giữa các lần chụp (giây)
        """
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(
            target=self._capture_loop, 
            args=(interval,),
            daemon=True
        )
        self.capture_thread.start()
    
    def stop_continuous_capture(self):
        """
        Dừng chụp màn hình liên tục
        """
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
    
    def _capture_loop(self, interval: float):
        """
        Vòng lặp chụp màn hình liên tục
        """
        while self.is_capturing:
            screenshot = self.capture_screenshot()
            if screenshot:
                try:
                    # Thêm ảnh vào queue, bỏ qua nếu queue đầy
                    self.image_queue.put_nowait((screenshot, time.time()))
                except queue.Full:
                    # Bỏ ảnh cũ nhất nếu queue đầy
                    try:
                        self.image_queue.get_nowait()
                        self.image_queue.put_nowait((screenshot, time.time()))
                    except queue.Empty:
                        pass
            
            time.sleep(interval)
    
    def get_latest_screenshot(self) -> Optional[Tuple[Image.Image, float]]:
        """
        Lấy ảnh chụp màn hình mới nhất
        
        Returns:
            Tuple (image, timestamp) nếu có, None nếu không
        """
        try:
            return self.image_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Lấy kích thước màn hình
        
        Returns:
            Tuple (width, height)
        """
        return pyautogui.size()
    
    def save_screenshot(self, filepath: str) -> bool:
        """
        Lưu ảnh chụp màn hình hiện tại
        
        Args:
            filepath: Đường dẫn file để lưu
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            screenshot = self.capture_screenshot()
            if screenshot:
                screenshot.save(filepath)
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi lưu ảnh: {e}")
            return False

