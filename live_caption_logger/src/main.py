# File chính để chạy ứng dụng Live Caption Logger

import sys
import os
from pathlib import Path

# Thêm thư mục src vào Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from ui.main_window import MainWindow
    
    def main():
        """
        Hàm chính để khởi chạy ứng dụng
        """
        print("Khởi động Live Caption Logger...")
        print("Đang kiểm tra các dependencies...")
        
        # Kiểm tra các thư viện cần thiết
        try:
            import tkinter
            print("✓ Tkinter có sẵn")
        except ImportError:
            print("✗ Lỗi: Tkinter không có sẵn")
            return
        
        try:
            import PIL
            print("✓ Pillow có sẵn")
        except ImportError:
            print("✗ Lỗi: Pillow chưa được cài đặt")
            print("Chạy: pip install Pillow")
            return
        
        try:
            import cv2
            print("✓ OpenCV có sẵn")
        except ImportError:
            print("✗ Lỗi: OpenCV chưa được cài đặt")
            print("Chạy: pip install opencv-python")
            return
        
        try:
            import pyautogui
            print("✓ PyAutoGUI có sẵn")
        except ImportError:
            print("✗ Lỗi: PyAutoGUI chưa được cài đặt")
            print("Chạy: pip install pyautogui")
            return
        
        try:
            import pytesseract
            print("✓ PyTesseract có sẵn")
        except ImportError:
            print("✗ Lỗi: PyTesseract chưa được cài đặt")
            print("Chạy: pip install pytesseract")
            return
        
        # Kiểm tra Tesseract OCR
        try:
            pytesseract.get_tesseract_version()
            print("✓ Tesseract OCR có sẵn")
        except Exception:
            print("⚠ Cảnh báo: Tesseract OCR chưa được cài đặt hoặc không tìm thấy")
            print("Vui lòng cài đặt Tesseract OCR:")
            print("- Windows: Tải từ https://github.com/UB-Mannheim/tesseract/wiki")
            print("- Ubuntu: sudo apt install tesseract-ocr")
            print("- macOS: brew install tesseract")
        
        print("\nKhởi động giao diện...")
        
        # Tạo và chạy ứng dụng
        app = MainWindow()
        app.run()
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Lỗi import: {e}")
    print("Vui lòng đảm bảo tất cả dependencies đã được cài đặt:")
    print("pip install -r requirements.txt")

