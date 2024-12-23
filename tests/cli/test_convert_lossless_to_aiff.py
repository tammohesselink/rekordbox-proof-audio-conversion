import os
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from audio_conversion_tools.cli.convert_lossless_to_aiff import convert_lossless_to_aiff, main


@pytest.fixture
def test_directory(tmp_path):
    # Create test files
    (tmp_path / "test1.wav").touch()
    (tmp_path / "test2.flac").touch()
    (tmp_path / "test3.mp3").touch()  # Should be ignored
    
    # Create subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "test4.wav").touch()
    (subdir / "test5.flac").touch()
    
    return tmp_path


def test_convert_lossless_non_recursive(test_directory):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.convert_to_aiff', return_value=True) as mock_convert:
        
        # Mock user input to not delete original files
        with patch('builtins.input', return_value='n'):
            convert_lossless_to_aiff(recursive=False)
        
        # Should try to convert test1.wav and test2.flac
        assert mock_convert.call_count == 2
        mock_convert.assert_any_call(str(test_directory / "test1.wav"))
        mock_convert.assert_any_call(str(test_directory / "test2.flac"))


def test_convert_lossless_recursive(test_directory):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.convert_to_aiff', return_value=True) as mock_convert:
        
        # Mock user inputs for recursive confirmation and file deletion
        with patch('builtins.input', side_effect=['', 'n']):
            convert_lossless_to_aiff(recursive=True)
        
        # Should try to convert all wav and flac files
        assert mock_convert.call_count == 4
        mock_convert.assert_any_call(str(test_directory / "test1.wav"))
        mock_convert.assert_any_call(str(test_directory / "test2.flac"))
        mock_convert.assert_any_call(str(test_directory / "subdir" / "test4.wav"))
        mock_convert.assert_any_call(str(test_directory / "subdir" / "test5.flac"))


def test_convert_lossless_with_deletion(test_directory):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.convert_to_aiff', return_value=True), \
         patch('os.remove') as mock_remove:
        
        # Mock user input to delete original files
        with patch('builtins.input', return_value='y'):
            convert_lossless_to_aiff(recursive=False)
        
        # Should try to remove original files after successful conversion
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call(str(test_directory / "test1.wav"))
        mock_remove.assert_any_call(str(test_directory / "test2.flac"))


def test_convert_lossless_failed_conversion(test_directory):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.convert_to_aiff', return_value=False), \
         patch('os.remove') as mock_remove:
        
        # Mock user input to delete original files
        with patch('builtins.input', return_value='y'):
            convert_lossless_to_aiff(recursive=False)
        
        # Should not remove files if conversion failed
        mock_remove.assert_not_called()


def test_convert_lossless_invalid_delete_input():
    with pytest.raises(ValueError, match="Answer should be y or n"):
        with patch('builtins.input', return_value='invalid'):
            convert_lossless_to_aiff(recursive=False)


def test_main_with_recursive():
    with patch('argparse.ArgumentParser.parse_args', return_value=Mock(recursive=True)), \
         patch('audio_conversion_tools.cli.convert_lossless_to_aiff.convert_lossless_to_aiff') as mock_convert, \
         patch('builtins.input'):  # Mock the final "press any key" input
        
        main()
        mock_convert.assert_called_once_with(recursive=True)


def test_main_without_recursive():
    with patch('argparse.ArgumentParser.parse_args', return_value=Mock(recursive=False)), \
         patch('audio_conversion_tools.cli.convert_lossless_to_aiff.convert_lossless_to_aiff') as mock_convert, \
         patch('builtins.input'):  # Mock the final "press any key" input
        
        main()
        mock_convert.assert_called_once_with(recursive=False)


def test_convert_lossless_empty_directory(tmp_path):
    with patch('os.getcwd', return_value=str(tmp_path)), \
         patch('audio_conversion_tools.convert_audio.convert_to_aiff') as mock_convert:
        
        with patch('builtins.input', return_value='n'):
            convert_lossless_to_aiff(recursive=False)
        
        # Should not try to convert any files
        mock_convert.assert_not_called()


def test_convert_lossless_no_matching_files(test_directory):
    # Remove all .wav and .flac files
    for f in test_directory.glob("**/*.wav"):
        f.unlink()
    for f in test_directory.glob("**/*.flac"):
        f.unlink()
    
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.convert_to_aiff') as mock_convert:
        
        with patch('builtins.input', return_value='n'):
            convert_lossless_to_aiff(recursive=False)
        
        # Should not try to convert any files
        mock_convert.assert_not_called()
