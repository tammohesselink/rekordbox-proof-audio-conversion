import os
import sys

from loguru import logger

from audio_conversion_tools.convert_audio import convert_aif_to_16bit, convert_to_aiff, get_file_info

logger.add("auto_convert_downloads.log")


def main():
    filename = sys.argv[1]

    if filename.lower().endswith(".aif") or filename.lower().endswith(".aiff"):
        sample_rate, bit_depth = get_file_info(filename)

        if not (sample_rate in [44100, 48000] and bit_depth == 16):
            logger.info(f"Converting {filename} to 16-bit AIFF...")
            convert_aif_to_16bit(filename)

            os.remove(filename.rsplit(".", 1)[0] + "_temp.aiff")
            logger.info(f"Deleted {filename.rsplit('.', 1)[0] + '_temp.aiff'}")

    elif filename.lower().endswith(".wav") or filename.lower().endswith(".flac"):
        logger.info(f"Converting {filename} to 16-bit AIFF...")
        convert_to_aiff(filename)

        os.remove(filename)
        logger.info(f"Deleted {filename}")
    else:
        logger.info(f"No conversion required for {filename}")


if __name__ == "__main__":
    main()
