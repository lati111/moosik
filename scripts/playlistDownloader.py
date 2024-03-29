import os ,csv, sys, string, random, shutil, re, json

from bs4 import BeautifulSoup
import requests, subprocess

from tkinter import *
from tkinter.ttk import *

from pytube import Playlist
import yt_dlp

from moviepy.video.io.VideoFileClip import VideoFileClip


def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__
    next = True
    
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def runCommand(commandArray):
    result = subprocess.run(
        commandArray, 
        stdout=subprocess.PIPE
    )

    result = result.stdout.splitlines()
    result = result[-2]
    result = result.decode('utf-8')
    
    return result
        
class PlaylistDownloader():
    spotdlDataSavedPattern = re.compile(r"\b(Saved) [0-9]+ \b(songs to backup/spotDL/)[a-zA-Z0-9 ]+\b(.spotdl)")    
    SAVE_PATH = os.getcwd() + '/backup'
    PLAYLIST_PATH = os.getcwd() + '/playlists'
    TEMP_PATH = os.getcwd() + '/processing'
    MUSIC_PATH = os.getcwd() + '/music'
    playlistTitle = ""
    counterText = None
    current = 0
    total = 0
    urlInput = None
    playlists = []
    gui = None
    
    def __init__(self):
        self.playlists = []
        self.counterText = StringVar()
        with open(r"data\playlists.csv", encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile, skipinitialspace=True)
            for row in reader:
                self.playlists.append(row)
    
    def progressCounter(self, prefix):
        self.current = self.current + 1
        self.counterText.set(prefix + " " + str(self.current) +' / '+str(self.total))
        self.gui.window.update() 
    
    def processYoutubeVideo(self, d):
        if d['status'] == 'finished':
            self.progressCounter("downloading")
                
    def downloadPlaylist(self, title, url, source):
        # initialise GUI
        self.gui.clearWindow()
        Label(self.gui.window, text = 'Downloading Playlist: '+ title, font =('Verdana', 15)).pack(side = TOP, pady = 10, expand=True)
        print("Downloading playlist: " + title + "...")
        self.playlistTitle = title
        
        # load load counter
        playlist_path = "playlists/"+title
        self.counterText.set('initializing')
        Label(self.gui.window, textvariable= self.counterText, font =('Verdana', 10)).pack(side = TOP, pady = 10)
        self.gui.window.update() 
        
        # check if playlist directory exists
        if not os.path.isdir(playlist_path):
            os.makedirs(playlist_path)
        
        # download songs
        self.current = 0
        match source:
            case "youtube":
                self.downloadYoutubePlaylist(url)

                print("converting to mp3")
                self.current = 0
                self.convertPlaylist()
            case "spotify":
                self.downloadSpotifyPlaylist(url)
                
        print("playlist downloaded")
        self.gui.openPlaylistDownloader()
          
    def downloadYoutubePlaylist(self, url):
        self.SAVE_PATH = os.getcwd() + '/backup/' + self.playlistTitle
        self.PLAYLIST_PATH = os.getcwd() + '/playlists/' + self.playlistTitle
        self.TEMP_PATH = os.getcwd() + '/processing/' + self.playlistTitle
        
        ydl_opts = {
            'outtmpl': self.SAVE_PATH + '/%(title)s.%(ext)s',
            'format': 'mp4',
            'progress_hooks': [self.processYoutubeVideo],
            'writethumbnail': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
        }
        
        # set counter
        playlist = Playlist(url)
        self.total = len(playlist.video_urls)
        self.counterText.set('downloading 0 / '+str(self.total))
        self.gui.window.update() 

        # download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
    
    def downloadSpotifyPlaylist(self, url):
        self.counterText.set('scraping playlist')
        self.gui.window.update() 
        
        self.SAVE_PATH = 'backup/spotDL/' + self.playlistTitle + '.spotdl'
        self.PLAYLIST_PATH = 'playlists/' + self.playlistTitle + '/'
        output = runCommand(['spotdl', 'save', url, '--save-file', self.SAVE_PATH])
        print(output)
        
        if self.spotdlDataSavedPattern.match(output):
            with open(self.SAVE_PATH, "r") as metaFile:
                data = metaFile.read()
                data = json.loads(data)
                
                self.total = len(data)
                self.counterText.set('downloading 0 / '+str(self.total))
                self.gui.window.update() 
                
                blockPrint()
                for song in data:
                    runCommand(['spotdl', 'download', song['url'], '--output', self.PLAYLIST_PATH + '{title}'])
                    self.progressCounter("downloading")
                enablePrint()
        else:
            print("failed")
      
    def convertPlaylist(self):
        for filename in os.listdir(self.SAVE_PATH):
            f = os.path.join(self.SAVE_PATH, filename)
            if os.path.isfile(f):
                if ".mp4" not in filename:
                    continue
                
                mp3_path = os.path.join(self.PLAYLIST_PATH,filename).replace(".mp4", ".mp3")
                if os.path.isfile(mp3_path):
                    continue
                
                tempName = get_random_string(12)
                oldMp4Path = os.path.join(self.TEMP_PATH, filename)
                newMp4Path = os.path.join(self.TEMP_PATH, tempName + ".mp4")
                newMp3Path = os.path.join(self.TEMP_PATH,tempName + ".mp3")
                if not os.path.isdir(self.TEMP_PATH):
                    os.mkdir(self.TEMP_PATH)
                    
                shutil.copy2(f, oldMp4Path, follow_symlinks=False)
                os.rename(oldMp4Path, newMp4Path)
                
                blockPrint()
                video = VideoFileClip(newMp4Path)
                video.audio.write_audiofile(newMp3Path)
                enablePrint()
                
                os.rename(newMp3Path, os.path.join(self.PLAYLIST_PATH,filename.replace(".mp4", ".mp3")))
                
                self.progressCounter('converting')
                
    def createPlaylistOption(self, title, url, source):
        match source:
            case "youtube":
                Button(
                    self.gui.window, 
                    text = title + ' (youtube)', 
                    width='40', 
                    command= 
                    lambda: self.downloadPlaylist(title, url, "youtube")
                ).pack(side = TOP, padx= 20)
            case "spotify":
                Button(
                    self.gui.window, 
                    text = title + ' (spotify)', 
                    width='40', 
                    command= 
                    lambda: self.downloadPlaylist(title, url, "spotify")
                ).pack(side = TOP, padx= 20)
 
    def addNewPlaylist(self):
        url = self.urlInput.get()
        title = ""
        source = ""
        
        if "https://www.youtube.com" in url:
            playlist = Playlist(url)
            title = playlist.title
            source = "youtube"
        elif "https://open.spotify.com" in url:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find("h1").text
            source = "spotify"
            
        List = [title, url, source]
        self.playlists.append(List)
        
        with open(r"data\playlists.csv", 'a', newline='\n') as f_object:
            writer_object = csv.writer(f_object)
            writer_object.writerow("")
            writer_object.writerow(List)
            f_object.close()

        self.openPlaylistList()
    
    def openNewPlaylist(self):
        self.gui.clearWindow()
        self.gui.insertBanner("New Playlist", self.openPlaylistList)
        Label(self.gui.window, text = 'Please link your playlist', font =('Verdana', 10)).pack(side = TOP, pady = 10)
        self.urlInput = Entry(self.gui.window, width='45')
        self.urlInput.pack(side = TOP, padx = 20, pady=10, expand=True)
        Button(self.gui.window, text = "Add", width='15', command=self.addNewPlaylist).pack(side = TOP, padx= 40, pady = 10)
    
    def openPlaylistList(self):
        self.gui.clearWindow()
        self.gui.insertBanner("Playlist Downloader", self.gui.openMainMenu)
        Label(self.gui.window, text = 'Select a playlist', font =('Verdana', 10)).pack(side = TOP, pady = 10)
        Button(self.gui.window, text = "New Playlist", width='25', command=self.openNewPlaylist).pack(side = TOP, padx= 40)
        
        for playlist in self.playlists[1:]:
            if playlist: #check if empty
                self.createPlaylistOption(playlist[0], playlist[1], playlist[2])
    
    def guiStart(self, gui):
        self.gui = gui
        self.openPlaylistList()
              
    def getPlaylists(self):
        return self.playlists