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

### 2. Install dependencies

We will be installing dependencies using `uv`, the super fast Python package manager. If you do not have `uv`, I'd recommend checking this [thread](https://open.spotify.com/playlist/2FekNrO1rasjSaIndayN7O?si=66ef762c945e4f0a) to install it.

Copy and paste (and run) the following line in your terminal session to install all necessary packages.

```bash
uv venv venv && source .venv/bin/activate
uv pip install setuptools -e .
```

### 2.1 Install ffmpeg
You will be needing `ffmpeg` to convert the downloaded audio files to MP3. 
You can download it:

* Ubuntu and Debian: `sudo apt-get install ffmpeg`

* macOS: `brew install ffmpeg`

* Windows: `choco install ffmpeg`




### 3. Set up Spotify

Unfortunately, I could not find a workaround for this step - it seems like we're forced to go through the Spotify API to fetch information about playlists. But, it doesn't take long at all.

Go to the Spotify [dashboard](https://developer.spotify.com/dashboard/).  Log in. Once at the Dashboard, click the green button labeled "Create App". Don't worry - you're not signing up for anything or commiting to something from Spotify.

Here **it really doesn't matter what you put** for "App name" and "App description." 
I just put "Testing" for both.

The next section is "Redirect URIs", which is a bit more important. 
You can put anything here, but I'd recommend putting `http://localhost:8888/callback`.
The script won't be using this URL, but it's necessary to put something here.

Make sure to check "I understand and agree with Spotify's Developer Terms of Service and Design Guidelines" and click "Create".


You should see this:

![Spotify App Screen](https://miro.medium.com/max/1400/1*8c7agz6nxmez9-bm2NFCxQ.jpeg)

You will see the "Client ID" field on the left (it's redacted here). Copy and save your Client ID somewhere - you'll need it later. Click "Show client secret" under Client ID and it should show you another long list of characters. Also copy and save your Client Secret.

Next, we need your playlist URI. To do this, simply open Spotify, right-click on the playlist you want to download, hover over "Share", and click "Copy link to playlist". 

It should look something like this: `https://open.spotify.com/playlist/2FekNrO1rasjSaIndayN7O?si=6666762ba5421f0a`.

### 4. Running

Running this script is straightforward. Simply run in your terminal session:

```bash
spotify_to_mp3
```

If you run into an error saying something like "ffprobe or avprobe not found", check out this [solution](https://stackoverflow.com/questions/30770155/ffprobe-or-avprobe-not-found-please-install-one).

If all goes well, you should see your playlist beginning to download in a folder with the same name. Enjoy!

## Modifications

If you don't like inputting your Client ID and Client Secret every time, you can edit `config.ini` to set the respective variables. 


## Debugging

This script was made in the better part of an afternoon, and so it's not by far bug-free. 

Personally, I've run into no problems using this script on any of my playlists, however, your mileage may vary. The most promenant bug I've run into involves the `youtube-search` package not consistantly turning up results, and most of the time, the best solution is to simply try running the script again and giving it more chances to get the search right.
