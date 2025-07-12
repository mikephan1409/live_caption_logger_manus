# File chính để chạy ứng dụng Live Caption Logger

import configparser
import logging
import time
from pathlib import Path
import sys

# Giả lập các module từ dự án gốc để mã nguồn có tính minh họa
# In a real scenario, these would be the actual project modules
class OCRProcessor:
    def __init__(self, tesseract_path, language):
        self.tesseract_path = tesseract_path
        self.language = language
        # In a real app, you would set pytesseract.pytesseract.tesseract_cmd here
        if not Path(self.tesseract_path).is_file():
            raise FileNotFoundError(f"Tesseract executable not found at: {self.tesseract_path}")
        logging.info(f"OCR Processor initialized for language: '{self.language}'")

    def recognize(self, image):
        # Giả lập quá trình OCR
        logging.debug("Performing OCR on image.")
        return "Đây là một phụ đề mẫu được nhận dạng."

class ScreenCapture:
    def __init__(self, region=None):
        self.region = region
        logging.info(f"Screen Capture initialized for region: {self.region or 'Full Screen'}")

    def capture(self):
        # Giả lập chụp ảnh màn hình
        logging.debug("Capturing screen.")
        return "image_data_placeholder"

class CaptionLogger:
    def __init__(self, db_path):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Caption Logger initialized with database: {self.db_path}")

    def log(self, text):
        # Giả lập ghi log vào DB
        logging.info(f"Logging caption: '{text}'")

def setup_logging(log_file, log_level_str):
    """Cấu hình hệ thống logging để ghi vào file và console."""
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file logger '{log_file}': {e}")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging configured.")

def load_config(path="config.ini"):
    """Tải và phân tích tệp cấu hình."""
    if not Path(path).is_file():
        logging.critical(f"Configuration file not found: {path}")
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    logging.info(f"Configuration loaded from {path}")
    return config

def initialize_dependencies(config):
    """Khởi tạo các thành phần cốt lõi dựa trên cấu hình."""
    try:
        tesseract_path = config.get('Tesseract', 'tesseract_cmd_path')
        ocr_language = config.get('OCR', 'language')
        ocr_processor = OCRProcessor(tesseract_path, ocr_language)

        capture_region_str = config.get('ScreenCapture', 'capture_region', fallback=None)
        capture_region = tuple(map(int, capture_region_str.split(','))) if capture_region_str else None
        screen_capture = ScreenCapture(region=capture_region)

        db_path = config.get('Logging', 'database_path')
        caption_logger = CaptionLogger(db_path)
        
        return ocr_processor, screen_capture, caption_logger

    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.error(f"Configuration error in config.ini: {e}")
        raise
    except FileNotFoundError as e:
        logging.error(f"Initialization failed: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during initialization: {e}", exc_info=True)
        raise

def main_loop(ocr, capture, logger, frequency_hz):
    """Vòng lặp chính của ứng dụng để chụp, xử lý và ghi log."""
    interval = 1.0 / frequency_hz
    last_processed_text = ""
    
    logging.info(f"Starting main loop with frequency: {frequency_hz}Hz (Interval: {interval:.2f}s)")
    
    while True:
        try:
            start_time = time.time()
            
            image = capture.capture()
            current_text = ocr.recognize(image)
            
            if current_text and current_text != last_processed_text:
                logger.log(current_text)
                last_processed_text = current_text
            
            elapsed_time = time.time() - start_time
            sleep_time = max(0, interval - elapsed_time)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logging.info("Process interrupted by user. Exiting.")
            break
        except Exception as e:
            logging.error(f"An error occurred in the main loop: {e}", exc_info=True)
            time.sleep(5) 

if __name__ == "__main__":
    log_file = 'app.log'
    try:
        config = load_config("config.ini")
        
        log_file = config.get('Logging', 'log_file', fallback='app.log')
        log_level = config.get('Logging', 'log_level', fallback='INFO')
        setup_logging(log_file, log_level)
        
        ocr_processor, screen_capture, caption_logger = initialize_dependencies(config)
        
        capture_frequency = config.getfloat('ScreenCapture', 'capture_frequency_hz', fallback=2.0)
        main_loop(ocr_processor, screen_capture, caption_logger, capture_frequency)
        
    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: {e}. Please ensure 'config.ini' exists and is correctly configured.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Application failed to start.", exc_info=True)
        print(f"An unrecoverable error occurred. Check '{log_file}' for details.")
        sys.exit(1)

