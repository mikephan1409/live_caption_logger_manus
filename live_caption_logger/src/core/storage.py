# Module lưu trữ cho Live Caption Logger

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import shutil

class StorageManager:
    """
    Lớp quản lý lưu trữ dữ liệu transcript
    """
    
    def __init__(self, db_path: str):
        """
        Khởi tạo storage manager
        
        Args:
            db_path: Đường dẫn đến file cơ sở dữ liệu
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """
        Khởi tạo cơ sở dữ liệu và tạo bảng
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Bảng sessions - lưu thông tin các phiên ghi chép
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bảng transcripts - lưu nội dung transcript
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    text_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    confidence REAL,
                    is_incremental BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            # Bảng exports - lưu thông tin các lần xuất file
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    format TEXT NOT NULL,
                    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            
            conn.commit()
    
    def create_session(self, title: str, metadata: Dict = None) -> int:
        """
        Tạo phiên ghi chép mới
        
        Args:
            title: Tiêu đề phiên
            metadata: Thông tin bổ sung
            
        Returns:
            ID của phiên được tạo
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
                INSERT INTO sessions (title, start_time, metadata)
                VALUES (?, ?, ?)
            ''', (title, datetime.now(), metadata_json))
            
            session_id = cursor.lastrowid
            conn.commit()
            
            return session_id
    
    def end_session(self, session_id: int):
        """
        Kết thúc phiên ghi chép
        
        Args:
            session_id: ID của phiên
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET end_time = ?, status = 'completed'
                WHERE id = ?
            ''', (datetime.now(), session_id))
            
            conn.commit()
    
    def save_transcript_entry(self, session_id: int, text_data: Dict):
        """
        Lưu một mục transcript
        
        Args:
            session_id: ID của phiên
            text_data: Dữ liệu văn bản từ text processor
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transcripts 
                (session_id, text_id, content, timestamp, confidence, is_incremental)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                text_data['id'],
                text_data['text'],
                text_data['timestamp'],
                text_data['confidence'],
                text_data['is_incremental']
            ))
            
            conn.commit()
    
    def get_session_transcript(self, session_id: int) -> List[Dict]:
        """
        Lấy transcript của một phiên
        
        Args:
            session_id: ID của phiên
            
        Returns:
            Danh sách các mục transcript
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT text_id, content, timestamp, confidence, is_incremental
                FROM transcripts
                WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            rows = cursor.fetchall()
            
            return [
                {
                    'text_id': row[0],
                    'content': row[1],
                    'timestamp': datetime.fromisoformat(row[2]),
                    'confidence': row[3],
                    'is_incremental': bool(row[4])
                }
                for row in rows
            ]
    
    def get_sessions(self, limit: int = 50) -> List[Dict]:
        """
        Lấy danh sách các phiên ghi chép
        
        Args:
            limit: Số lượng phiên tối đa
            
        Returns:
            Danh sách thông tin phiên
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, start_time, end_time, status, metadata
                FROM sessions
                ORDER BY start_time DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            sessions = []
            for row in rows:
                metadata = json.loads(row[5]) if row[5] else {}
                sessions.append({
                    'id': row[0],
                    'title': row[1],
                    'start_time': datetime.fromisoformat(row[2]),
                    'end_time': datetime.fromisoformat(row[3]) if row[3] else None,
                    'status': row[4],
                    'metadata': metadata
                })
            
            return sessions
    
    def export_session_to_text(self, session_id: int, file_path: str, include_timestamps: bool = True) -> bool:
        """
        Xuất phiên ra file text
        
        Args:
            session_id: ID của phiên
            file_path: Đường dẫn file xuất
            include_timestamps: Có bao gồm timestamp không
            
        Returns:
            True nếu thành công
        """
        try:
            transcript_entries = self.get_session_transcript(session_id)
            session_info = self.get_session_info(session_id)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"Transcript: {session_info['title']}\n")
                f.write(f"Thời gian bắt đầu: {session_info['start_time']}\n")
                if session_info['end_time']:
                    f.write(f"Thời gian kết thúc: {session_info['end_time']}\n")
                f.write("=" * 50 + "\n\n")
                
                # Content
                for entry in transcript_entries:
                    if include_timestamps:
                        f.write(f"[{entry['timestamp'].strftime('%H:%M:%S')}] ")
                    f.write(f"{entry['content']}\n")
                    if not entry['is_incremental']:
                        f.write("\n")  # Thêm dòng trống giữa các đoạn
            
            # Lưu thông tin export
            self.save_export_info(session_id, file_path, 'txt')
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi xuất file text: {e}")
            return False
    
    def export_session_to_markdown(self, session_id: int, file_path: str) -> bool:
        """
        Xuất phiên ra file Markdown
        
        Args:
            session_id: ID của phiên
            file_path: Đường dẫn file xuất
            
        Returns:
            True nếu thành công
        """
        try:
            transcript_entries = self.get_session_transcript(session_id)
            session_info = self.get_session_info(session_id)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"# {session_info['title']}\n\n")
                f.write(f"**Thời gian bắt đầu:** {session_info['start_time']}\n\n")
                if session_info['end_time']:
                    f.write(f"**Thời gian kết thúc:** {session_info['end_time']}\n\n")
                
                f.write("## Nội dung\n\n")
                
                # Content
                current_paragraph = []
                for entry in transcript_entries:
                    if entry['is_incremental']:
                        # Thay thế đoạn hiện tại
                        current_paragraph = [entry['content']]
                    else:
                        # Thêm vào đoạn hiện tại
                        current_paragraph.append(entry['content'])
                        
                        # Xuất đoạn khi gặp entry không incremental
                        if len(current_paragraph) > 1:
                            f.write(' '.join(current_paragraph) + "\n\n")
                            current_paragraph = []
                
                # Xuất đoạn cuối nếu còn
                if current_paragraph:
                    f.write(' '.join(current_paragraph) + "\n\n")
            
            # Lưu thông tin export
            self.save_export_info(session_id, file_path, 'md')
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi xuất file Markdown: {e}")
            return False
    
    def get_session_info(self, session_id: int) -> Optional[Dict]:
        """
        Lấy thông tin của một phiên
        
        Args:
            session_id: ID của phiên
            
        Returns:
            Thông tin phiên hoặc None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, start_time, end_time, status, metadata
                FROM sessions
                WHERE id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            
            if row:
                metadata = json.loads(row[5]) if row[5] else {}
                return {
                    'id': row[0],
                    'title': row[1],
                    'start_time': datetime.fromisoformat(row[2]),
                    'end_time': datetime.fromisoformat(row[3]) if row[3] else None,
                    'status': row[4],
                    'metadata': metadata
                }
            
            return None
    
    def save_export_info(self, session_id: int, file_path: str, format: str):
        """
        Lưu thông tin export
        
        Args:
            session_id: ID của phiên
            file_path: Đường dẫn file
            format: Định dạng file
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO exports (session_id, file_path, format)
                VALUES (?, ?, ?)
            ''', (session_id, file_path, format))
            
            conn.commit()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Sao lưu cơ sở dữ liệu
        
        Args:
            backup_path: Đường dẫn file sao lưu
            
        Returns:
            True nếu thành công
        """
        try:
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Lỗi khi sao lưu database: {e}")
            return False

