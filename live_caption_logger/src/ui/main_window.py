# Giao diện chính cho Live Caption Logger

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Thêm đường dẫn src vào Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.screen_capture import ScreenCapture
from core.ocr_processor import OCRProcessor
from core.text_processor import TextProcessor
from core.storage import StorageManager
from utils.config import *

class MainWindow:
    """
    Giao diện chính của ứng dụng Live Caption Logger
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(UI_CONFIG['window_title'])
        self.root.geometry(f"{UI_CONFIG['window_size'][0]}x{UI_CONFIG['window_size'][1]}")
        
        # Khởi tạo các module
        self.screen_capture = ScreenCapture()
        self.ocr_processor = OCRProcessor(**OCR_CONFIG)
        self.text_processor = TextProcessor(**TEXT_PROCESSING_CONFIG)
        self.storage_manager = StorageManager(str(DATABASE_CONFIG['path']))
        
        # Biến trạng thái
        self.is_recording = False
        self.current_session_id = None
        self.processing_thread = None
        
        # Tạo giao diện
        self.create_widgets()
        self.setup_layout()
        
        # Bind sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """
        Tạo các widget cho giao diện
        """
        # Frame chính
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Frame điều khiển
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Điều khiển", padding="10")
        
        # Nút bắt đầu/dừng
        self.start_stop_btn = ttk.Button(
            self.control_frame, 
            text="Bắt đầu ghi", 
            command=self.toggle_recording
        )
        
        # Entry tiêu đề phiên
        ttk.Label(self.control_frame, text="Tiêu đề phiên:").grid(row=0, column=0, sticky="w", pady=5)
        self.session_title_var = tk.StringVar(value=f"Phiên ghi {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        self.session_title_entry = ttk.Entry(
            self.control_frame, 
            textvariable=self.session_title_var,
            width=40
        )
        
        # Frame cấu hình vùng chụp
        self.region_frame = ttk.LabelFrame(self.main_frame, text="Vùng chụp màn hình", padding="10")
        
        # Nút chọn vùng
        self.select_region_btn = ttk.Button(
            self.region_frame,
            text="Chọn vùng Live Caption",
            command=self.select_capture_region
        )
        
        # Hiển thị vùng hiện tại
        self.region_info_var = tk.StringVar(value="Chưa chọn vùng")\n        self.region_info_label = ttk.Label(self.region_frame, textvariable=self.region_info_var)
        
        # Nút tự động phát hiện
        self.auto_detect_btn = ttk.Button(
            self.region_frame,
            text="Tự động phát hiện",
            command=self.auto_detect_region
        )
        
        # Frame hiển thị văn bản
        self.text_frame = ttk.LabelFrame(self.main_frame, text="Văn bản Live Caption", padding="10")
        
        # Text widget để hiển thị văn bản
        self.text_display = tk.Text(
            self.text_frame,
            height=15,
            width=70,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        
        # Scrollbar cho text widget
        self.text_scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=self.text_scrollbar.set)
        
        # Frame thống kê
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Thống kê", padding="10")
        
        # Labels thống kê
        self.stats_labels = {
            'session_time': ttk.Label(self.stats_frame, text="Thời gian: 00:00:00"),
            'word_count': ttk.Label(self.stats_frame, text="Số từ: 0"),
            'confidence': ttk.Label(self.stats_frame, text="Độ tin cậy: 0%")
        }
        
        # Frame xuất file
        self.export_frame = ttk.LabelFrame(self.main_frame, text="Xuất file", padding="10")
        
        # Nút xuất
        self.export_txt_btn = ttk.Button(
            self.export_frame,
            text="Xuất Text",
            command=lambda: self.export_session('txt')
        )
        
        self.export_md_btn = ttk.Button(
            self.export_frame,
            text="Xuất Markdown",
            command=lambda: self.export_session('md')
        )
        
        # Frame danh sách phiên
        self.sessions_frame = ttk.LabelFrame(self.main_frame, text="Phiên đã ghi", padding="10")
        
        # Treeview để hiển thị danh sách phiên
        self.sessions_tree = ttk.Treeview(
            self.sessions_frame,
            columns=('title', 'start_time', 'status'),
            show='headings',
            height=6
        )
        
        # Cấu hình cột
        self.sessions_tree.heading('title', text='Tiêu đề')
        self.sessions_tree.heading('start_time', text='Thời gian bắt đầu')
        self.sessions_tree.heading('status', text='Trạng thái')
        
        self.sessions_tree.column('title', width=200)
        self.sessions_tree.column('start_time', width=150)
        self.sessions_tree.column('status', width=100)
        
        # Scrollbar cho treeview
        self.sessions_scrollbar = ttk.Scrollbar(
            self.sessions_frame, 
            orient="vertical", 
            command=self.sessions_tree.yview
        )
        self.sessions_tree.configure(yscrollcommand=self.sessions_scrollbar.set)
        
        # Bind double-click để xem phiên
        self.sessions_tree.bind('<Double-1>', self.view_session)
    
    def setup_layout(self):
        """
        Thiết lập layout cho giao diện
        """
        # Main frame
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Control frame
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        self.session_title_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.start_stop_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Region frame
        self.region_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        self.select_region_btn.grid(row=0, column=0, padx=5)
        self.auto_detect_btn.grid(row=0, column=1, padx=5)
        self.region_info_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Text frame
        self.text_frame.grid(row=2, column=0, sticky="nsew", pady=5, padx=(0, 5))
        self.text_display.grid(row=0, column=0, sticky="nsew")
        self.text_scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_frame.columnconfigure(0, weight=1)
        self.text_frame.rowconfigure(0, weight=1)
        
        # Stats frame
        self.stats_frame.grid(row=2, column=1, sticky="new", pady=5)
        for i, (key, label) in enumerate(self.stats_labels.items()):
            label.grid(row=i, column=0, sticky="w", pady=2)
        
        # Export frame
        self.export_frame.grid(row=3, column=1, sticky="ew", pady=5)
        self.export_txt_btn.grid(row=0, column=0, padx=5)
        self.export_md_btn.grid(row=0, column=1, padx=5)
        
        # Sessions frame
        self.sessions_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        self.sessions_tree.grid(row=0, column=0, sticky="ew")
        self.sessions_scrollbar.grid(row=0, column=1, sticky="ns")
        self.sessions_frame.columnconfigure(0, weight=1)
        
        # Configure main grid weights
        self.main_frame.rowconfigure(2, weight=1)
        
        # Load sessions
        self.load_sessions()
    
    def toggle_recording(self):
        """
        Bắt đầu hoặc dừng ghi chép
        """
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """
        Bắt đầu ghi chép
        """
        # Kiểm tra vùng chụp
        if not self.screen_capture.capture_region:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn vùng chụp màn hình trước!")
            return
        
        # Tạo phiên mới
        session_title = self.session_title_var.get().strip()
        if not session_title:
            session_title = f"Phiên ghi {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        self.current_session_id = self.storage_manager.create_session(session_title)
        
        # Reset text processor
        self.text_processor.reset_session()
        
        # Bắt đầu chụp màn hình
        self.screen_capture.start_continuous_capture(CAPTURE_CONFIG['interval'])
        
        # Bắt đầu thread xử lý
        self.is_recording = True
        self.processing_thread = threading.Thread(target=self.processing_loop, daemon=True)
        self.processing_thread.start()
        
        # Cập nhật giao diện
        self.start_stop_btn.config(text="Dừng ghi")
        self.session_title_entry.config(state="disabled")
        
        # Xóa text display
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete(1.0, tk.END)
        self.text_display.config(state=tk.DISABLED)
        
        print(f"Bắt đầu ghi phiên: {session_title}")
    
    def stop_recording(self):
        """
        Dừng ghi chép
        """
        self.is_recording = False
        
        # Dừng chụp màn hình
        self.screen_capture.stop_continuous_capture()
        
        # Kết thúc phiên
        if self.current_session_id:
            self.storage_manager.end_session(self.current_session_id)
        
        # Cập nhật giao diện
        self.start_stop_btn.config(text="Bắt đầu ghi")
        self.session_title_entry.config(state="normal")
        
        # Tạo tiêu đề mới cho phiên tiếp theo
        self.session_title_var.set(f"Phiên ghi {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Reload sessions
        self.load_sessions()
        
        print("Đã dừng ghi chép")
    
    def processing_loop(self):
        """
        Vòng lặp xử lý chính
        """
        while self.is_recording:
            try:
                # Lấy ảnh mới nhất
                screenshot_data = self.screen_capture.get_latest_screenshot()
                
                if screenshot_data:
                    image, timestamp = screenshot_data
                    
                    # Xử lý OCR
                    ocr_result = self.ocr_processor.extract_text(image)
                    
                    # Xử lý văn bản
                    processed_text = self.text_processor.process_new_text(ocr_result)
                    
                    if processed_text:
                        # Lưu vào database
                        self.storage_manager.save_transcript_entry(
                            self.current_session_id, 
                            processed_text
                        )
                        
                        # Cập nhật giao diện
                        self.root.after(0, self.update_display, processed_text)
                
                time.sleep(0.1)  # Ngắt ngủ ngắn để tránh CPU cao
                
            except Exception as e:
                print(f"Lỗi trong processing loop: {e}")
                time.sleep(1)
    
    def update_display(self, text_data):
        """
        Cập nhật hiển thị văn bản
        """
        # Cập nhật text display
        self.text_display.config(state=tk.NORMAL)
        
        timestamp_str = text_data['timestamp'].strftime('%H:%M:%S')
        display_text = f"[{timestamp_str}] {text_data['text']}\n"
        
        self.text_display.insert(tk.END, display_text)
        self.text_display.see(tk.END)
        self.text_display.config(state=tk.DISABLED)
        
        # Cập nhật thống kê
        session_summary = self.text_processor.get_session_summary()
        
        # Tính thời gian phiên
        if session_summary['start_time']:
            duration = datetime.now() - session_summary['start_time']
            duration_str = str(duration).split('.')[0]  # Bỏ microseconds
        else:
            duration_str = "00:00:00"
        
        self.stats_labels['session_time'].config(text=f"Thời gian: {duration_str}")
        self.stats_labels['word_count'].config(text=f"Số từ: {session_summary['word_count']}")
        self.stats_labels['confidence'].config(text=f"Độ tin cậy: {text_data['confidence']:.1f}%")
    
    def select_capture_region(self):
        """
        Cho phép người dùng chọn vùng chụp màn hình
        """
        messagebox.showinfo(
            "Chọn vùng", 
            "Sẽ mở cửa sổ chọn vùng. Kéo để chọn vùng Live Caption trên màn hình."
        )
        
        # Tạo cửa sổ overlay để chọn vùng
        self.create_region_selector()
    
    def create_region_selector(self):
        """
        Tạo cửa sổ chọn vùng
        """
        # Tạo cửa sổ overlay
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.3)
        overlay.configure(bg='black')
        overlay.attributes('-topmost', True)
        
        # Biến để lưu tọa độ
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        
        # Canvas để vẽ
        canvas = tk.Canvas(overlay, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        def start_selection(event):
            self.selection_start = (event.x, event.y)
            if self.selection_rect:
                canvas.delete(self.selection_rect)
        
        def update_selection(event):
            if self.selection_start:
                if self.selection_rect:
                    canvas.delete(self.selection_rect)
                
                x1, y1 = self.selection_start
                x2, y2 = event.x, event.y
                
                self.selection_rect = canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    outline='red', 
                    width=2
                )
        
        def end_selection(event):
            if self.selection_start:
                self.selection_end = (event.x, event.y)
                
                # Tính toán vùng chọn
                x1, y1 = self.selection_start
                x2, y2 = self.selection_end
                
                x = min(x1, x2)
                y = min(y1, y2)
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                
                if width > 10 and height > 10:  # Vùng đủ lớn
                    self.screen_capture.set_capture_region(x, y, width, height)
                    self.region_info_var.set(f"Vùng: {x}, {y}, {width}x{height}")
                
                overlay.destroy()
        
        def cancel_selection(event):
            overlay.destroy()
        
        # Bind events
        canvas.bind('<Button-1>', start_selection)
        canvas.bind('<B1-Motion>', update_selection)
        canvas.bind('<ButtonRelease-1>', end_selection)
        canvas.bind('<Escape>', cancel_selection)
        
        # Focus để nhận sự kiện keyboard
        canvas.focus_set()
        
        # Hiển thị hướng dẫn
        canvas.create_text(
            canvas.winfo_screenwidth() // 2,
            50,
            text="Kéo để chọn vùng Live Caption. Nhấn Escape để hủy.",
            fill='white',
            font=('Arial', 16)
        )
    
    def auto_detect_region(self):
        """
        Tự động phát hiện vùng Live Caption
        """
        region = self.screen_capture.auto_detect_live_caption_region()
        
        if region:
            x, y, width, height = region
            self.screen_capture.set_capture_region(x, y, width, height)
            self.region_info_var.set(f"Vùng: {x}, {y}, {width}x{height}")
            messagebox.showinfo("Thành công", "Đã tự động phát hiện vùng Live Caption!")
        else:
            messagebox.showwarning("Không tìm thấy", "Không thể tự động phát hiện vùng Live Caption. Vui lòng chọn thủ công.")
    
    def export_session(self, format_type):
        """
        Xuất phiên hiện tại
        """
        if not self.current_session_id:
            messagebox.showwarning("Cảnh báo", "Không có phiên nào để xuất!")
            return
        
        # Chọn file để lưu
        if format_type == 'txt':
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        else:  # markdown
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
            )
        
        if file_path:
            if format_type == 'txt':
                success = self.storage_manager.export_session_to_text(
                    self.current_session_id, 
                    file_path,
                    include_timestamps=EXPORT_CONFIG['include_timestamps']
                )
            else:
                success = self.storage_manager.export_session_to_markdown(
                    self.current_session_id, 
                    file_path
                )
            
            if success:
                messagebox.showinfo("Thành công", f"Đã xuất file: {file_path}")
            else:
                messagebox.showerror("Lỗi", "Không thể xuất file!")
    
    def load_sessions(self):
        """
        Tải danh sách phiên
        """
        # Xóa dữ liệu cũ
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
        
        # Tải phiên mới
        sessions = self.storage_manager.get_sessions()
        
        for session in sessions:
            self.sessions_tree.insert('', 'end', values=(
                session['title'],
                session['start_time'].strftime('%Y-%m-%d %H:%M'),
                session['status']
            ), tags=(session['id'],))
    
    def view_session(self, event):
        """
        Xem chi tiết phiên được chọn
        """
        selection = self.sessions_tree.selection()
        if not selection:
            return
        
        item = self.sessions_tree.item(selection[0])
        session_id = item['tags'][0]
        
        # Tạo cửa sổ xem phiên
        self.create_session_viewer(session_id)
    
    def create_session_viewer(self, session_id):
        """
        Tạo cửa sổ xem chi tiết phiên
        """
        viewer = tk.Toplevel(self.root)
        viewer.title("Xem phiên ghi chép")
        viewer.geometry("600x400")
        
        # Lấy thông tin phiên
        session_info = self.storage_manager.get_session_info(session_id)
        transcript_entries = self.storage_manager.get_session_transcript(session_id)
        
        # Frame thông tin
        info_frame = ttk.LabelFrame(viewer, text="Thông tin phiên", padding="10")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Tiêu đề: {session_info['title']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Bắt đầu: {session_info['start_time']}").pack(anchor="w")
        if session_info['end_time']:
            ttk.Label(info_frame, text=f"Kết thúc: {session_info['end_time']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Trạng thái: {session_info['status']}").pack(anchor="w")
        
        # Frame nội dung
        content_frame = ttk.LabelFrame(viewer, text="Nội dung", padding="10")
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Text widget
        text_widget = tk.Text(content_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Hiển thị nội dung
        for entry in transcript_entries:
            timestamp_str = entry['timestamp'].strftime('%H:%M:%S')
            text_widget.insert(tk.END, f"[{timestamp_str}] {entry['content']}\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Frame nút
        button_frame = ttk.Frame(viewer)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Nút xuất
        ttk.Button(
            button_frame,
            text="Xuất Text",
            command=lambda: self.export_specific_session(session_id, 'txt')
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="Xuất Markdown",
            command=lambda: self.export_specific_session(session_id, 'md')
        ).pack(side="left", padx=5)
    
    def export_specific_session(self, session_id, format_type):
        """
        Xuất phiên cụ thể
        """
        if format_type == 'txt':
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
            )
        
        if file_path:
            if format_type == 'txt':
                success = self.storage_manager.export_session_to_text(session_id, file_path)
            else:
                success = self.storage_manager.export_session_to_markdown(session_id, file_path)
            
            if success:
                messagebox.showinfo("Thành công", f"Đã xuất file: {file_path}")
            else:
                messagebox.showerror("Lỗi", "Không thể xuất file!")
    
    def on_closing(self):
        """
        Xử lý khi đóng ứng dụng
        """
        if self.is_recording:
            self.stop_recording()
        
        self.root.destroy()
    
    def run(self):
        """
        Chạy ứng dụng
        """
        self.root.mainloop()

if __name__ == "__main__":
    app = MainWindow()
    app.run()

