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

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_sizes: dict[str, int] = {}
        self.processed_files: list[str] = []
        self.locks = {}  # Dictionary to store locks for each file

    def get_lock(self, file_path):
        if file_path not in self.locks:
            self.locks[file_path] = threading.Lock()
        return self.locks[file_path]
    
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
        print(self.file_sizes)
        print(self.processed_files)

        if event.is_directory:
            return

        file_path = event.src_path

        # Skip files with ".part" extension
        if file_path.endswith('.part'):
            return
        
        if file_path in self.processed_files:
            logger.debug(f"File {file_path} has already been processed, skipping")
            return

        try:
            current_size = os.path.getsize(file_path)
        except FileNotFoundError:
            logger.warning(f"File {file_path} not found, skipping (probably a temporary download file)")
            return

        # Check if the file size has remained constant for a certain period
        logger.info(f'Checking if {file_path} has finished downloading...')
        time.sleep(2)  # Adjust the delay as needed
        if file_path in self.file_sizes and current_size == self.file_sizes[file_path]:
            if file_path.lower().endswith(".aif") or file_path.lower().endswith(".aiff"):
                sample_rate, bit_depth = get_file_info(file_path)

                if (sample_rate in [44100, 48000] and bit_depth == 16):
                    logger.info(f"No conversion required for {file_path}")
                    return

            lock = self.get_lock(file_path)
            with lock:
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
    # Replace this with the path to your Downloads folder
    downloads_folder = os.getenv("DOWNLOADS_LOCATION")


    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=downloads_folder, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()