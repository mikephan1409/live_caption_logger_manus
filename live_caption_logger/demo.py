#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demo script cho Live Caption Logger - chạy mà không cần GUI
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Thêm thư mục src vào Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def create_demo_session():
    """Tạo một phiên demo với dữ liệu mẫu"""
    
    try:
        from core.text_processor import TextProcessor
        from core.storage import StorageManager
        from core.ocr_processor import OCRProcessor
        from PIL import Image, ImageDraw, ImageFont
        
        print("🚀 Bắt đầu demo Live Caption Logger")
        print("=" * 50)
        
        # Khởi tạo các module
        text_processor = TextProcessor()
        storage = StorageManager("demo_transcripts.db")
        ocr = OCRProcessor()
        
        print("✓ Khởi tạo các module thành công")
        
        # Tạo phiên demo
        session_title = f"Demo Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        session_id = storage.create_session(session_title, {
            "demo": True,
            "created_by": "Live Caption Logger Demo"
        })
        
        print(f"✓ Tạo phiên demo: {session_title}")
        print(f"  Session ID: {session_id}")
        
        # Dữ liệu văn bản mẫu (giả lập Live Caption)
        sample_texts = [
            "Xin chào và chào mừng đến với cuộc họp hôm nay",
            "Chúng ta sẽ thảo luận về dự án Live Caption Logger",
            "Đây là một ứng dụng giúp ghi lại và lưu trữ bản ghi từ Live Caption",
            "Ứng dụng sử dụng công nghệ OCR để đọc văn bản từ màn hình",
            "Sau đó xử lý và lưu trữ vào cơ sở dữ liệu",
            "Người dùng có thể xuất transcript ra nhiều định dạng khác nhau",
            "Cảm ơn mọi người đã tham gia cuộc họp",
            "Hẹn gặp lại trong cuộc họp tiếp theo"
        ]
        
        print("\n📝 Đang mô phỏng quá trình ghi chép...")
        
        # Mô phỏng quá trình ghi chép
        for i, text in enumerate(sample_texts, 1):
            # Tạo dữ liệu OCR giả
            ocr_result = {
                'text': text,
                'confidence': 85.0 + (i * 2),  # Độ tin cậy tăng dần
                'word_count': len(text.split())
            }
            
            # Xử lý văn bản
            processed_text = text_processor.process_new_text(ocr_result)
            
            if processed_text:
                # Lưu vào database
                storage.save_transcript_entry(session_id, processed_text)
                
                print(f"  [{i:2d}] {text}")
                print(f"       Độ tin cậy: {processed_text['confidence']:.1f}%")
            
            # Nghỉ một chút để mô phỏng thời gian thực
            time.sleep(0.5)
        
        # Kết thúc phiên
        storage.end_session(session_id)
        print("\n✓ Kết thúc phiên ghi chép")
        
        # Hiển thị thống kê
        session_info = storage.get_session_info(session_id)
        transcript_entries = storage.get_session_transcript(session_id)
        
        print(f"\n📊 Thống kê phiên:")
        print(f"  Tiêu đề: {session_info['title']}")
        print(f"  Thời gian bắt đầu: {session_info['start_time']}")
        print(f"  Thời gian kết thúc: {session_info['end_time']}")
        print(f"  Số dòng transcript: {len(transcript_entries)}")
        
        total_words = sum(len(entry['content'].split()) for entry in transcript_entries)
        total_chars = sum(len(entry['content']) for entry in transcript_entries)
        avg_confidence = sum(entry['confidence'] for entry in transcript_entries) / len(transcript_entries)
        
        print(f"  Tổng số từ: {total_words}")
        print(f"  Tổng số ký tự: {total_chars}")
        print(f"  Độ tin cậy trung bình: {avg_confidence:.1f}%")
        
        # Xuất file demo
        print(f"\n💾 Xuất file demo...")
        
        # Xuất Text
        txt_path = f"demo_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        if storage.export_session_to_text(session_id, txt_path):
            print(f"✓ Xuất file Text: {txt_path}")
        
        # Xuất Markdown
        md_path = f"demo_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        if storage.export_session_to_markdown(session_id, md_path):
            print(f"✓ Xuất file Markdown: {md_path}")
        
        print(f"\n🎉 Demo hoàn thành!")
        print(f"📁 Database được lưu tại: demo_transcripts.db")
        print(f"📄 Các file transcript đã được tạo")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_existing_sessions():
    """Hiển thị các phiên đã có trong database"""
    
    try:
        from core.storage import StorageManager
        
        if not os.path.exists("demo_transcripts.db"):
            print("Chưa có database demo. Chạy demo trước để tạo dữ liệu.")
            return
        
        storage = StorageManager("demo_transcripts.db")
        sessions = storage.get_sessions()
        
        if not sessions:
            print("Không có phiên nào trong database.")
            return
        
        print(f"\n📋 Danh sách phiên ({len(sessions)} phiên):")
        print("-" * 80)
        
        for session in sessions:
            print(f"ID: {session['id']}")
            print(f"Tiêu đề: {session['title']}")
            print(f"Bắt đầu: {session['start_time']}")
            if session['end_time']:
                print(f"Kết thúc: {session['end_time']}")
            print(f"Trạng thái: {session['status']}")
            print("-" * 40)
        
    except Exception as e:
        print(f"Lỗi khi hiển thị phiên: {e}")

def main():
    """Menu chính của demo"""
    
    while True:
        print("\n" + "=" * 50)
        print("🎯 Live Caption Logger Demo")
        print("=" * 50)
        print("1. Tạo phiên demo mới")
        print("2. Xem các phiên đã có")
        print("3. Thoát")
        print("-" * 50)
        
        choice = input("Chọn tùy chọn (1-3): ").strip()
        
        if choice == '1':
            create_demo_session()
        elif choice == '2':
            show_existing_sessions()
        elif choice == '3':
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()

