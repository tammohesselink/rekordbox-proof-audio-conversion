from audio_conversion_tools.logging import logger

def create_m3u_playlist(files, playlist_location):
    with open(playlist_location, "w") as playlist_file:
        for file in files:
            playlist_file.write("/" + file.Location + "\n")

    logger.info(f"M3U playlist '{playlist_location}' has been created.")
