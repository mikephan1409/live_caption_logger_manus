# Cấu hình ứng dụng Live Caption Logger

import os
from pathlib import Path

# Đường dẫn cơ bản
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Tạo thư mục nếu chưa tồn tại
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Cấu hình OCR
OCR_CONFIG = {
    'language': 'eng',  # Ngôn ngữ mặc định
    'psm': 6,  # Page segmentation mode
    'oem': 3,  # OCR Engine Mode
}

# Cấu hình chụp màn hình
CAPTURE_CONFIG = {
    'interval': 1.0,  # Khoảng thời gian giữa các lần chụp (giây)
    'region': None,   # Vùng chụp (x, y, width, height) - None để chụp toàn màn hình
}

# Cấu hình xử lý văn bản
TEXT_PROCESSING_CONFIG = {
    'min_confidence': 30,  # Độ tin cậy tối thiểu của OCR
    'duplicate_threshold': 0.8,  # Ngưỡng để phát hiện văn bản trùng lặp
    'max_line_length': 200,  # Độ dài tối đa của một dòng
}

# Cấu hình cơ sở dữ liệu
DATABASE_CONFIG = {
    'path': DATA_DIR / "transcripts.db",
    'backup_interval': 3600,  # Backup mỗi giờ (giây)
}

# Cấu hình giao diện
UI_CONFIG = {
    'window_title': "Live Caption Logger",
    'window_size': (800, 600),
    'theme': 'light',  # light hoặc dark
}

# Cấu hình xuất file
EXPORT_CONFIG = {
    'default_format': 'txt',  # txt, md, json
    'include_timestamps': True,
    'include_metadata': True,
}

