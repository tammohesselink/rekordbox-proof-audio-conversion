from unittest import mock

import pytest

from audio_conversion_tools.cli.convert_to_rekordbox_playable import main


@pytest.fixture
def mock_dependencies():
    with (
        mock.patch(
            "audio_conversion_tools.cli.convert_to_rekordbox_playable.convert_aiff_to_16_bit"
        ) as mock_convert_aiff,
        mock.patch(
            "audio_conversion_tools.cli.convert_to_rekordbox_playable.convert_lossless_to_aiff"
        ) as mock_convert_lossless,
        mock.patch("audio_conversion_tools.cli.convert_to_rekordbox_playable.argparse.ArgumentParser") as mock_parser,
    ):
        mock_args = mock.Mock()
        mock_args.recursive = False
        mock_parser_instance = mock.Mock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance

        yield {
            "convert_aiff": mock_convert_aiff,
            "convert_lossless": mock_convert_lossless,
            "parser": mock_parser,
            "args": mock_args,
        }


def test_convert_to_rekordbox_non_recursive(mock_dependencies):
    mock_dependencies["args"].recursive = False

    main()

    mock_dependencies["convert_aiff"].assert_called_once_with(recursive=False)
    mock_dependencies["convert_lossless"].assert_called_once_with(recursive=False)


def test_convert_to_rekordbox_recursive(mock_dependencies):
    mock_dependencies["args"].recursive = True

    main()

    mock_dependencies["convert_aiff"].assert_called_once_with(recursive=True)
    mock_dependencies["convert_lossless"].assert_called_once_with(recursive=True)


def test_convert_to_rekordbox_argument_parsing(mock_dependencies):
    main()

    mock_dependencies["parser"].assert_called_once_with(description="Convert AIFF files to 16-bit format.")
    parser_instance = mock_dependencies["parser"].return_value
    parser_instance.add_argument.assert_called_once_with(
        "--recursive", action="store_true", help="Enable recursive mode to process subdirectories."
    )
    parser_instance.parse_args.assert_called_once()
