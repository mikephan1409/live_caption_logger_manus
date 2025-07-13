import sounddevice as sd
import configparser
from pathlib import Path

CONFIG_FILE = "config.ini"

def select_audio_device():
    """Lists available input devices and prompts the user to select one."""
    print("Querying for available audio input devices...")
    try:
        devices = sd.query_devices()
        input_devices = [dev for i, dev in enumerate(devices) if dev['max_input_channels'] > 0]
    except Exception as e:
        print(f"\nError: Could not query audio devices. {e}")
        print("Please ensure you have a microphone connected and drivers installed.")
        return None

    if not input_devices:
        print("\nError: No audio input devices found.")
        print("Please ensure a microphone is connected.")
        return None

    print("\n--- Available Audio Input Devices ---")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"  ID: {i}, Name: {dev['name']}")
    print("-------------------------------------\n")

    while True:
        try:
            device_id_str = input("Enter the ID of the device you want to use: ")
            device_id = int(device_id_str)
            if any(i == device_id for i, dev in enumerate(devices) if dev['max_input_channels'] > 0):
                return device_id
            else:
                print("Error: Invalid ID. Please choose an ID from the list above.")
        except ValueError:
            print("Error: Please enter a valid number.")
        except (EOFError, KeyboardInterrupt):
            print("\nSelection cancelled.")
            return None


def update_config_file(device_id):
    """Updates the config.ini file with the selected device ID."""
    config = configparser.ConfigParser()
    config_path = Path(CONFIG_FILE)

    if config_path.exists():
        config.read(config_path)
        print(f"Loaded existing configuration from '{CONFIG_FILE}'.")

    # Ensure sections exist
    if not config.has_section('Audio'):
        config.add_section('Audio')
        print("Created new [Audio] section.")
    if not config.has_section('Whisper'):
        config.add_section('Whisper')
    if not config.has_section('Logging'):
        config.add_section('Logging')

    # Set default values if they don't exist
    config.set('Audio', 'samplerate', config.get('Audio', 'samplerate', fallback='16000'))
    config.set('Audio', 'channels', config.get('Audio', 'channels', fallback='1'))
    config.set('Whisper', 'model_name', config.get('Whisper', 'model_name', fallback='base.en'))
    config.set('Logging', 'log_file', config.get('Logging', 'log_file', fallback='logs/app.log'))
    config.set('Logging', 'log_level', config.get('Logging', 'log_level', fallback='INFO'))

    # Update the device ID
    config.set('Audio', 'device', str(device_id))
    
    try:
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"\nSuccessfully updated '{CONFIG_FILE}' with Device ID: {device_id}")
    except IOError as e:
        print(f"\nError: Could not write to '{CONFIG_FILE}'. {e}")

if __name__ == "__main__":
    selected_id = select_audio_device()
    if selected_id is not None:
        update_config_file(selected_id)
