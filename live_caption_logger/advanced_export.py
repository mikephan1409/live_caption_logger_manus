#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script nâng cao cho Live Caption Logger - thêm tính năng xuất nâng cao
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Thêm thư mục src vào Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def export_to_json(session_id, output_path):
    """Xuất phiên ra định dạng JSON"""
    
    try:
        from core.storage import StorageManager
        
        storage = StorageManager("demo_transcripts.db")
        session_info = storage.get_session_info(session_id)
        transcript_entries = storage.get_session_transcript(session_id)
        
        if not session_info:
            print(f"Không tìm thấy phiên với ID: {session_id}")
            return False
        
        # Tạo cấu trúc JSON
        json_data = {
            "session": {
                "id": session_info['id'],
                "title": session_info['title'],
                "start_time": session_info['start_time'].isoformat(),
                "end_time": session_info['end_time'].isoformat() if session_info['end_time'] else None,
                "status": session_info['status'],
                "metadata": session_info['metadata']
            },
            "transcript": [
                {
                    "text_id": entry['text_id'],
                    "content": entry['content'],
                    "timestamp": entry['timestamp'].isoformat(),
                    "confidence": entry['confidence'],
                    "is_incremental": entry['is_incremental']
                }
                for entry in transcript_entries
            ],
            "statistics": {
                "total_entries": len(transcript_entries),
                "total_words": sum(len(entry['content'].split()) for entry in transcript_entries),
                "total_characters": sum(len(entry['content']) for entry in transcript_entries),
                "average_confidence": sum(entry['confidence'] for entry in transcript_entries) / len(transcript_entries) if transcript_entries else 0,
                "duration_seconds": (session_info['end_time'] - session_info['start_time']).total_seconds() if session_info['end_time'] else None
            },
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "format": "json",
                "version": "1.0"
            }
        }
        
        # Ghi file JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Xuất JSON thành công: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Lỗi khi xuất JSON: {e}")
        return False

def export_to_csv(session_id, output_path):
    """Xuất phiên ra định dạng CSV"""
    
    try:
        from core.storage import StorageManager
        import csv
        
        storage = StorageManager("demo_transcripts.db")
        session_info = storage.get_session_info(session_id)
        transcript_entries = storage.get_session_transcript(session_id)
        
        if not session_info:
            print(f"Không tìm thấy phiên với ID: {session_id}")
            return False
        
        # Ghi file CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Text ID', 'Timestamp', 'Content', 'Confidence', 'Is Incremental', 'Word Count'
            ])
            
            # Data
            for entry in transcript_entries:
                writer.writerow([
                    entry['text_id'],
                    entry['timestamp'].isoformat(),
                    entry['content'],
                    entry['confidence'],
                    entry['is_incremental'],
                    len(entry['content'].split())
                ])
        
        print(f"✓ Xuất CSV thành công: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Lỗi khi xuất CSV: {e}")
        return False

def export_to_srt(session_id, output_path):
    """Xuất phiên ra định dạng SRT (subtitle)"""
    
    try:
        from core.storage import StorageManager
        
        storage = StorageManager("demo_transcripts.db")
        session_info = storage.get_session_info(session_id)
        transcript_entries = storage.get_session_transcript(session_id)
        
        if not session_info:
            print(f"Không tìm thấy phiên với ID: {session_id}")
            return False
        
        # Ghi file SRT
        with open(output_path, 'w', encoding='utf-8') as f:
            start_time = session_info['start_time']
            
            for i, entry in enumerate(transcript_entries, 1):
                # Tính thời gian relative
                entry_time = entry['timestamp']
                relative_seconds = (entry_time - start_time).total_seconds()
                
                # Chuyển đổi sang định dạng SRT time
                hours = int(relative_seconds // 3600)
                minutes = int((relative_seconds % 3600) // 60)
                seconds = int(relative_seconds % 60)
                milliseconds = int((relative_seconds % 1) * 1000)
                
                start_srt = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
                
                # Thời gian kết thúc (giả sử mỗi entry kéo dài 3 giây)
                end_seconds = relative_seconds + 3
                end_hours = int(end_seconds // 3600)
                end_minutes = int((end_seconds % 3600) // 60)
                end_secs = int(end_seconds % 60)
                end_ms = int((end_seconds % 1) * 1000)
                
                end_srt = f"{end_hours:02d}:{end_minutes:02d}:{end_secs:02d},{end_ms:03d}"
                
                # Ghi entry SRT
                f.write(f"{i}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                f.write(f"{entry['content']}\n\n")
        
        print(f"✓ Xuất SRT thành công: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Lỗi khi xuất SRT: {e}")
        return False

def create_summary_report(session_id, output_path):
    """Tạo báo cáo tóm tắt chi tiết"""
    
    try:
        from core.storage import StorageManager
        
        storage = StorageManager("demo_transcripts.db")
        session_info = storage.get_session_info(session_id)
        transcript_entries = storage.get_session_transcript(session_id)
        
        if not session_info:
            print(f"Không tìm thấy phiên với ID: {session_id}")
            return False
        
        # Tính toán thống kê
        total_words = sum(len(entry['content'].split()) for entry in transcript_entries)
        total_chars = sum(len(entry['content']) for entry in transcript_entries)
        avg_confidence = sum(entry['confidence'] for entry in transcript_entries) / len(transcript_entries) if transcript_entries else 0
        
        duration = None
        if session_info['end_time']:
            duration = session_info['end_time'] - session_info['start_time']
        
        # Phân tích từ khóa (đơn giản)
        all_words = []
        for entry in transcript_entries:
            words = entry['content'].lower().split()
            all_words.extend(words)
        
        # Đếm từ
        word_count = {}
        for word in all_words:
            # Loại bỏ dấu câu
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 3:  # Chỉ đếm từ dài hơn 3 ký tự
                word_count[clean_word] = word_count.get(clean_word, 0) + 1
        
        # Top 10 từ phổ biến
        top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Tạo báo cáo Markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Báo cáo tóm tắt phiên ghi chép\n\n")
            f.write(f"## Thông tin phiên\n\n")
            f.write(f"- **Tiêu đề:** {session_info['title']}\n")
            f.write(f"- **ID phiên:** {session_info['id']}\n")
            f.write(f"- **Thời gian bắt đầu:** {session_info['start_time']}\n")
            if session_info['end_time']:
                f.write(f"- **Thời gian kết thúc:** {session_info['end_time']}\n")
                f.write(f"- **Thời lượng:** {duration}\n")
            f.write(f"- **Trạng thái:** {session_info['status']}\n\n")
            
            f.write(f"## Thống kê nội dung\n\n")
            f.write(f"- **Tổng số dòng transcript:** {len(transcript_entries)}\n")
            f.write(f"- **Tổng số từ:** {total_words:,}\n")
            f.write(f"- **Tổng số ký tự:** {total_chars:,}\n")
            f.write(f"- **Độ tin cậy trung bình:** {avg_confidence:.1f}%\n")
            
            if duration:
                words_per_minute = (total_words / duration.total_seconds()) * 60
                f.write(f"- **Tốc độ nói:** {words_per_minute:.1f} từ/phút\n")
            
            f.write(f"\n## Từ khóa phổ biến\n\n")
            for i, (word, count) in enumerate(top_words, 1):
                f.write(f"{i}. **{word}** - {count} lần\n")
            
            f.write(f"\n## Chi tiết độ tin cậy\n\n")
            confidence_ranges = {
                "Rất cao (90-100%)": 0,
                "Cao (80-89%)": 0,
                "Trung bình (70-79%)": 0,
                "Thấp (<70%)": 0
            }
            
            for entry in transcript_entries:
                conf = entry['confidence']
                if conf >= 90:
                    confidence_ranges["Rất cao (90-100%)"] += 1
                elif conf >= 80:
                    confidence_ranges["Cao (80-89%)"] += 1
                elif conf >= 70:
                    confidence_ranges["Trung bình (70-79%)"] += 1
                else:
                    confidence_ranges["Thấp (<70%)"] += 1
            
            for range_name, count in confidence_ranges.items():
                percentage = (count / len(transcript_entries)) * 100 if transcript_entries else 0
                f.write(f"- **{range_name}:** {count} dòng ({percentage:.1f}%)\n")
            
            f.write(f"\n## Nội dung đầy đủ\n\n")
            for entry in transcript_entries:
                timestamp_str = entry['timestamp'].strftime('%H:%M:%S')
                f.write(f"**[{timestamp_str}]** {entry['content']}\n\n")
            
            f.write(f"\n---\n")
            f.write(f"*Báo cáo được tạo bởi Live Caption Logger vào {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        print(f"✓ Tạo báo cáo tóm tắt thành công: {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Lỗi khi tạo báo cáo: {e}")
        return False

def main():
    """Menu chính cho xuất nâng cao"""
    
    try:
        from core.storage import StorageManager
        
        # Kiểm tra database
        if not os.path.exists("demo_transcripts.db"):
            print("❌ Không tìm thấy database demo. Chạy demo.py trước để tạo dữ liệu.")
            return
        
        storage = StorageManager("demo_transcripts.db")
        sessions = storage.get_sessions()
        
        if not sessions:
            print("❌ Không có phiên nào trong database.")
            return
        
        while True:
            print("\n" + "=" * 60)
            print("📊 Live Caption Logger - Xuất nâng cao")
            print("=" * 60)
            
            # Hiển thị danh sách phiên
            print("Danh sách phiên:")
            for i, session in enumerate(sessions, 1):
                print(f"  {i}. {session['title']} (ID: {session['id']})")
            
            print("\nTùy chọn xuất:")
            print("1. Xuất JSON")
            print("2. Xuất CSV")
            print("3. Xuất SRT (Subtitle)")
            print("4. Tạo báo cáo tóm tắt")
            print("5. Xuất tất cả định dạng")
            print("6. Thoát")
            print("-" * 60)
            
            choice = input("Chọn tùy chọn (1-6): ").strip()
            
            if choice == '6':
                print("👋 Tạm biệt!")
                break
            
            if choice not in ['1', '2', '3', '4', '5']:
                print("❌ Lựa chọn không hợp lệ!")
                continue
            
            # Chọn phiên
            try:
                session_choice = input(f"Chọn phiên (1-{len(sessions)}): ").strip()
                session_index = int(session_choice) - 1
                
                if session_index < 0 or session_index >= len(sessions):
                    print("❌ Số phiên không hợp lệ!")
                    continue
                
                selected_session = sessions[session_index]
                session_id = selected_session['id']
                session_title = selected_session['title']
                
                # Tạo tên file base
                safe_title = "".join(c for c in session_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = f"{safe_title}_{timestamp}"
                
                print(f"\n📝 Đang xuất phiên: {session_title}")
                
                if choice == '1':  # JSON
                    output_path = f"{base_name}.json"
                    export_to_json(session_id, output_path)
                
                elif choice == '2':  # CSV
                    output_path = f"{base_name}.csv"
                    export_to_csv(session_id, output_path)
                
                elif choice == '3':  # SRT
                    output_path = f"{base_name}.srt"
                    export_to_srt(session_id, output_path)
                
                elif choice == '4':  # Báo cáo
                    output_path = f"{base_name}_report.md"
                    create_summary_report(session_id, output_path)
                
                elif choice == '5':  # Tất cả
                    print("📦 Đang xuất tất cả định dạng...")
                    export_to_json(session_id, f"{base_name}.json")
                    export_to_csv(session_id, f"{base_name}.csv")
                    export_to_srt(session_id, f"{base_name}.srt")
                    create_summary_report(session_id, f"{base_name}_report.md")
                    
                    # Xuất định dạng có sẵn
                    storage.export_session_to_text(session_id, f"{base_name}.txt")
                    storage.export_session_to_markdown(session_id, f"{base_name}.md")
                    
                    print("🎉 Đã xuất tất cả định dạng!")
                
            except ValueError:
                print("❌ Vui lòng nhập số hợp lệ!")
            except Exception as e:
                print(f"❌ Lỗi: {e}")
    
    except Exception as e:
        print(f"❌ Lỗi chung: {e}")

if __name__ == "__main__":
    main()

