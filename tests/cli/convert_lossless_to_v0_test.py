from unittest import mock

import pytest

from audio_conversion_tools.cli.convert_lossless_to_v0 import main


@pytest.fixture
def mock_dependencies():
    with (
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_v0.convert_aif_to_mp3_v0") as mock_convert,
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_v0.os") as mock_os,
        mock.patch("audio_conversion_tools.cli.convert_lossless_to_v0.input") as mock_input,
    ):
        yield {
            "convert": mock_convert,
            "os": mock_os,
            "input": mock_input,
        }


def test_convert_v0_no_files_found(mock_dependencies):
    mock_dependencies["os"].listdir.return_value = ["test.mp3", "test.txt"]  # No convertible files
    mock_dependencies["input"].side_effect = ["y", ""]  # Delete files + exit prompt
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    main()

    mock_dependencies["convert"].assert_not_called()
    mock_dependencies["os"].remove.assert_not_called()


def test_convert_v0_with_files(mock_dependencies):
    mock_dependencies["os"].listdir.return_value = ["test1.wav", "test2.flac", "test3.aiff"]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["y", ""]  # Delete files + exit prompt
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    main()

    assert mock_dependencies["convert"].call_count == 3
    mock_dependencies["convert"].assert_has_calls(
        [mock.call("test1.wav"), mock.call("test2.flac"), mock.call("test3.aiff")]
    )
    assert mock_dependencies["os"].remove.call_count == 3
    mock_dependencies["os"].remove.assert_has_calls(
        [mock.call("test1.wav"), mock.call("test2.flac"), mock.call("test3.aiff")]
    )


def test_convert_v0_no_file_deletion(mock_dependencies):
    mock_dependencies["os"].listdir.return_value = ["test1.wav", "test2.aif"]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["n", ""]  # Don't delete files + exit prompt
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    main()

    assert mock_dependencies["convert"].call_count == 2
    mock_dependencies["os"].remove.assert_not_called()


def test_convert_v0_invalid_delete_input(mock_dependencies):
    mock_dependencies["input"].side_effect = ["invalid"]
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    with pytest.raises(ValueError, match="Answer should be y or n"):
        main()


def test_convert_v0_failed_conversion(mock_dependencies):
    mock_dependencies["os"].listdir.return_value = ["test1.wav", "test2.flac"]
    mock_dependencies["convert"].side_effect = [True, False]  # First succeeds, second fails
    mock_dependencies["input"].side_effect = ["y", ""]  # Delete files + exit prompt
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    main()

    assert mock_dependencies["convert"].call_count == 2
    # Only the first file should be deleted since second conversion failed
    mock_dependencies["os"].remove.assert_called_once_with("test1.wav")


def test_convert_v0_case_insensitive_extensions(mock_dependencies):
    mock_dependencies["os"].listdir.return_value = ["test1.WAV", "test2.AIFF", "test3.FlAc"]
    mock_dependencies["convert"].return_value = True
    mock_dependencies["input"].side_effect = ["y", ""]  # Delete files + exit prompt
    mock_dependencies["os"].getcwd.return_value = "/test/dir"

    main()

    assert mock_dependencies["convert"].call_count == 3
    mock_dependencies["convert"].assert_has_calls(
        [mock.call("test1.WAV"), mock.call("test2.AIFF"), mock.call("test3.FlAc")]
    )
