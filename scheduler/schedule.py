import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import subprocess
from pathlib import Path
from dotenv import load_dotenv

from audio_conversion_tools.logging import logger
from audio_conversion_tools.convert_audio import convert_aif_to_16bit, get_file_info, convert_to_aiff

load_dotenv()

# Get the DOWNLOADS_LOCATIONS variable from the environment
downloads_locations = os.getenv("DOWNLOADS_LOCATIONS")

# Split the string into a list of folder paths
downloads_folders = downloads_locations.split(",")

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_sizes: dict[str, int] = {}
        self.processed_files: list[str] = []
        self.locked_files: list[str] = []

        # Use a separate observer for each downloads folder
        self.observers = [Observer() for _ in downloads_folders]

        # Start an observer for each downloads folder
        for observer, folder in zip(self.observers, downloads_folders):
            observer.schedule(self, path=folder, recursive=True)
            observer.start()
    
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path

        # Skip files with ".part" extension
        if file_path.endswith('.part'):
            return

        logger.info(f'Download started: {file_path}')
        self.file_sizes[file_path] = os.path.getsize(file_path)

    def on_modified(self, event):
        print(self.locked_files)
        if event.is_directory:
            return

        file_path = event.src_path

        # Skip files with ".part" extension
        if file_path.endswith('.part'):
            return
        
        # If file has been processed or is currently being processed, skip
        if file_path in self.processed_files:
            # logger.debug(f"File {file_path} has already been processed, skipping")
            return
        
        if file_path in self.locked_files:
            logger.debug(f"File {file_path} is currently being processed, skipping")
            return

        try:
            current_size = os.path.getsize(file_path)
        except FileNotFoundError:
            logger.warning(f"File {file_path} not found, skipping (probably a temporary download file)")
            return

        # We lock the file so we don't attempt to run conversion twice at the same time        
        self.locked_files.append(file_path)

        # Check if the file size has remained constant for a certain period
        logger.info(f'Checking if {file_path} has finished downloading...')
        time.sleep(2)  # Adjust the delay as needed
        if file_path in self.file_sizes and current_size == self.file_sizes[file_path]:
            if file_path.lower().endswith(".aif") or file_path.lower().endswith(".aiff"):
                sample_rate, bit_depth = get_file_info(file_path)

                if (sample_rate in [44100, 48000] and bit_depth == 16):
                    logger.info(f"No conversion required for {file_path}")
                    return

            logger.info(f'Download completed: {file_path}')
            # Mark the file as processed to avoid double execution
            self.processed_files.append(file_path)

            logger.info(f"Converting {file_path} to 16-bit AIFF...")
            self.processed_files.append(str(Path(file_path).with_suffix(".aiff")))
            run_script_on_new_file(file_path)

        else:
            # Update the file size if the file is still being modified
            logger.debug(f"File {file_path} is still being modified, updating file size")
            self.file_sizes[file_path] = current_size
        
        self.locked_files.remove(file_path)
            
def run_script_on_new_file(filename: str):
    try:
        # Replace this with the absolute path to your Python script and any other necessary arguments
        script_path = os.getenv("SCHEDULED_SCRIPT_LOCATION")
        python_path = os.getenv("PYTHON_LOCATION")

        # Run your Python script with the new file as an argument
        subprocess.run([python_path, script_path, filename], check=True)

        # Remove the file from the file_sizes dictionary only after successful execution
        del event_handler.file_sizes[filename]
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")

if __name__ == "__main__":
    event_handler = FileHandler()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        for observer in event_handler.observers:
            observer.stop()

        for observer in event_handler.observers:
            observer.join()