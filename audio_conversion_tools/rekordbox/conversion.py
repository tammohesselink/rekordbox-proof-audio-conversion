import datetime
import shutil
from pathlib import Path

from loguru import logger
from pyrekordbox import xml

from audio_conversion_tools.convert_audio import (
    convert_aif_to_16bit,
    convert_to_aiff,
    convert_wav_to_16bit,
    determine_target_sample_rate,
    get_file_info,
)


class ConversionError(Exception): ...


def convert_files(unplayable_files: list[xml.Track], archive_folder: Path):
    """
    Converts the files from samplerate s to samplerate s/2 and the bitrate to 16 bit.

    Args:
        unplayable_files (List[xml.Track]): list of unplayable tracks
        archive_folder (Path): folder to move the archive tracks to
    """
    succesful_conversions = 0
    for file in unplayable_files:
        file_location = Path(file.Location).absolute()

        if not file_location.exists():
            logger.error(f"No file available at {file_location}, skipping conversion!")
            continue

        input_sample_rate, input_bit_depth = get_file_info(file_location)

        output_bit_depth = 16
        output_sample_rate = determine_target_sample_rate(input_sample_rate)

        location_within_archive_folder = archive_folder / Path(file.Location).name

        if location_within_archive_folder.exists():
            logger.error(
                f"File {Path(file_location).name} already exists in the archive, will not overwrite the archive. "
                "Clear your archive manually if you want to confirm this file.",
            )
            continue

        succesful_conversion = False
        try:
            if file.Kind.lower()[:3] == "wav":
                succesful_conversion = convert_wav_to_16bit(
                    file_name=file_location,
                    temp_location=location_within_archive_folder,
                )
            if file.Kind.lower()[:3] == "aif":
                succesful_conversion = convert_aif_to_16bit(
                    file_name=file_location,
                    temp_location=location_within_archive_folder,
                )
            if succesful_conversion:
                add_to_conversion_db(
                    archive_folder,
                    file_location=file_location,
                    location_within_archive_folder=location_within_archive_folder,
                    input_sample_rate=input_sample_rate,
                    input_bit_depth=input_bit_depth,
                    output_sample_rate=output_sample_rate,
                    output_bit_depth=output_bit_depth,
                )
                succesful_conversions += 1
        except ConversionError:
            logger.info(f"Error converting file {file.Location}")

    logger.info(f"Succesfully converted {succesful_conversions} of {len(unplayable_files)} files!")


def convert_flacs(flac_files: list[xml.Track], archive_folder: Path):
    succesful_conversions = 0
    for file in flac_files:
        file_location = Path(file.Location).absolute()

        location_within_archive_folder = archive_folder / "converted_flacs" / Path(file.Location).name

        if convert_to_aiff(file_location, location_within_archive_folder):
            succesful_conversions += 1

    logger.info(f"Succesfully converted {succesful_conversions} of {len(flac_files)} files!")


def archive_files(unplayable_files: list[xml.Track], archive_folder: Path):
    Path(archive_folder).mkdir(parents=True, exist_ok=True)

    for file in unplayable_files:
        # Adding the / is important because unfortunately rekordbox saves the location without a leading /
        shutil.copy(Path(file.Location).absolute(), archive_folder / Path(file.Location).name)
        logger.info(f"Moved {file.Location} to {archive_folder / Path(file.Location).name}")


def add_to_conversion_db(
    archive_folder,
    file_location,
    location_within_archive_folder,
    input_sample_rate,
    input_bit_depth,
    output_sample_rate,
    output_bit_depth,
):
    current_time = datetime.datetime.now()

    with open(Path(archive_folder) / "converted.csv", "a") as f:
        f.write(
            f"{current_time},{file_location},{location_within_archive_folder},{input_sample_rate},{output_sample_rate},{input_bit_depth},{output_bit_depth}\n",
        )


def _calculate_bit_depth(file) -> int:
    return int(round(1000 * file.BitRate / (file.SampleRate * 2)))
