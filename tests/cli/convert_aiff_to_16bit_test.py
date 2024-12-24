from unittest import mock

import pytest

from audio_conversion_tools.cli.convert_aiff_to_16bit import convert_aiff_to_16_bit


@pytest.fixture
def mock_dependencies():
    with (
        mock.patch("audio_conversion_tools.cli.convert_aiff_to_16bit.find_files") as mock_find_files,
        mock.patch("audio_conversion_tools.cli.convert_aiff_to_16bit.get_file_info") as mock_get_file_info,
        mock.patch("audio_conversion_tools.cli.convert_aiff_to_16bit.convert_aif_to_16bit") as mock_convert,
        mock.patch("audio_conversion_tools.cli.convert_aiff_to_16bit.os") as mock_os,
        mock.patch("audio_conversion_tools.cli.convert_aiff_to_16bit.input") as mock_input,
    ):
        yield {
            "find_files": mock_find_files,
            "get_file_info": mock_get_file_info,
            "convert": mock_convert,
            "os": mock_os,
            "input": mock_input,
        }


def test_convert_aiff_no_files_to_convert(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.aiff", "test2.aiff"]
    # All files are already 16-bit, 44.1kHz
    mock_dependencies["get_file_info"].return_value = (44100, 16)
    mock_dependencies["input"].side_effect = ["y"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_aiff_to_16_bit(recursive=False)

    mock_dependencies["find_files"].assert_called_once_with("/test/dir", extensions=[".aif", ".aiff"], recursive=False)
    mock_dependencies["convert"].assert_not_called()
    mock_dependencies["os"].remove.assert_not_called()


def test_convert_aiff_with_files_to_convert(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.aiff", "test2.aiff"]
    # First file is 32-bit, second is 16-bit
    mock_dependencies["get_file_info"].side_effect = [(44100, 32), (44100, 16)]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["y"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_aiff_to_16_bit(recursive=False)

    mock_dependencies["convert"].assert_called_once_with("test1.aiff")
    mock_dependencies["os"].remove.assert_called_once_with("test1_temp.aiff")


def test_convert_aiff_recursive_mode(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.aiff", "test2.aiff"]
    mock_dependencies["get_file_info"].side_effect = [(44100, 32), (44100, 32)]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["", "y"]  # First input for recursive confirmation
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_aiff_to_16_bit(recursive=True)

    mock_dependencies["find_files"].assert_called_once_with("/test/dir", extensions=[".aif", ".aiff"], recursive=True)
    assert mock_dependencies["convert"].call_count == 2
    assert mock_dependencies["os"].remove.call_count == 2


def test_convert_aiff_no_temp_file_deletion(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.aiff"]
    mock_dependencies["get_file_info"].return_value = (44100, 32)
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["n"]  # Don't delete temp files
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_aiff_to_16_bit(recursive=False)

    mock_dependencies["convert"].assert_called_once_with("test1.aiff")
    mock_dependencies["os"].remove.assert_not_called()


def test_convert_aiff_invalid_delete_input(mock_dependencies):
    mock_dependencies["input"].side_effect = ["invalid"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    with pytest.raises(ValueError, match="Answer should be y or n"):
        convert_aiff_to_16_bit(recursive=False)
