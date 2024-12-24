import os

import pytest

from audio_conversion_tools.utils import _find_files_recursively, _get_extension, find_files


@pytest.fixture
def test_directory(tmp_path):
    # Create a test directory structure:
    # test_dir/
    #   ├── file1.wav
    #   ├── file2.aiff
    #   ├── file3.txt
    #   └── subdir/
    #       ├── file4.wav
    #       └── file5.aiff

    # Create root level files
    (tmp_path / "file1.wav").touch()
    (tmp_path / "file2.aiff").touch()
    (tmp_path / "file3.txt").touch()

    # Create subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file4.wav").touch()
    (subdir / "file5.aiff").touch()

    return tmp_path


def test_find_files_non_recursive(test_directory):
    os.chdir(test_directory)
    files = find_files(".", extensions=[".wav", ".aiff"], recursive=False)

    assert len(files) == 2
    assert "./file1.wav" in files
    assert "./file2.aiff" in files
    assert "file3.txt" not in files
    assert "subdir/file4.wav" not in files
    assert "subdir/file5.aiff" not in files


def test_find_files_recursive(test_directory):
    files = find_files(test_directory, extensions=[".wav", ".aiff"], recursive=True)

    assert len(files) == 4
    assert any(f.endswith("file1.wav") for f in files)
    assert any(f.endswith("file2.aiff") for f in files)
    assert any(f.endswith("file4.wav") for f in files)
    assert any(f.endswith("file5.aiff") for f in files)
    assert not any(f.endswith("file3.txt") for f in files)


def test_find_files_empty_directory(tmp_path):
    files = find_files(tmp_path, extensions=[".wav", ".aiff"], recursive=True)
    assert len(files) == 0


def test_find_files_no_matching_extensions(test_directory):
    files = find_files(test_directory, extensions=[".mp3"], recursive=True)
    assert len(files) == 0


def test_find_files_case_insensitive(test_directory):
    # Create files with uppercase extensions
    (test_directory / "upper1.WAV").touch()
    (test_directory / "upper2.AIFF").touch()

    files = find_files(test_directory, extensions=[".wav", ".aiff"], recursive=True)

    assert any(f.endswith("upper1.WAV") for f in files)
    assert any(f.endswith("upper2.AIFF") for f in files)


def test_find_files_recursively(test_directory):
    files = _find_files_recursively(test_directory, extensions=[".wav", ".aiff"])

    assert len(files) == 4
    assert any(f.endswith("file1.wav") for f in files)
    assert any(f.endswith("file2.aiff") for f in files)
    assert any(f.endswith("file4.wav") for f in files)
    assert any(f.endswith("file5.aiff") for f in files)


def test_get_extension():
    assert _get_extension("test.wav") == ".wav"
    assert _get_extension("test.AIFF") == ".aiff"
    assert _get_extension("test.txt") == ".txt"
    assert _get_extension("test") == ""
    assert _get_extension(".hidden") == ".hidden"
    assert _get_extension("path/to/file.wav") == ".wav"
    assert _get_extension("file.with.multiple.dots.wav") == ".wav"


def test_find_files_with_dots_in_name(test_directory):
    # Create file with dots in name
    (test_directory / "file.with.dots.wav").touch()

    files = find_files(test_directory, extensions=[".wav"], recursive=True)
    assert any(f.endswith("file.with.dots.wav") for f in files)


def test_find_files_with_spaces(test_directory):
    # Create file with spaces in name
    (test_directory / "file with spaces.wav").touch()

    files = find_files(test_directory, extensions=[".wav"], recursive=True)
    assert any(f.endswith("file with spaces.wav") for f in files)


def test_find_files_empty_extensions_list(test_directory):
    files = find_files(test_directory, extensions=[], recursive=True)
    assert len(files) == 0
