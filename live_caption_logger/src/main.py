# File chính để chạy ứng dụng Live Caption Logger
import configparser
import logging
import queue
import sys
import time
import sounddevice as sd
from pathlib import Path

# Placeholder for the actual Whisper transcription model
class WhisperModel:
    def __init__(self, model_name):
        logging.info(f"Loading Whisper model: {model_name}...")
        self.model_name = model_name
        # In a real application, this is where you would load the actual model, e.g.:
        # self.model = whisper.load_model(model_name)
        logging.info("Whisper model loaded successfully (simulation).")

    def transcribe(self, audio_data):
        # Simulate transcription
        logging.debug(f"Transcribing audio data of shape: {audio_data.shape}")
        # In a real application, you would call:
        # return self.model.transcribe(audio_data, fp16=torch.cuda.is_available())['text']
        return "This is a simulated live transcription."

def setup_logging(config):
    """Configures the logging system based on settings in the config file."""
    log_file = config.get('Logging', 'log_file', fallback='app.log')
    log_level_str = config.get('Logging', 'log_level', fallback='INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging configured.")

def load_config(path="config.ini"):
    """Loads and validates the configuration file."""
    config_path = Path(path)
    if not config_path.is_file():
        logging.critical(f"FATAL: Configuration file not found at '{path}'.")
        logging.critical("Please run 'python list_devices.py' to create and configure it.")
        raise FileNotFoundError(f"Configuration file '{path}' not found.")
    
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    logging.info(f"Configuration loaded from '{path}'.")
    return config

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        logging.warning(f"Audio stream status: {status}")
    q.put(indata.copy())

if __name__ == "__main__":
    stream = None  # Initialize stream to None
    try:
        # --- 1. Load Configuration and Setup Logging ---
        config = load_config("config.ini")
        setup_logging(config)

        # --- 2. Initialize Dependencies ---
        model_name = config.get('Whisper', 'model_name', fallback='base.en')
        whisper_model = WhisperModel(model_name)

        # --- 3. Setup Audio Stream ---
        samplerate = config.getint('Audio', 'samplerate')
        channels = config.getint('Audio', 'channels')
        device_id = config.getint('Audio', 'device')
        
        logging.info(f"Attempting to open audio stream on device ID {device_id}...")
        q = queue.Queue()
        
        stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            device=device_id,
            callback=audio_callback
        )
        stream.start()
        logging.info("Audio stream started successfully.")

        # --- 4. Main Application Loop ---
        print("\n--- Live Captioning Active --- (Press Ctrl+C to stop)")
        while True:
            # In a real app, you would collect audio from the queue,
            # process it, and pass it to the Whisper model.
            audio_chunk = q.get()
            transcription = whisper_model.transcribe(audio_chunk)
            print(f"\r>> {transcription}", end="", flush=True)
            # This is a simplified loop. A real implementation would handle
            # audio chunking, silence detection, etc.
            time.sleep(0.1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.critical(f"Configuration error in 'config.ini': {e}")
        print(f"Error in 'config.ini': {e}. Please check the file structure.", file=sys.stderr)
        sys.exit(1)
    except sd.PortAudioError as e:
        logging.critical(f"SoundDevice Error: {e}. Could not open audio stream.")
        logging.critical("Is the correct audio 'device' ID set in config.ini? Run list_devices.py to check.")
        print(f"\nAudio Error: {e}\nPlease check your audio device configuration.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logging.critical("An unexpected error occurred during startup or execution.", exc_info=True)
        print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n--- Exiting gracefully ---")
    finally:
        if stream is not None and stream.active:
            logging.info("Stopping audio stream.")
            stream.stop()
            stream.close()
            logging.info("Audio stream closed.")
        else:
            logging.info("Audio stream was not active. No cleanup needed.")


