import os

from audio_conversion_tools.convert_audio import convert_aif_to_mp3_v0
from audio_conversion_tools.logging import logger

if __name__ == "__main__":
    delete_files = input("Do you want to delete the files after conversion? y/n\n")

    if delete_files not in ["y", "n"]:
        raise ValueError("Answer should be y or n")
    else:
        delete_files = delete_files == "y"

    if delete_files:
        logger.info("Will delete all files after conversion!")

    # Get all aif and aiff files in the current directory
    files_to_convert = [f for f in os.listdir() if f.lower().endswith((".aif", ".aiff", ".wav", ".flac"))]
    logger.info(f"Currently in {os.getcwd()}")
    logger.info(f"Converting all .wav, .aif(f) and .flac files in the current folder: {files_to_convert}")

    for file_name in files_to_convert:
        if convert_aif_to_mp3_v0(file_name):
            logger.info(f"Converted {file_name}")
            if delete_files:
                os.remove(file_name)
                logger.info(f"Deleted {file_name}")

    input("Finished! Press any key to exit.")
