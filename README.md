# Spotify to MP3 - Python

The simplest way to convert/download your Spotify playlist into MP3 files, using Python 3.

## How To Use

This code is meant to be as simple and easy-to-use as possible. Despite this, there are some setup and usage steps (such as installing necessary packages) that are necessary for this code to work. Please read this section carefully.

### 1. Clone the respository

To clone this repoistory using Git, use

```bash
git clone https://github.com/JayChen35/spotify-to-mp3-python.git
```

If you aren't familiar with Git, navigate to the top-left of this page and find the green button labeled "Clone or download". Clicking this and then click "Download ZIP". Extract the contents of the downloaded .zip file.

Open a terminal session and navigate to this folder, using `cd`.

```bash
cd spotify-to-mp3-python/
```

### 2. Installing dependencies

We will be installing dependencies using `pip`, the official Python package manager. If you do not have `pip`, I'd recommend checking this [thread](https://stackoverflow.com/questions/6587507/how-to-install-pip-with-python-3/) to install it.

Copy and paste (and run) the following line in your terminal session to install all necessary packages.

```bash
pip3 install spotipy && pip3 install youtube_dl && pip3 install youtube_search && pip3 install yt_dlp && pip3 install ffprobe && pip3 install ffmpeg
```

### 3. Setting up Spotify

Unfortunately, I could not find a workaround for this step - it seems like we're forced to go through the Spotify API to fetch information about playlists. But, it doesn't take long at all.

Go to the Spotify [dashboard](https://developer.spotify.com/dashboard/).  Log in. Once at the Dashboard, click the green button labeled "Create App". Don't worry - you're not signing up for anything or commiting to something from Spotify. Here, **it really doesn't matter what you put** for "App name" and "App description". For me, I just put "Testing" for both. Make sure to check both agreement boxes and click "Create".

You should see this:

![Spotify App Screen](https://miro.medium.com/max/1400/1*8c7agz6nxmez9-bm2NFCxQ.jpeg)

You will see the "Client ID" field on the left (it's redacted here). Copy and save your Client ID somewhere - you'll need it later. Click "Show client secret" under Client ID and it should show you another long list of characters. Also copy and save your Client Secret.

Next, we need your playlist URI. To do this, simply open Spotify, right-click on the playlist you want to download, hover over "Share", and click "Copy Spotify URI". It should look something like this: `spotify:playlist:37i9dQZEVXbJiZcmkrIHGU`. When inputting this into the script, make sure to *only input the characters after "spotify:playlist:"*. So for this example, input `37i9dQZEVXbJiZcmkrIHGU`. Save your URI somewhere handy.

Alternatively, you can find the URI as follows:
1. Right-click on the playlist you want to download
2. Click "Share"
3. Click "Embed Playlist"
4. Click "Show Code"
5. The URI is the code between "https://open.spotify.com/embed/playlist/" and the first "?"

For example in this code snippet:

```html
<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/11cPCycyvvpL0MDLO648vE?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
```

The code is 11cPCycyvvpL0MDLO648vE

### 4. Running

Running this script is straightforward. Simply run in your terminal session:

```bash
python3 spotify_to_mp3.py
```

If you run into an error saying something like "ffprobe or avprobe not found", check out this [solution](https://stackoverflow.com/questions/30770155/ffprobe-or-avprobe-not-found-please-install-one).

If all goes well, you should see your playlist beginning to download in a folder with the same name. Enjoy!

## Modifications

If you don't like inputting your Client ID, Client Secret, Username, and URI  every time, you can edit lines 96-99 in `spotify_to_mp3.py` to set the respective variables into a string containing your credentials instead of prompting with `input()`. For example, line 98 would become

```python
username = "YourUserName"
```

## Debugging

This script was made in the better part of an afternoon and so it's not, by far, bug-free. Personally, I've run into no problems using this script on any of my playlists, however, your mileage may vary. The most promenant bug I've run into involves the `youtube-search` package not consistantly turning up results, and most of the time, the best solution is to simply try running the script again and giving it more chances to get the search right.
