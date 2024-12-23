import argparse

from audio_conversion_tools.cli.convert_aiff_to_16bit import convert_aiff_to_16_bit
from audio_conversion_tools.cli.convert_lossless_to_aiff import convert_lossless_to_aiff


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert AIFF files to 16-bit format.")
    parser.add_argument("--recursive", action="store_true", help="Enable recursive mode to process subdirectories.")
    args = parser.parse_args()

    convert_aiff_to_16_bit(recursive=args.recursive)
    convert_lossless_to_aiff(recursive=args.recursive)


if __name__ == "__main__":
    main()
