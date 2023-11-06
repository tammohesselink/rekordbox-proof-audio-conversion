import os

from audio_conversion_tools.convert_audio import convert_aif_to_16bit, convert_wav_to_16bit, get_file_info

TEST_WAV_LOCATION = "tests/test_audio/silence.wav"
TEST_AIFF_LOCATION = "tests/test_audio/silence.aiff"

TEST_TEMP_WAV_LOCATION = "tests/test_audio/silence_temp.wav"
TEST_TEMP_AIFF_LOCATION = "tests/test_audio/silence_temp.aiff"


def test_convert_wav():
    assert convert_wav_to_16bit(
        TEST_WAV_LOCATION,
    )

    original_sample_rate, original_bit_rate = get_file_info(TEST_TEMP_WAV_LOCATION)
    converted_sample_rate, converted_bit_rate = get_file_info(TEST_WAV_LOCATION)

    assert original_sample_rate == 88200
    assert original_bit_rate == 32
    assert converted_sample_rate == 44100
    assert converted_bit_rate == 16

    os.rename(TEST_TEMP_WAV_LOCATION, TEST_WAV_LOCATION)


def test_convert_aiff():
    assert convert_aif_to_16bit(
        TEST_AIFF_LOCATION,
    )

    original_sample_rate, original_bit_rate = get_file_info(TEST_TEMP_AIFF_LOCATION)
    converted_sample_rate, converted_bit_rate = get_file_info(TEST_AIFF_LOCATION)

    assert original_sample_rate == 88200
    assert original_bit_rate == 32
    assert converted_sample_rate == 44100
    assert converted_bit_rate == 16

    os.rename(TEST_TEMP_AIFF_LOCATION, TEST_AIFF_LOCATION)
