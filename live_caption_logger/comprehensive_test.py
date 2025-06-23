#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script kiểm thử toàn diện cho Live Caption Logger
"""

import sys
import os
from pathlib import Path
import time
import tempfile
import shutil

# Thêm thư mục src vào Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_performance():
    """Kiểm thử hiệu suất của các module"""
    print("\n🚀 Kiểm thử hiệu suất")
    print("-" * 40)
    
    try:
        from core.screen_capture import ScreenCapture
        from core.ocr_processor import OCRProcessor
        from core.text_processor import TextProcessor
        from core.storage import StorageManager
        from PIL import Image, ImageDraw
        import time
        
        # Tạo database tạm thời
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        # Khởi tạo modules
        ocr = OCRProcessor()
        text_processor = TextProcessor()
        storage = StorageManager(db_path)
        
        # Tạo phiên test
        session_id = storage.create_session("Performance Test")
        
        # Test OCR performance
        print("📊 Kiểm thử hiệu suất OCR...")
        
        # Tạo nhiều ảnh test
        test_images = []
        test_texts = [
            "This is a performance test",
            "Testing OCR speed and accuracy",
            "Live Caption Logger performance",
            "Multiple text processing test",
            "Final performance evaluation"
        ]
        
        for text in test_texts:
            img = Image.new('RGB', (400, 60), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((10, 20), text, fill='black')
            test_images.append(img)
        
        # Đo thời gian OCR
        start_time = time.time()
        ocr_results = []
        
        for img in test_images:
            result = ocr.extract_text(img)
            ocr_results.append(result)
        
        ocr_time = time.time() - start_time
        print(f"  ✓ OCR {len(test_images)} ảnh: {ocr_time:.2f}s ({ocr_time/len(test_images):.3f}s/ảnh)")
        
        # Test text processing performance
        print("📊 Kiểm thử hiệu suất xử lý văn bản...")
        
        start_time = time.time()
        processed_texts = []
        
        for result in ocr_results:
            processed = text_processor.process_new_text(result)
            if processed:
                processed_texts.append(processed)
        
        text_processing_time = time.time() - start_time
        print(f"  ✓ Xử lý {len(ocr_results)} văn bản: {text_processing_time:.2f}s ({text_processing_time/len(ocr_results):.3f}s/văn bản)")
        
        # Test storage performance
        print("📊 Kiểm thử hiệu suất lưu trữ...")
        
        start_time = time.time()
        
        for text_data in processed_texts:
            storage.save_transcript_entry(session_id, text_data)
        
        storage_time = time.time() - start_time
        print(f"  ✓ Lưu {len(processed_texts)} entries: {storage_time:.2f}s ({storage_time/len(processed_texts):.3f}s/entry)")
        
        # Test export performance
        print("📊 Kiểm thử hiệu suất xuất file...")
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            export_path = tmp.name
        
        start_time = time.time()
        storage.export_session_to_text(session_id, export_path)
        export_time = time.time() - start_time
        
        print(f"  ✓ Xuất file: {export_time:.2f}s")
        
        # Tổng kết
        total_time = ocr_time + text_processing_time + storage_time + export_time
        print(f"\n📈 Tổng thời gian: {total_time:.2f}s")
        print(f"📈 Throughput: {len(test_images)/total_time:.1f} ảnh/giây")
        
        # Dọn dẹp
        storage.end_session(session_id)
        os.unlink(db_path)
        os.unlink(export_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm thử hiệu suất: {e}")
        return False

def test_stress():
    """Kiểm thử tải nặng"""
    print("\n💪 Kiểm thử tải nặng")
    print("-" * 40)
    
    try:
        from core.text_processor import TextProcessor
        from core.storage import StorageManager
        import random
        import string
        
        # Tạo database tạm thời
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        text_processor = TextProcessor()
        storage = StorageManager(db_path)
        
        # Tạo phiên test
        session_id = storage.create_session("Stress Test")
        
        # Tạo nhiều văn bản ngẫu nhiên
        num_texts = 100
        print(f"📊 Tạo và xử lý {num_texts} văn bản ngẫu nhiên...")
        
        start_time = time.time()
        processed_count = 0
        
        for i in range(num_texts):
            # Tạo văn bản ngẫu nhiên
            words = []
            for _ in range(random.randint(5, 20)):
                word_length = random.randint(3, 10)
                word = ''.join(random.choices(string.ascii_lowercase, k=word_length))
                words.append(word)
            
            text = ' '.join(words)
            
            # Tạo OCR result giả
            ocr_result = {
                'text': text,
                'confidence': random.uniform(70, 100),
                'word_count': len(words)
            }
            
            # Xử lý
            processed = text_processor.process_new_text(ocr_result)
            if processed:
                storage.save_transcript_entry(session_id, processed)
                processed_count += 1
            
            # In tiến độ
            if (i + 1) % 20 == 0:
                print(f"  Đã xử lý: {i + 1}/{num_texts}")
        
        total_time = time.time() - start_time
        
        print(f"✓ Hoàn thành: {processed_count}/{num_texts} văn bản được xử lý")
        print(f"✓ Thời gian: {total_time:.2f}s")
        print(f"✓ Tốc độ: {processed_count/total_time:.1f} văn bản/giây")
        
        # Kiểm tra database
        transcript = storage.get_session_transcript(session_id)
        print(f"✓ Database: {len(transcript)} entries được lưu")
        
        # Test xuất file lớn
        print("📊 Kiểm thử xuất file lớn...")
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            export_path = tmp.name
        
        start_time = time.time()
        success = storage.export_session_to_text(session_id, export_path)
        export_time = time.time() - start_time
        
        if success:
            file_size = os.path.getsize(export_path)
            print(f"✓ Xuất file: {export_time:.2f}s, kích thước: {file_size:,} bytes")
        else:
            print("❌ Không thể xuất file")
        
        # Dọn dẹp
        storage.end_session(session_id)
        os.unlink(db_path)
        if os.path.exists(export_path):
            os.unlink(export_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm thử tải nặng: {e}")
        return False

def test_edge_cases():
    """Kiểm thử các trường hợp biên"""
    print("\n🔍 Kiểm thử các trường hợp biên")
    print("-" * 40)
    
    try:
        from core.text_processor import TextProcessor
        from core.ocr_processor import OCRProcessor
        from PIL import Image
        
        text_processor = TextProcessor()
        ocr = OCRProcessor()
        
        # Test 1: Văn bản rỗng
        print("📊 Test 1: Văn bản rỗng")
        ocr_result = {'text': '', 'confidence': 0, 'word_count': 0}
        result = text_processor.process_new_text(ocr_result)
        print(f"  ✓ Kết quả: {result is None}")
        
        # Test 2: Văn bản quá ngắn
        print("📊 Test 2: Văn bản quá ngắn")
        ocr_result = {'text': 'hi', 'confidence': 90, 'word_count': 1}
        result = text_processor.process_new_text(ocr_result)
        print(f"  ✓ Kết quả: {result is None}")
        
        # Test 3: Độ tin cậy thấp
        print("📊 Test 3: Độ tin cậy thấp")
        ocr_result = {'text': 'this is a test', 'confidence': 20, 'word_count': 4}
        result = text_processor.process_new_text(ocr_result)
        print(f"  ✓ Kết quả: {result is None}")
        
        # Test 4: Văn bản có ký tự đặc biệt
        print("📊 Test 4: Văn bản có ký tự đặc biệt")
        ocr_result = {'text': 'Hello @#$%^&*() World!!!', 'confidence': 85, 'word_count': 3}
        result = text_processor.process_new_text(ocr_result)
        print(f"  ✓ Kết quả: {result is not None}")
        if result:
            print(f"    Văn bản đã làm sạch: '{result['text']}'")
        
        # Test 5: Văn bản trùng lặp
        print("📊 Test 5: Văn bản trùng lặp")
        ocr_result = {'text': 'This is a duplicate test', 'confidence': 90, 'word_count': 5}
        result1 = text_processor.process_new_text(ocr_result)
        result2 = text_processor.process_new_text(ocr_result)  # Trùng lặp
        print(f"  ✓ Lần 1: {result1 is not None}")
        print(f"  ✓ Lần 2 (trùng lặp): {result2 is None}")
        
        # Test 6: Ảnh trống
        print("📊 Test 6: OCR ảnh trống")
        empty_img = Image.new('RGB', (100, 100), color='white')
        ocr_result = ocr.extract_text(empty_img)
        print(f"  ✓ OCR ảnh trống: confidence = {ocr_result['confidence']}")
        
        # Test 7: Ảnh quá nhỏ
        print("📊 Test 7: OCR ảnh quá nhỏ")
        tiny_img = Image.new('RGB', (10, 10), color='white')
        ocr_result = ocr.extract_text(tiny_img)
        print(f"  ✓ OCR ảnh nhỏ: confidence = {ocr_result['confidence']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm thử trường hợp biên: {e}")
        return False

def test_memory_usage():
    """Kiểm thử sử dụng bộ nhớ"""
    print("\n🧠 Kiểm thử sử dụng bộ nhớ")
    print("-" * 40)
    
    try:
        import psutil
        import gc
        
        # Lấy thông tin bộ nhớ ban đầu
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Bộ nhớ ban đầu: {initial_memory:.1f} MB")
        
        # Chạy test tải nặng
        from core.text_processor import TextProcessor
        from core.storage import StorageManager
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        text_processor = TextProcessor()
        storage = StorageManager(db_path)
        session_id = storage.create_session("Memory Test")
        
        # Tạo nhiều dữ liệu
        for i in range(50):
            ocr_result = {
                'text': f'Memory test iteration {i} with some additional text to increase memory usage',
                'confidence': 85.0,
                'word_count': 12
            }
            
            processed = text_processor.process_new_text(ocr_result)
            if processed:
                storage.save_transcript_entry(session_id, processed)
        
        # Kiểm tra bộ nhớ sau khi xử lý
        after_processing = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 Bộ nhớ sau xử lý: {after_processing:.1f} MB")
        print(f"📊 Tăng thêm: {after_processing - initial_memory:.1f} MB")
        
        # Dọn dẹp và garbage collection
        storage.end_session(session_id)
        del storage
        del text_processor
        gc.collect()
        
        # Kiểm tra bộ nhớ sau dọn dẹp
        after_cleanup = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 Bộ nhớ sau dọn dẹp: {after_cleanup:.1f} MB")
        
        # Dọn dẹp file
        os.unlink(db_path)
        
        return True
        
    except ImportError:
        print("⚠️  psutil không có sẵn, bỏ qua test bộ nhớ")
        return True
    except Exception as e:
        print(f"❌ Lỗi kiểm thử bộ nhớ: {e}")
        return False

def run_comprehensive_tests():
    """Chạy tất cả các test toàn diện"""
    print("🧪 Bắt đầu kiểm thử toàn diện Live Caption Logger")
    print("=" * 60)
    
    tests = [
        ("Hiệu suất", test_performance),
        ("Tải nặng", test_stress),
        ("Trường hợp biên", test_edge_cases),
        ("Sử dụng bộ nhớ", test_memory_usage)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Đang chạy test: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASS")
                passed += 1
            else:
                print(f"❌ {test_name}: FAIL")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Kết quả tổng thể: {passed}/{total} tests PASS")
    
    if passed == total:
        print("🎉 Tất cả tests đều thành công!")
        print("✅ Ứng dụng sẵn sàng để triển khai")
    else:
        print("⚠️  Một số tests thất bại")
        print("🔧 Cần xem xét và sửa chữa")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)

