import os
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from audio_conversion_tools.cli.convert_aiff_to_16bit import convert_aiff_to_16_bit, main


@pytest.fixture
def test_directory(tmp_path):
    # Create test files
    (tmp_path / "test1.aiff").touch()
    (tmp_path / "test2.aif").touch()
    (tmp_path / "test3.wav").touch()  # Should be ignored
    
    # Create subdirectory with files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "test4.aiff").touch()
    
    return tmp_path


@pytest.fixture
def mock_file_info():
    def _mock_info(filename):
        if "test1" in str(filename):
            return 88200, 32  # Needs conversion
        elif "test2" in str(filename):
            return 44100, 16  # Already correct format
        elif "test4" in str(filename):
            return 96000, 24  # Needs conversion
        return None, None
    return _mock_info


def test_convert_aiff_non_recursive(test_directory, mock_file_info):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.get_file_info', side_effect=mock_file_info), \
         patch('audio_conversion_tools.convert_audio.convert_aif_to_16bit') as mock_convert:
        
        # Mock user input to not delete temp files
        with patch('builtins.input', return_value='n'):
            convert_aiff_to_16_bit(recursive=False)
        
        # Should only try to convert test1.aiff (test2.aif is already 16-bit)
        assert mock_convert.call_count == 1
        mock_convert.assert_called_with(str(test_directory / "test1.aiff"))


def test_convert_aiff_recursive(test_directory, mock_file_info):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.get_file_info', side_effect=mock_file_info), \
         patch('audio_conversion_tools.convert_audio.convert_aif_to_16bit') as mock_convert:
        
        # Mock user inputs for recursive confirmation and temp file deletion
        with patch('builtins.input', side_effect=['', 'n']):
            convert_aiff_to_16_bit(recursive=True)
        
        # Should try to convert test1.aiff and test4.aiff
        assert mock_convert.call_count == 2
        mock_convert.assert_any_call(str(test_directory / "test1.aiff"))
        mock_convert.assert_any_call(str(test_directory / "subdir" / "test4.aiff"))


def test_convert_aiff_with_temp_deletion(test_directory, mock_file_info):
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.get_file_info', side_effect=mock_file_info), \
         patch('audio_conversion_tools.convert_audio.convert_aif_to_16bit', return_value=True), \
         patch('os.remove') as mock_remove:
        
        # Mock user input to delete temp files
        with patch('builtins.input', return_value='y'):
            convert_aiff_to_16_bit(recursive=False)
        
        # Should try to remove temp file for test1.aiff
        mock_remove.assert_called_once_with(str(test_directory / "test1_temp.aiff"))


def test_convert_aiff_invalid_delete_input():
    with pytest.raises(ValueError, match="Answer should be y or n"):
        with patch('builtins.input', return_value='invalid'):
            convert_aiff_to_16_bit(recursive=False)


def test_main_with_recursive():
    with patch('argparse.ArgumentParser.parse_args', return_value=Mock(recursive=True)), \
         patch('audio_conversion_tools.cli.convert_aiff_to_16bit.convert_aiff_to_16_bit') as mock_convert, \
         patch('builtins.input'):  # Mock the final "press any key" input
        
        main()
        mock_convert.assert_called_once_with(recursive=True)


def test_main_without_recursive():
    with patch('argparse.ArgumentParser.parse_args', return_value=Mock(recursive=False)), \
         patch('audio_conversion_tools.cli.convert_aiff_to_16bit.convert_aiff_to_16_bit') as mock_convert, \
         patch('builtins.input'):  # Mock the final "press any key" input
        
        main()
        mock_convert.assert_called_once_with(recursive=False)


def test_convert_aiff_no_files_to_convert(test_directory):
    def mock_file_info(filename):
        return 44100, 16  # All files already in correct format
    
    with patch('os.getcwd', return_value=str(test_directory)), \
         patch('audio_conversion_tools.convert_audio.get_file_info', side_effect=mock_file_info), \
         patch('audio_conversion_tools.convert_audio.convert_aif_to_16bit') as mock_convert:
        
        with patch('builtins.input', return_value='n'):
            convert_aiff_to_16_bit(recursive=False)
        
        # Should not try to convert any files
        mock_convert.assert_not_called()


def test_convert_aiff_empty_directory(tmp_path):
    with patch('os.getcwd', return_value=str(tmp_path)), \
         patch('audio_conversion_tools.cli.convert_aiff_to_16bit.convert_aif_to_16bit') as mock_convert:
        
        with patch('builtins.input', return_value='n'):
            convert_aiff_to_16_bit(recursive=False)
        
        # Should not try to convert any files
        mock_convert.assert_not_called()
