from setuptools import setup, find_packages

setup(
    name='spotify_to_mp3',
    version='1.0.0',
    description='A tool to download Spotify playlists as MP3 files',
    author='Haim Daniel',
    packages=find_packages(),
    install_requires=[
        'spotipy',
        'configparser',
        'youtube_dl',
        'youtube_search',
        'yt_dlp',
        'ffprobe',
        'ffmpeg',
    ],
    entry_points={
        'console_scripts': [
            'spotify_to_mp3=spotify_to_mp3.spotify_to_mp3:main',
        ],
    },
)