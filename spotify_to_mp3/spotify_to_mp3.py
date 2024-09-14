# Downloads a Spotify playlist into a folder of MP3 tracks
# Jason Chen, 21 June 2020

import multiprocessing
import os
import pathlib
import urllib.request

import spotipy
import yt_dlp
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch


# **************PLEASE READ THE README.md FOR USE INSTRUCTIONS**************
def write_tracks(client, text_file: str, tracks: dict):
    # This includes the name, artist, and spotify URL.
    # A comma delimits each field and a newline delimiting each track.
    with open(text_file, 'w+', encoding='utf-8') as file_out:
        while True:
            for item in tracks['items']:
                if 'track' in item:
                    track = item['track']
                else:
                    track = item
                try:
                    track_url = track['external_urls']['spotify']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name'] or 'Unknown Artist'
                    album_art_url = track['album']['images'][0]['url']
                    csv_line = (
                        track_name
                        + ","
                        + track_artist
                        + ","
                        + track_url
                        + ","
                        + album_art_url
                        + "\n"
                    )
                    try:
                        file_out.write(csv_line)
                    except (
                        UnicodeEncodeError
                    ):  # Most likely caused by non-English song names
                        print(
                            "Track named {} failed due to an encoding error. This is \
                            most likely due to this song having a non-English name.".format(
                                track_name
                            )
                        )
                except KeyError:
                    print(
                        u'Skipping track {0} by {1} (local only?)'.format(
                            track['name'], track['artists'][0]['name']
                        )
                    )
            # 1 page = 50 results, check if there are more pages
            if tracks['next']:
                tracks = client.next(tracks)
            else:
                break


def get_playlist_id(playlist_uri: str) -> str:
    assert playlist_uri.startswith("https://open.spotify.com/playlist/")
    return playlist_uri.split('https://open.spotify.com/playlist/')[1].split('?')[0]


def write_playlist(client, playlist_uri: str):
    playlist_id = get_playlist_id(playlist_uri)
    results = client.playlist(playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    text_file = u'{0}.txt'.format(playlist_name, ok='-_()[]{}')
    print(u'Writing {0} tracks to {1}.'.format(results['tracks']['total'], text_file))
    tracks = results['tracks']
    write_tracks(client, text_file, tracks)

    img_urls = []
    for item in tracks['items']:
        img_urls.append(item['track']['album']['images'][0]['url'])
    return playlist_name, img_urls


def find_and_download_songs(reference_file: str):
    total_attempts = 10
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            temp = line.split(",")
            name, artist, album_art_url = temp[0], temp[1], temp[3]
            text_to_search = artist + " - " + name
            best_url = None
            attempts_left = total_attempts
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(
                        text_to_search, max_results=1
                    ).to_dict()
                    best_url = "https://www.youtube.com{}".format(
                        results_list[0]['url_suffix']
                    )
                    break
                except IndexError:
                    attempts_left -= 1
                    print(
                        "No valid URLs found for {}, trying again ({} attempts left).".format(
                            text_to_search, attempts_left
                        )
                    )
            if best_url is None:
                print(
                    "No valid URLs found for {}, skipping track.".format(text_to_search)
                )
                continue

            print("Initiating download for Image {}.".format(album_art_url))
            f = open('{}.jpg'.format(name), 'wb')
            f.write(urllib.request.urlopen(album_art_url).read())
            f.close()

            # Run you-get to fetch and download the link's audio
            print("Initiating download for {}.".format(text_to_search))
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s',  # name the file the ID of the video
                'embedthumbnail': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'FFmpegMetadata',
                    },
                ],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info([best_url][0], download=True)

                # extract the name of the downloaded file from the info_dict
            filename = ydl.prepare_filename(info_dict)
            print(f"The downloaded file name is: {filename}")

            print('AddingCoverImage ...')
            audio = MP3(f'{filename}' + '.mp3', ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            audio.tags.add(
                APIC(
                    encoding=3,  # 3 is for utf-8
                    mime="image/jpeg",  # can be image/jpeg or image/png
                    type=3,  # 3 is for the cover image
                    desc='Cover',
                    data=open("{}.jpg".format(name), mode='rb').read(),
                )
            )
            audio.save()
            os.remove("{}.jpg".format(name))


def multicore_find_and_download_songs(reference_file: str, n_cores: int):
    """Extract songs from the reference file.

    Multiprocessed implementation of find_and_download_songs
    This method is responsible for managing and distributing the multicore workload
    """
    lines = []
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            lines.append(line)

    # Process allocation of songs per cpu
    number_of_songs = len(lines)
    songs_per_cpu = number_of_songs // n_cores

    # Calculates number of songs that don't evenly fit into the cpu list
    # i.e. 4 cores and 5 songs, one core will have to process 1 extra song
    extra_songs = number_of_songs - (n_cores * songs_per_cpu)

    # Create a list of number of songs which by index allocates it to a cpu
    # 4 core cpu and 5 songs [2, 1, 1, 1] where each item is the number of songs
    #                   Core 0^ 1^ 2^ 3^
    cpu_count_list = []
    for cpu in range(n_cores):
        songs = songs_per_cpu
        if cpu < extra_songs:
            songs = songs + 1
        cpu_count_list.append(songs)

    # Based on the cpu song allocation list split up the reference file
    index = 0
    file_segments = []
    for cpu in cpu_count_list:
        right = cpu + index
        segment = lines[index:right]
        index = index + cpu
        file_segments.append(segment)

    # Prepares all of the seperate processes before starting them
    # Pass each process a new shorter list of songs vs 1 process being handed all of the songs
    processes = []
    segment_index = 0
    for segment in file_segments:
        p = multiprocessing.Process(
            target=multicore_handler, args=(segment, segment_index)
        )
        processes.append(p)
        segment_index = segment_index + 1

    # Start the processes
    for p in processes:
        p.start()

    # Wait for the processes to complete and exit as a group
    for p in processes:
        p.join()


def multicore_handler(reference_list: list, segment_index: int):
    """A wrapper around the original find_and_download_songs method

    Ensures future compatibility, and reserves the same functionality.
    Just allows for several shorter lists to be used and cleaned up
    """
    # Create reference filename based off of the process id (segment_index)
    reference_filename = "{}.txt".format(segment_index)

    # Write the reference_list to a new "reference_file" to enable compatibility
    with open(reference_filename, 'w+', encoding='utf-8') as file_out:
        for line in reference_list:
            file_out.write(line)

    # Call the original find_and_download method
    find_and_download_songs(reference_filename)

    # Clean up the extra list that was generated
    if os.path.exists(reference_filename):
        os.remove(reference_filename)


def get_config():
    cur_dir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
    config_file = cur_dir.parent / "config.ini"
    if config_file.exists():
        import configparser

        config = configparser.ConfigParser()
        config.read(config_file)
        client_id = config["Settings"]["client_id"]
        client_secret = config["Settings"]["client_secret"]
    else:
        client_id = input("Client ID: ")
        client_secret = input("Client secret: ")
    return client_id, client_secret


def main():
    print("Please read README.md for use instructions.")
    client_id, client_secret = get_config()
    playlist_uri = input("Playlist URI: ")
    auth_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    playlist_name, album_art_urls = write_playlist(sp, playlist_uri)
    reference_file = f"{playlist_name}.txt"
    # Create the playlist folder
    if not os.path.exists(playlist_name):
        os.makedirs(playlist_name)
    os.rename(reference_file, playlist_name + "/" + reference_file)
    os.chdir(playlist_name)
    n_cores = multiprocessing.cpu_count()
    multicore_find_and_download_songs(reference_file, n_cores)
    os.remove(f'{reference_file}')
    print("Operation complete.")


if __name__ == "__main__":
    main()
