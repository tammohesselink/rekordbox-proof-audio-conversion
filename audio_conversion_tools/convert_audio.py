import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import soundfile as sf

from audio_conversion_tools.logging import logger

FFMPEG_LOG_LOCATION = Path(__file__).parent.parent / "ffmpeg_log.log"


class ConversionError(Exception): ...


def get_file_info(file_name: str) -> Tuple[Optional[int], Optional[int]]:
    subtype_mapping = {"PCM_16": 16, "PCM_24": 24, "PCM_32": 32}

    try:
        info = sf.info(file_name)
        sample_rate = info.samplerate
        bit_depth = subtype_mapping[info.subtype]
        return sample_rate, bit_depth
    except Exception as e:
        logger.error(f"Could not get file info for {file_name}: {e}")
        return None, None


def determine_target_sample_rate(sample_rate: int) -> int:
    """
    Rekordbox requires the sample rate to be 44.1 or 48 kHz. We divide the sample rate
    by 2 or 4 in case the sample rate is too high, so we don't have any synchronisation
    issues later.
    """
    if sample_rate in [88200, 96000]:
        target_sample_rate = sample_rate // 2
    elif sample_rate == 192000:
        target_sample_rate = 48000
    elif sample_rate in [44100, 48000]:
        target_sample_rate = sample_rate
    else:
        raise ValueError(f"Unknown sample rate {sample_rate}!")

    return target_sample_rate


def check_sample_rate_allowed(sample_rate: int | None) -> bool:
    if sample_rate is None:
        return False
    return sample_rate in [44100, 48000]


def check_bit_depth_allowed(bit_rate: int | None) -> bool:
    if bit_rate is None:
        return False
    return bit_rate == 16


def convert_aif_to_16bit(file_name: str, temp_location: str | None = None) -> bool:
    """Converts a given AIFF file to 16-bit AIFF and changes sample rate if required."""
    if temp_location is None:
        temp_location = str(file_name).rsplit(".", 1)[0] + "_temp.aiff"

    # Rename the original file to temp_location
    os.rename(file_name, temp_location)

    sample_rate, bit_depth = get_file_info(temp_location)

    if sample_rate is None or bit_depth is None:
        logger.error(f"Couldn't determine sample rate or bit depth for {temp_location}")
        return False

    # If already 16-bit and either 44.1kHz or 48kHz, move back to the original name and return
    if check_bit_depth_allowed(bit_depth) and check_sample_rate_allowed(sample_rate):
        os.rename(temp_location, file_name)
        logger.warning(f"Skipped {file_name} as it's already in desired format.")
        return False

    target_sample_rate = determine_target_sample_rate(sample_rate)

    cmd = [
        "ffmpeg",
        "-y",  # We overwrite if a file already exists
        "-hide_banner",
        "-i",
        temp_location,
        "-ar",
        str(target_sample_rate),
        "-sample_fmt",
        "s16",
        "-write_id3v2",
        "1",
        file_name,
    ]

    with open(FFMPEG_LOG_LOCATION, "a") as log_file:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            # Log the captured output to your log file
            log_file.write(result.stdout)
            log_file.write("\n\n")
            logger.info(
                f"Converted {file_name} from {bit_depth} bit / {sample_rate}Hz to 16 bit / {target_sample_rate}Hz",
            )
            return True
        except subprocess.CalledProcessError as e:
            # Log the captured output to your log file
            log_file.write(e.output)
            log_file.write("\n\n")
            os.rename(temp_location, file_name)  # Move the temp file back to original name if failed
            logger.error(
                f"Failed to convert {file_name} to 16-bit AIFF with target sample rate {target_sample_rate}Hz: :"
                f" {e.output}",
            )
            return False


def convert_wav_to_16bit(file_name: str, temp_location: str | None = None) -> bool:
    """Converts a given WAV file to 16-bit AIFF and changes sample rate if required."""
    if temp_location is None:
        temp_location = str(file_name).rsplit(".", 1)[0] + "_temp.wav"

    # Rename the original file to temp_location
    os.rename(file_name, temp_location)

    sample_rate, bit_depth = get_file_info(temp_location)

    if sample_rate is None or bit_depth is None:
        logger.warning(f"Couldn't determine sample rate or bit depth for {temp_location}")
        return False

    # If already 16-bit and either 44.1kHz or 48kHz, move back to the original name and return
    if check_bit_depth_allowed(bit_depth) and check_sample_rate_allowed(sample_rate):
        os.rename(temp_location, file_name)
        logger.warning(f"Skipped {file_name} as it's already in desired format.")
        return False

    try:
        target_sample_rate = determine_target_sample_rate(sample_rate)
    except ValueError as e:
        logger.error(f"Could not determine target sample rate for {file_name}: {e}")
        return False

    cmd = [
        "ffmpeg",
        "-y",  # We overwrite if a file already exists
        "-hide_banner",
        "-i",
        temp_location,
        "-ar",
        str(target_sample_rate),
        "-sample_fmt",
        "s16",
        "-write_id3v2",
        "1",
        file_name,
    ]

    with open(FFMPEG_LOG_LOCATION, "a") as log_file:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            log_file.write(result.stdout)
            log_file.write("\n\n")
            logger.info(
                f"Converted {file_name} from {bit_depth} bit / {sample_rate}Hz to 16 bit / {target_sample_rate}Hz",
            )
            return True
        except subprocess.CalledProcessError as e:
            log_file.write(e.output)
            log_file.write("\n\n")

            os.rename(temp_location, file_name)  # Move the temp file back to original name if failed
            logger.error(
                f"Failed to convert {file_name} to 16-bit WAV with target sample rate {target_sample_rate}Hz: :"
                f" {e.output}",
            )
            return False


def convert_to_aiff(file_name: str, output_name: str | None = None) -> bool:
    if not Path(file_name).exists():
        logger.error(f"The file {file_name} does not exist!")
        return False

    if output_name is None:
        output_name = str(file_name).rsplit(".", 1)[0] + ".aiff"

    # Create output directory if it doesn't exist
    output_path = Path(output_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sample_rate, bit_depth = get_file_info(file_name)

    if sample_rate is None or bit_depth is None:
        logger.error(f"Couldn't determine sample rate or bit depth for {file_name}, will not convert")
        return False

    try:
        target_sample_rate = determine_target_sample_rate(sample_rate)
    except ValueError as e:
        logger.error(f"Could not determine target sample rate for {file_name}: {e}")
        return False

    cmd = [
        "ffmpeg",
        "-y",  # We overwrite if a file already exists
        "-hide_banner",
        "-i",
        file_name,
        "-ar",
        str(target_sample_rate),
        "-sample_fmt",
        "s16",
        "-write_id3v2",
        "1",
        output_name,
    ]

    with open(FFMPEG_LOG_LOCATION, "a") as log_file:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            log_file.write(result.stdout)
            log_file.write("\n\n")

            logger.info(
                f"Converted {file_name} ({(sample_rate / 1000):.1f}kHz / {bit_depth} bit) to AIFF"
                f" ({(target_sample_rate / 1000):.1f}kHz / 16 bit)",
            )
            return True
        except subprocess.CalledProcessError as e:
            log_file.write(e.output)
            log_file.write("\n\n")
            logger.error(f"Failed to convert {file_name} to AIFF: {e.output}")
            return False


def convert_aif_to_mp3_v0(file_name: str) -> bool:
    output_name = str(file_name).rsplit(".", 1)[0] + ".mp3"

    # Command to use ffmpeg to convert the file to v0 mp3
    cmd = [
        "ffmpeg",
        "-y",  # We overwrite if a file already exists
        "-hide_banner",
        "-i",
        file_name,
        "-q:a",
        "0",  # This sets the quality to VBR V0
        "-write_id3v2",
        "1",
        output_name,
    ]

    with open(FFMPEG_LOG_LOCATION, "a") as log_file:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
            # Log the captured output to your log file
            log_file.write(result.stdout)
            log_file.write("\n\n")
            logger.info(f"Converted {file_name} to mp3")
            return True
        except subprocess.CalledProcessError as e:
            # Log the captured output to your log file
            log_file.write(e.output)
            log_file.write("\n\n")
            logger.error(f"Failed to convert {file_name} to mp3: {e.output}")
            return False
