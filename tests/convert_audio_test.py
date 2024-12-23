import os
import shutil
from pathlib import Path

import pytest

from audio_conversion_tools.convert_audio import (
    check_bit_depth_allowed,
    check_sample_rate_allowed,
    convert_aif_to_16bit,
    convert_aif_to_mp3_v0,
    convert_to_aiff,
    convert_wav_to_16bit,
    determine_target_sample_rate,
    get_file_info,
)

TEST_FOLDER = Path(__file__).parent

TEST_WAV_32_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_32bit.wav"
TEST_AIFF_32_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_32bit.aiff"
TEST_TEMP_WAV_32_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_32bit_temp.wav"
TEST_TEMP_AIFF_32_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_32bit_temp.aiff"

TEST_WAV_16_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_16bit.wav"
TEST_AIFF_16_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_16bit.aiff"
TEST_TEMP_WAV_16_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_16bit_temp.wav"
TEST_TEMP_AIFF_16_BIT_LOCATION = TEST_FOLDER / "test_audio" / "silence_16bit_temp.aiff"


def test_get_file_info() -> None:
    sample_rate, bit_depth = get_file_info(TEST_WAV_32_BIT_LOCATION)
    assert sample_rate == 88200
    assert bit_depth == 32

    sample_rate, bit_depth = get_file_info(TEST_AIFF_32_BIT_LOCATION)
    assert sample_rate == 88200
    assert bit_depth == 32


def test_get_file_info_nonexistent_file() -> None:
    sample_rate, bit_depth = get_file_info("nonexistent.wav")
    assert sample_rate is None
    assert bit_depth is None


def test_determine_target_sample_rate() -> None:
    assert determine_target_sample_rate(44100) == 44100
    assert determine_target_sample_rate(48000) == 48000
    assert determine_target_sample_rate(88200) == 44100
    assert determine_target_sample_rate(96000) == 48000
    assert determine_target_sample_rate(192000) == 48000

    with pytest.raises(ValueError):
        determine_target_sample_rate(22050)


def test_check_sample_rate_allowed() -> None:
    assert check_sample_rate_allowed(44100) is True
    assert check_sample_rate_allowed(48000) is True
    assert check_sample_rate_allowed(88200) is False
    assert check_sample_rate_allowed(96000) is False
    assert check_sample_rate_allowed(None) is False


def test_check_bit_depth_allowed() -> None:
    assert check_bit_depth_allowed(16) is True
    assert check_bit_depth_allowed(24) is False
    assert check_bit_depth_allowed(32) is False
    assert check_bit_depth_allowed(None) is False


def test_convert_wav() -> None:
    assert convert_wav_to_16bit(TEST_WAV_32_BIT_LOCATION)

    original_sample_rate, original_bit_rate = get_file_info(TEST_TEMP_WAV_32_BIT_LOCATION)
    converted_sample_rate, converted_bit_rate = get_file_info(TEST_WAV_32_BIT_LOCATION)

    assert original_sample_rate == 88200
    assert original_bit_rate == 32
    assert converted_sample_rate == 44100
    assert converted_bit_rate == 16

    os.remove(TEST_WAV_32_BIT_LOCATION)
    os.rename(TEST_TEMP_WAV_32_BIT_LOCATION, TEST_WAV_32_BIT_LOCATION)


def test_convert_aiff() -> None:
    assert convert_aif_to_16bit(TEST_AIFF_32_BIT_LOCATION)

    original_sample_rate, original_bit_rate = get_file_info(TEST_TEMP_AIFF_32_BIT_LOCATION)
    converted_sample_rate, converted_bit_rate = get_file_info(TEST_AIFF_32_BIT_LOCATION)

    assert original_sample_rate == 88200
    assert original_bit_rate == 32
    assert converted_sample_rate == 44100
    assert converted_bit_rate == 16

    os.remove(TEST_AIFF_32_BIT_LOCATION)
    os.rename(TEST_TEMP_AIFF_32_BIT_LOCATION, TEST_AIFF_32_BIT_LOCATION)


def test_convert_wav_nonexistent_file() -> None:
    with pytest.raises(FileNotFoundError):
        convert_wav_to_16bit("nonexistent.wav")


def test_convert_aiff_nonexistent_file() -> None:
    with pytest.raises(FileNotFoundError):
        convert_aif_to_16bit("nonexistent.aiff")


def test_convert_to_aiff() -> None:
    output_name = str(TEST_WAV_32_BIT_LOCATION).replace(".wav", "_converted.aiff")
    assert convert_to_aiff(TEST_WAV_32_BIT_LOCATION, output_name)

    sample_rate, bit_depth = get_file_info(output_name)
    assert sample_rate == 44100
    assert bit_depth == 16


def test_convert_to_aiff_nonexistent_file() -> None:
    assert not convert_to_aiff("nonexistent.wav")


def test_convert_aif_to_mp3_v0() -> None:
    assert convert_aif_to_mp3_v0(TEST_AIFF_32_BIT_LOCATION)
    output_name = str(TEST_AIFF_32_BIT_LOCATION).replace(".aiff", ".mp3")
    assert Path(output_name).exists()
    os.remove(output_name)


def test_convert_aif_to_mp3_v0_nonexistent_file() -> None:
    assert not convert_aif_to_mp3_v0("nonexistent.aiff")


def test_convert_wav_already_correct_format() -> None:
    original_file_backup_path = "temp_audio"
    shutil.copy2(TEST_WAV_32_BIT_LOCATION, original_file_backup_path)

    # First convert to correct format
    assert convert_wav_to_16bit(TEST_WAV_32_BIT_LOCATION)

    # Try converting again - should return False as no conversion needed
    assert not convert_wav_to_16bit(TEST_WAV_32_BIT_LOCATION)

    # Restore original file
    os.remove(TEST_WAV_32_BIT_LOCATION)
    os.rename(original_file_backup_path, TEST_WAV_32_BIT_LOCATION)


def test_convert_aiff_already_correct_format() -> None:
    original_file_backup_path = "temp_audio"
    shutil.copy2(TEST_AIFF_32_BIT_LOCATION, original_file_backup_path)

    # First convert to correct format
    assert convert_aif_to_16bit(TEST_AIFF_32_BIT_LOCATION)

    # Try converting again - should return False as no conversion needed
    assert not convert_aif_to_16bit(TEST_AIFF_32_BIT_LOCATION)

    # Restore original file
    os.remove(TEST_AIFF_32_BIT_LOCATION)
    os.rename(original_file_backup_path, TEST_AIFF_32_BIT_LOCATION)
