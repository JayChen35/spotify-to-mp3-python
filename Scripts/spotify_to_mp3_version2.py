# Downloads a Spotify playlist into a folder of MP3 tracks
# Improved version by Omswaroop T M , 24th December 2024

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import yt_dlp
from youtube_search import YoutubeSearch
import multiprocessing
import urllib.request
from flask import Flask, request, redirect
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

app = Flask(__name__)

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'your_client_id'
SPOTIPY_CLIENT_SECRET = 'your_client_secret'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIPY_SCOPE = 'user-library-read'

sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope=SPOTIPY_SCOPE)

@app.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # You can add more operations with the Spotify client here
    return "Logged in successfully"

if __name__ == '__main__':
    app.run(port=8888)

def write_tracks(text_file: str, tracks: dict):
    with open(text_file, 'w+', encoding='utf-8') as file_out:
        while True:
            for item in tracks['items']:
                track = item.get('track', item)
                try:
                    track_url = track['external_urls']['spotify']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    album_art_url = track['album']['images'][0]['url']
                    csv_line = f"{track_name},{track_artist},{track_url},{album_art_url}\n"
                    file_out.write(csv_line)
                except UnicodeEncodeError:
                    print(f"Track named {track_name} failed due to an encoding error.")
                except KeyError:
                    print(f"Skipping track {track['name']} by {track['artists'][0]['name']} (local only?)")
            if tracks['next']:
                tracks = spotify.next(tracks)
            else:
                break

def write_playlist(username: str, playlist_id: str):
    results = spotify.user_playlist(username, playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    text_file = f"{playlist_name}.txt"
    print(f"Writing {results['tracks']['total']} tracks to {text_file}.")
    tracks = results['tracks']
    write_tracks(text_file, tracks)
    img_urls = [item['track']['album']['images'][0]['url'] for item in tracks['items']]
    return playlist_name, img_urls

def find_and_download_songs(reference_file: str):
    TOTAL_ATTEMPTS = 10
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            temp = line.split(",")
            name, artist, album_art_url = temp[0], temp[1], temp[3]
            text_to_search = f"{artist} - {name}"
            best_url = None
            attempts_left = TOTAL_ATTEMPTS
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(text_to_search, max_results=1).to_dict()
                    best_url = f"https://www.youtube.com{results_list[0]['url_suffix']}"
                    break
                except IndexError:
                    attempts_left -= 1
                    print(f"No valid URLs found for {text_to_search}, trying again ({attempts_left} attempts left).")
            if not best_url:
                print(f"No valid URLs found for {text_to_search}, skipping track.")
                continue

            download_album_art(album_art_url, name)
            download_song_from_youtube(best_url, name)
            add_album_art_to_mp3(name)

def download_album_art(album_art_url: str, name: str):
    try:
        print(f"Initiating download for Image {album_art_url}.")
        with open(f'{name}.jpg', 'wb') as f:
            f.write(urllib.request.urlopen(album_art_url).read())
    except Exception as e:
        print(f"Error downloading album art: {e}")

def download_song_from_youtube(best_url: str, name: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{name}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(best_url, download=True)
    except Exception as e:
        print(f"Error downloading song: {e}")

def add_album_art_to_mp3(name: str):
    try:
        audio = MP3(f'{name}.mp3', ID3=ID3)
        audio.add_tags()
    except error:
        pass
    try:
        with open(f"{name}.jpg", 'rb') as img_file:
            audio.tags.add(
                APIC(
                    encoding=3,  # 3 is for utf-8
                    mime="image/jpeg",
                    type=3,  # 3 is for the cover image
                    desc='Cover',
                    data=img_file.read()
                )
            )
        audio.save()
        os.remove(f"{name}.jpg")
    except Exception as e:
        print(f"Error adding album art to mp3: {e}")

def multicore_find_and_download_songs(reference_file: str, cpu_count: int):
    with open(reference_file, "r", encoding='utf-8') as file:
        lines = file.readlines()

    # Split the tasks among CPUs
    tasks = split_tasks(lines, cpu_count)

    processes = []
    for i, task in enumerate(tasks):
        p = multiprocessing.Process(target=multicore_handler, args=(task, i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def split_tasks(lines: list, cpu_count: int):
    task_size = len(lines) // cpu_count
    tasks = [lines[i * task_size:(i + 1) * task_size] for i in range(cpu_count)]
    if len(lines) % cpu_count != 0:
        tasks[-1].extend(lines[cpu_count * task_size:])
    return tasks

def multicore_handler(task: list, index: int):
    reference_filename = f"{index}.txt"
    with open(reference_filename, 'w+', encoding='utf-8') as file_out:
        file_out.writelines(task)
    find_and_download_songs(reference_filename)
    os.remove(reference_filename)

def enable_multicore(autoenable=False, maxcores=None, buffercores=1):
    native_cpu_count = multiprocessing.cpu_count() - buffercores
    if autoenable:
        return min(maxcores if maxcores else native_cpu_count, native_cpu_count)
    multicore_query = input("Enable multiprocessing (Y or N): ").lower()
    if multicore_query not in ["y", "yes"]:
        return 1
    core_count_query = int(input("Max core count (0 for all cores): "))
    return min(core_count_query if core_count_query > 0 else native_cpu_count, native_cpu_count)

if __name__ == "__main__":
    print("Please read README.md for use instructions.")
    client_id = input("Client ID: ")
    client_secret = input("Client secret: ")
    username = input("Spotify username: ")
    playlist_uri = input("Playlist URI/Link: ")
    if "https://open.spotify.com/playlist/" in playlist_uri:
        playlist_uri = playlist_uri.replace("https://open.spotify.com/playlist/", "")
    multicore_support = enable_multicore(autoenable=False, maxcores=None, buffercores=1)
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlist_name, album_art_urls = write_playlist(username, playlist_uri)
    reference_file = f"{playlist_name}.txt"
    if not os.path.exists(playlist_name):
        os.makedirs(playlist_name)
    os.rename(reference_file, f"{playlist_name}/{reference_file}")
    os.chdir(playlist_name)
    if multicore_support > 1:
        multicore_find_and_download_songs(reference_file, multicore_support)
    else:
        find_and_download_songs(reference_file)
    os.remove(reference_file)
    print("Operation complete.")