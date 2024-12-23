import argparse
import os
from typing import List

from audio_conversion_tools.convert_audio import convert_to_aiff
from audio_conversion_tools.logging import logger
from audio_conversion_tools.utils import find_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert AIFF files to 16-bit format.")
    parser.add_argument("--recursive", action="store_true", help="Enable recursive mode to process subdirectories.")
    args = parser.parse_args()

    if args.recursive:
        input("Recursive mode enabled, will process subdirectories, if you are sure, press any key to continue.")
    delete_files_input = input("Do you want to delete the files after conversion? y/n\n")

    if delete_files_input not in ["y", "n"]:
        raise ValueError("Answer should be y or n")

    should_delete_files = delete_files_input == "y"

    if should_delete_files:
        logger.info("Will delete all files after conversion!")

    # Get all wav and flac files in the current directory
    files_to_convert: List[str] = find_files(os.getcwd(), extensions=[".wav", ".flac"], recursive=args.recursive)

    logger.info(f"Currently in {os.getcwd()}")
    if len(files_to_convert) > 0:
        logger.info(f"Converting all .wav and .flac files in the current folder: {files_to_convert}")

        for file_name in files_to_convert:
            if convert_to_aiff(file_name):
                if should_delete_files:
                    os.remove(file_name)
                    logger.info(f"Deleted {file_name}")
    else:
        logger.info("No .wav or .flac files found")

    input("Finished! Press any key to exit.")
