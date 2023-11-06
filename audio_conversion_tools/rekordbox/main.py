from pathlib import Path

import typer
from loguru import logger
from pyrekordbox import Rekordbox6Database
from pyrekordbox.xml import RekordboxXml

from audio_conversion_tools.rekordbox.constants import ALLOWED_BIT_DEPTHS, ALLOWED_SAMPLE_RATES, FILE_TYPES_TO_CONVERT
from audio_conversion_tools.rekordbox.convert_audio import _calculate_bit_depth, convert_files, convert_flacs


def convert_rekordbox_audio(
    archive_folder: str = typer.Option(...),
    rekordbox_xml_location: str = typer.Argument(
        None, help="XML file to use in case Rekordbox 6 database does not work."
    ),
    lower_bitrate: bool = typer.Option(False, "--lower-bitrate", "-l", help="Lower the bitrate to 16 bit."),
):
    (Path(archive_folder) / "converted_flacs").mkdir(exist_ok=True, parents=True)

    # Configure Loguru to write log messages to a file with timestamps
    logger.add(Path(archive_folder) / "example.log", format="{time} - {level} - {message}", level="INFO")

    if not rekordbox_xml_location:
        Rekordbox6Database()
    else:
        xml = RekordboxXml(rekordbox_xml_location)
        tracks = xml.get_tracks()

    lossless_files = [track for track in tracks if (any(x in track.Kind.lower() for x in FILE_TYPES_TO_CONVERT))]
    logger.info(
        f"Read Rekordbox collection, found {len(tracks)} tracks in total of which {len(lossless_files)} WAV / AIFF"
    )

    unplayable_files = [
        track
        for track in tracks
        if (
            (any(x in track.Kind.lower() for x in FILE_TYPES_TO_CONVERT))
            and (
                (int(track.SampleRate) not in ALLOWED_SAMPLE_RATES)
                or (_calculate_bit_depth(track) not in ALLOWED_BIT_DEPTHS)
            )
        )
    ]
    percentage_unplayable = (len(unplayable_files) / len(lossless_files)) * 100
    logger.info(f"Found {len(unplayable_files)} ({percentage_unplayable:.1f}%) unplayable WAV / AIFFs")

    logger.info(f"Will archive original files to {Path(archive_folder).resolve()}")
    logger.info("Starting the conversion process...")

    # We convert all files to the closest playable format.
    convert_files(unplayable_files, Path(archive_folder))

    # We also convert all FLACs in Rekordbox.
    flac_files = [track for track in tracks if track.Kind.lower()[:4] == "flac"]

    logger.info(f"Additionally found {len(flac_files)} FLACs which are also unplayable")

    convert_flacs(flac_files, Path(archive_folder))
    logger.warning(
        f"The converted FLACs can be found in {Path(archive_folder) / 'converted_flacs'},"
        "but you have to add these to Rekordbox manually as the file type changed"
    )


def main():
    typer.run(convert_rekordbox_audio)
