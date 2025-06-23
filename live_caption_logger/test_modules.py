#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script kiểm thử các module của Live Caption Logger
"""

import sys
import os
from pathlib import Path

# Thêm thư mục src vào Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_screen_capture():
    """Kiểm thử module chụp màn hình"""
    print("=== Kiểm thử Screen Capture ===")
    
    try:
        from core.screen_capture import ScreenCapture
        
        capture = ScreenCapture()
        print("✓ Khởi tạo ScreenCapture thành công")
        
        # Lấy kích thước màn hình
        screen_size = capture.get_screen_size()
        print(f"✓ Kích thước màn hình: {screen_size}")
        
        # Chụp ảnh màn hình
        screenshot = capture.capture_screenshot()
        if screenshot:
            print("✓ Chụp màn hình thành công")
            print(f"  Kích thước ảnh: {screenshot.size}")
        else:
            print("✗ Không thể chụp màn hình")
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_ocr_processor():
    """Kiểm thử module OCR"""
    print("\n=== Kiểm thử OCR Processor ===")
    
    try:
        from core.ocr_processor import OCRProcessor
        from PIL import Image, ImageDraw, ImageFont
        
        # Tạo ảnh test đơn giản
        img = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Vẽ text lên ảnh
        try:
            # Thử sử dụng font mặc định
            draw.text((10, 30), "Hello World Test", fill='black')
        except:
            draw.text((10, 30), "Hello World Test", fill='black')
        
        ocr = OCRProcessor()
        print("✓ Khởi tạo OCRProcessor thành công")
        
        # Kiểm thử OCR
        result = ocr.extract_text(img)
        print(f"✓ OCR kết quả: '{result['text']}'")
        print(f"  Độ tin cậy: {result['confidence']:.1f}%")
        
        # Kiểm thử ngôn ngữ có sẵn
        languages = ocr.get_available_languages()
        print(f"✓ Ngôn ngữ có sẵn: {languages[:5]}...")  # Hiển thị 5 ngôn ngữ đầu
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_text_processor():
    """Kiểm thử module xử lý văn bản"""
    print("\n=== Kiểm thử Text Processor ===")
    
    try:
        from core.text_processor import TextProcessor
        from datetime import datetime
        
        processor = TextProcessor()
        print("✓ Khởi tạo TextProcessor thành công")
        
        # Tạo dữ liệu OCR giả
        ocr_result = {
            'text': 'Hello this is a test message',
            'confidence': 85.5,
            'word_count': 6
        }
        
        # Xử lý văn bản
        processed = processor.process_new_text(ocr_result)
        if processed:
            print(f"✓ Xử lý văn bản thành công: '{processed['text']}'")
            print(f"  ID: {processed['id']}")
            print(f"  Timestamp: {processed['timestamp']}")
        else:
            print("✗ Không thể xử lý văn bản")
        
        # Kiểm thử tóm tắt phiên
        summary = processor.get_session_summary()
        print(f"✓ Tóm tắt phiên: {summary['word_count']} từ")
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_storage_manager():
    """Kiểm thử module lưu trữ"""
    print("\n=== Kiểm thử Storage Manager ===")
    
    try:
        from core.storage import StorageManager
        from datetime import datetime
        import tempfile
        
        # Tạo database tạm thời
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        storage = StorageManager(db_path)
        print("✓ Khởi tạo StorageManager thành công")
        
        # Tạo phiên test
        session_id = storage.create_session("Test Session", {"test": True})
        print(f"✓ Tạo phiên thành công, ID: {session_id}")
        
        # Lưu transcript entry
        text_data = {
            'id': 'test123',
            'text': 'This is a test transcript',
            'timestamp': datetime.now(),
            'confidence': 90.0,
            'is_incremental': False
        }
        
        storage.save_transcript_entry(session_id, text_data)
        print("✓ Lưu transcript entry thành công")
        
        # Lấy transcript
        transcript = storage.get_session_transcript(session_id)
        print(f"✓ Lấy transcript thành công: {len(transcript)} entries")
        
        # Kết thúc phiên
        storage.end_session(session_id)
        print("✓ Kết thúc phiên thành công")
        
        # Lấy danh sách phiên
        sessions = storage.get_sessions()
        print(f"✓ Lấy danh sách phiên: {len(sessions)} phiên")
        
        # Dọn dẹp
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        return False

def test_integration():
    """Kiểm thử tích hợp các module"""
    print("\n=== Kiểm thử tích hợp ===")
    
    try:
        from core.screen_capture import ScreenCapture
        from core.ocr_processor import OCRProcessor
        from core.text_processor import TextProcessor
        from core.storage import StorageManager
        from PIL import Image, ImageDraw
        import tempfile
        import time
        
        # Khởi tạo các module
        capture = ScreenCapture()
        ocr = OCRProcessor()
        text_processor = TextProcessor()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        storage = StorageManager(db_path)
        
        print("✓ Khởi tạo tất cả module thành công")
        
        # Tạo phiên
        session_id = storage.create_session("Integration Test")
        
        # Tạo ảnh test với văn bản
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), "Integration test message", fill='black')
        
        # Quy trình xử lý hoàn chỉnh
        ocr_result = ocr.extract_text(img)
        processed_text = text_processor.process_new_text(ocr_result)
        
        if processed_text:
            storage.save_transcript_entry(session_id, processed_text)
            print("✓ Quy trình tích hợp thành công")
            
            # Xuất file test
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
                export_path = tmp.name
            
            success = storage.export_session_to_text(session_id, export_path)
            if success:
                print("✓ Xuất file thành công")
                with open(export_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  Nội dung file: {len(content)} ký tự")
                os.unlink(export_path)
            else:
                print("✗ Không thể xuất file")
        else:
            print("✗ Không thể xử lý văn bản")
        
        # Dọn dẹp
        storage.end_session(session_id)
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"✗ Lỗi tích hợp: {e}")
        return False

def main():
    """Chạy tất cả các test"""
    print("Bắt đầu kiểm thử Live Caption Logger")
    print("=" * 50)
    
    tests = [
        test_screen_capture,
        test_ocr_processor,
        test_text_processor,
        test_storage_manager,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Kết quả: {passed}/{total} test thành công")
    
    if passed == total:
        print("🎉 Tất cả test đều PASS!")
        return True
    else:
        print("⚠️  Một số test FAIL!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

