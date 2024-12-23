import csv

import pytest

from audio_conversion_tools.rekordbox.revert_conversion import restore_files_from_csv


@pytest.fixture
def archive_folder(tmp_path):
    folder = tmp_path / "archive"
    folder.mkdir()
    return folder


@pytest.fixture
def destination_folder(tmp_path):
    folder = tmp_path / "destination"
    folder.mkdir()
    return folder


@pytest.fixture
def sample_csv(archive_folder, destination_folder):
    # Create test files in archive
    (archive_folder / "test1.wav").touch()
    (archive_folder / "test2.aiff").touch()

    # Create CSV file with conversion records
    csv_path = archive_folder / "converted.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # timestamp, original_location, archive_location, input_sr, output_sr, input_bd, output_bd
        writer.writerow(
            [
                "2024-01-01 12:00:00",
                str(destination_folder / "test1.wav"),
                str(archive_folder / "test1.wav"),
                "88200",
                "44100",
                "32",
                "16",
            ]
        )
        writer.writerow(
            [
                "2024-01-01 12:00:00",
                str(destination_folder / "test2.aiff"),
                str(archive_folder / "test2.aiff"),
                "88200",
                "44100",
                "32",
                "16",
            ]
        )
    return csv_path


def test_restore_files(sample_csv, archive_folder, destination_folder):
    restore_files_from_csv(sample_csv)

    # Check files were moved to destination
    assert (destination_folder / "test1.wav").exists()
    assert (destination_folder / "test2.aiff").exists()

    # Check files were removed from archive
    assert not (archive_folder / "test1.wav").exists()
    assert not (archive_folder / "test2.aiff").exists()


def test_restore_files_missing_archive_file(archive_folder, destination_folder):
    # Create CSV with reference to non-existent file
    csv_path = archive_folder / "converted.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "2024-01-01 12:00:00",
                str(destination_folder / "missing.wav"),
                str(archive_folder / "missing.wav"),
                "88200",
                "44100",
                "32",
                "16",
            ]
        )

    # Should not raise an error for missing files
    restore_files_from_csv(csv_path)
    assert not (destination_folder / "missing.wav").exists()


def test_restore_files_invalid_csv(tmp_path):
    # Create CSV with invalid format
    csv_path = tmp_path / "invalid.csv"
    with open(csv_path, "w") as f:
        f.write("invalid,csv,format\n")

    # Should handle invalid CSV gracefully
    restore_files_from_csv(csv_path)


def test_restore_files_empty_csv(tmp_path):
    # Create empty CSV
    csv_path = tmp_path / "empty.csv"
    csv_path.touch()

    # Should handle empty CSV gracefully
    restore_files_from_csv(csv_path)


def test_restore_files_destination_exists(archive_folder, destination_folder, sample_csv):
    # Create file at destination to simulate existing file
    (destination_folder / "test1.wav").touch()

    # Should overwrite existing file
    restore_files_from_csv(sample_csv)
    assert (destination_folder / "test1.wav").exists()
    assert not (archive_folder / "test1.wav").exists()


def test_restore_files_nonexistent_csv():
    with pytest.raises(FileNotFoundError):
        restore_files_from_csv("nonexistent.csv")
