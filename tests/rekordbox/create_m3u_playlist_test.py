from unittest.mock import Mock

import pytest
from pyrekordbox import xml

from audio_conversion_tools.rekordbox.create_m3u_playlist import create_m3u_playlist


@pytest.fixture
def mock_tracks():
    track1 = Mock(spec=xml.Track)
    track1.Location = "Music/track1.mp3"

    track2 = Mock(spec=xml.Track)
    track2.Location = "Music/folder/track2.wav"

    track3 = Mock(spec=xml.Track)
    track3.Location = "Music/track3.aiff"

    return [track1, track2, track3]


def test_create_m3u_playlist(mock_tracks, tmp_path):
    playlist_path = tmp_path / "test_playlist.m3u"
    create_m3u_playlist(mock_tracks, playlist_path)

    assert playlist_path.exists()
    content = playlist_path.read_text().splitlines()

    assert len(content) == 3
    assert content[0] == "/Music/track1.mp3"
    assert content[1] == "/Music/folder/track2.wav"
    assert content[2] == "/Music/track3.aiff"


def test_create_m3u_playlist_single_track(tmp_path):
    track = Mock(spec=xml.Track)
    track.Location = "Music/single_track.mp3"

    playlist_path = tmp_path / "single_track.m3u"
    create_m3u_playlist([track], playlist_path)

    assert playlist_path.exists()
    content = playlist_path.read_text().splitlines()

    assert len(content) == 1
    assert content[0] == "/Music/single_track.mp3"


def test_create_m3u_playlist_empty(tmp_path):
    playlist_path = tmp_path / "empty_playlist.m3u"
    create_m3u_playlist([], playlist_path)

    assert playlist_path.exists()
    content = playlist_path.read_text()

    assert content == ""


def test_create_m3u_playlist_with_spaces(tmp_path):
    track = Mock(spec=xml.Track)
    track.Location = "Music/Artist Name/Track Name.mp3"

    playlist_path = tmp_path / "playlist with spaces.m3u"
    create_m3u_playlist([track], playlist_path)

    assert playlist_path.exists()
    content = playlist_path.read_text().splitlines()

    assert len(content) == 1
    assert content[0] == "/Music/Artist Name/Track Name.mp3"


def test_create_m3u_playlist_nested_directory(tmp_path):
    nested_dir = tmp_path / "playlists" / "subdirectory"
    nested_dir.mkdir(parents=True)

    track = Mock(spec=xml.Track)
    track.Location = "Music/track.mp3"

    playlist_path = nested_dir / "nested_playlist.m3u"
    create_m3u_playlist([track], playlist_path)

    assert playlist_path.exists()
    content = playlist_path.read_text().splitlines()

    assert len(content) == 1
    assert content[0] == "/Music/track.mp3"
