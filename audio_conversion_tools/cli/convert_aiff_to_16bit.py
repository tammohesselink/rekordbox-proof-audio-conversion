import argparse
import os

from audio_conversion_tools.convert_audio import (
    check_bit_depth_allowed,
    check_sample_rate_allowed,
    convert_aif_to_16bit,
    get_file_info,
)
from audio_conversion_tools.logging import logger
from audio_conversion_tools.utils import find_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert AIFF files to 16-bit format.")
    parser.add_argument("--recursive", action="store_true", help="Enable recursive mode to process subdirectories.")
    args = parser.parse_args()

    convert_aiff_to_16_bit(recursive=args.recursive)

    input("\nFinished! Press any key to exit.")


def convert_aiff_to_16_bit(recursive: bool) -> None:
    if recursive:
        input("Recursive mode enabled, will process subdirectories, if you are sure, press any key to continue.")
    delete_files = input("Do you want to delete the temp files after conversion? y/n\n")

    if delete_files not in ["y", "n"]:
        raise ValueError("Answer should be y or n")
    else:
        delete_files = delete_files == "y"

    if delete_files:
        logger.info("Will delete temp files after conversion!")

    root_directory = os.getcwd()

    # Get all aif / aiff files in the current directory
    available_files = find_files(os.getcwd(), extensions=[".aif", ".aiff"], recursive=recursive)

    logger.info(f"Currently in {root_directory}")

    # We check which aiff files we want to convert
    files_to_convert = []
    for filename in available_files:
        sample_rate, bit_depth = get_file_info(filename)

        if not (check_bit_depth_allowed(bit_depth) and check_sample_rate_allowed(sample_rate)):
            files_to_convert.append(filename)

    logger.info(
        f"Found {len(available_files)} AIFF files in total, {len(files_to_convert)} of which need to be converted"
    )
    if len(files_to_convert) > 0:
        logger.info(f"Converting all non 16-bit .aif and .aiff files in the current folder: {files_to_convert}")

        for file_name in files_to_convert:
            if convert_aif_to_16bit(file_name) and delete_files:
                temp_name = str(file_name).rsplit(".", 1)[0] + "_temp.aiff"
                os.remove(temp_name)
                logger.info(f"Deleted temp file {temp_name}")


if __name__ == "__main__":
    main()
