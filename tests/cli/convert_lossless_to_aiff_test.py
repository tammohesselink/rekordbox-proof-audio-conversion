from unittest import mock

import pytest

from audio_conversion_tools.cli.convert_lossless_to_aiff import convert_lossless_to_aiff


@pytest.fixture
def mock_dependencies():
    with (
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_aiff.find_files") as mock_find_files,
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_aiff.convert_to_aiff") as mock_convert,
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_aiff.os") as mock_os,
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_aiff.input") as mock_input,
    ):
        yield {
            "find_files": mock_find_files,
            "convert": mock_convert,
            "os": mock_os,
            "input": mock_input,
        }


def test_convert_lossless_no_files_found(mock_dependencies):
    mock_dependencies["find_files"].return_value = []
    mock_dependencies["input"].side_effect = ["y"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_lossless_to_aiff(recursive=False)

    mock_dependencies["find_files"].assert_called_once_with("/test/dir", extensions=[".wav", ".flac"], recursive=False)
    mock_dependencies["convert"].assert_not_called()
    mock_dependencies["os"].remove.assert_not_called()


def test_convert_lossless_with_files(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.wav", "test2.flac"]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["y"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_lossless_to_aiff(recursive=False)

    assert mock_dependencies["convert"].call_count == 2
    mock_dependencies["convert"].assert_has_calls([mock.call("test1.wav"), mock.call("test2.flac")])
    assert mock_dependencies["os"].remove.call_count == 2
    mock_dependencies["os"].remove.assert_has_calls([mock.call("test1.wav"), mock.call("test2.flac")])


def test_convert_lossless_recursive_mode(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.wav", "test2.flac"]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["", "y"]  # First input for recursive confirmation
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_lossless_to_aiff(recursive=True)

    mock_dependencies["find_files"].assert_called_once_with("/test/dir", extensions=[".wav", ".flac"], recursive=True)
    assert mock_dependencies["convert"].call_count == 2
    assert mock_dependencies["os"].remove.call_count == 2


def test_convert_lossless_no_file_deletion(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.wav"]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["n"]  # Don't delete files
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_lossless_to_aiff(recursive=False)

    mock_dependencies["convert"].assert_called_once_with("test1.wav")
    mock_dependencies["os"].remove.assert_not_called()


def test_convert_lossless_invalid_delete_input(mock_dependencies):
    mock_dependencies["input"].side_effect = ["invalid"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    with pytest.raises(ValueError, match="Answer should be y or n"):
        convert_lossless_to_aiff(recursive=False)


def test_convert_lossless_failed_conversion(mock_dependencies):
    mock_dependencies["find_files"].return_value = ["test1.wav", "test2.flac"]
    mock_dependencies["convert"].side_effect = [True, False]  # First succeeds, second fails
    mock_dependencies["input"].side_effect = ["y"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    convert_lossless_to_aiff(recursive=False)

    assert mock_dependencies["convert"].call_count == 2
    # Only the first file should be deleted since second conversion failed
    mock_dependencies["os"].remove.assert_called_once_with("test1.wav")
