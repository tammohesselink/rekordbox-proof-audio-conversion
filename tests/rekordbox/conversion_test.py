from pathlib import Path
from unittest.mock import Mock

import pytest
from pyrekordbox import xml

from audio_conversion_tools.rekordbox.conversion import (
    _calculate_bit_depth,
    add_to_conversion_db,
    archive_files,
    convert_files,
    convert_flacs,
)

TEST_WAV_LOCATION = "tests/test_audio/silence_32bit.wav"
TEST_AIFF_LOCATION = "tests/test_audio/silence_32bit.aiff"


@pytest.fixture
def mock_track():
    track = Mock(spec=xml.Track)
    track.Location = TEST_WAV_LOCATION
    track.Kind = "WAV"
    track.BitRate = 1411
    track.SampleRate = 44100
    return track


@pytest.fixture
def mock_aiff_track():
    track = Mock(spec=xml.Track)
    track.Location = TEST_AIFF_LOCATION
    track.Kind = "AIFF"
    track.BitRate = 1411
    track.SampleRate = 44100
    return track


@pytest.fixture
def mock_flac_track():
    track = Mock(spec=xml.Track)
    track.Location = "tests/test_audio/test.flac"
    track.Kind = "FLAC"
    track.BitRate = 1411
    track.SampleRate = 44100
    return track


@pytest.fixture
def archive_folder(tmp_path):
    folder = tmp_path / "archive"
    folder.mkdir()
    return folder


def test_convert_files(mock_track, mock_aiff_track, archive_folder):
    # Test WAV conversion
    convert_files([mock_track], archive_folder)
    assert (archive_folder / "silence_32bit.wav").exists()
    assert (archive_folder / "converted.csv").exists()

    # Test AIFF conversion
    convert_files([mock_aiff_track], archive_folder)
    assert (archive_folder / "silence_32bit.aiff").exists()


def test_convert_files_nonexistent(archive_folder):
    track = Mock(spec=xml.Track)
    track.Location = "nonexistent.wav"
    track.Kind = "WAV"

    convert_files([track], archive_folder)
    assert not (archive_folder / "nonexistent.wav").exists()


def test_convert_files_already_exists(mock_track, archive_folder):
    # Create a file in archive to simulate existing file
    (archive_folder / "silence.wav").touch()

    convert_files([mock_track], archive_folder)
    # Should not overwrite existing file
    assert (archive_folder / "silence_32bit.wav").exists()


def test_convert_flacs(mock_flac_track, archive_folder):
    flac_folder = archive_folder / "converted_flacs"
    flac_folder.mkdir()

    # Create a test FLAC file
    test_flac = Path("tests/test_audio/test.flac")
    test_flac.parent.mkdir(parents=True, exist_ok=True)
    test_flac.touch()

    convert_flacs([mock_flac_track], archive_folder)

    expected_output = flac_folder / "test.aiff"
    assert not expected_output.exists()  # Should fail since test.flac is empty

    test_flac.unlink()


def test_archive_files(mock_track, archive_folder):
    archive_files([mock_track], archive_folder)
    assert (archive_folder / "silence_32bit.wav").exists()


def test_add_to_conversion_db(archive_folder):
    file_location = Path("test.wav")
    archive_location = archive_folder / "test.wav"

    add_to_conversion_db(
        archive_folder=archive_folder,
        file_location=file_location,
        location_within_archive_folder=archive_location,
        input_sample_rate=88200,
        input_bit_depth=32,
        output_sample_rate=44100,
        output_bit_depth=16,
    )

    db_file = archive_folder / "converted.csv"
    assert db_file.exists()

    content = db_file.read_text()
    assert str(file_location) in content
    assert str(archive_location) in content
    assert "88200" in content
    assert "44100" in content
    assert "32" in content
    assert "16" in content


def test_calculate_bit_depth(mock_track):
    # Test 16-bit calculation (1411 kbps at 44.1kHz)
    assert _calculate_bit_depth(mock_track) == 16

    # Test 24-bit calculation
    mock_track.BitRate = 2116.8
    assert _calculate_bit_depth(mock_track) == 24

    # Test 32-bit calculation
    mock_track.BitRate = 2822.4
    assert _calculate_bit_depth(mock_track) == 32
