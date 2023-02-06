import os, re ,csv, sys
import requests, shutil
from csv import writer

from tkinter import *
from tkinter.ttk import *

from pytube import Playlist
from pytube import YouTube

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

from moviepy.video.io.VideoFileClip import VideoFileClip

import eyed3
from eyed3.id3.frames import ImageFrame

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def cleanupFolder(folder):
    next = True
    
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        while next:
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                next = True
            except Exception as e:
                next = False
        
class PlaylistDownloader():
    counterText = None
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
    
    def downloadVideo(self, video, destination_path):
        vidTitle = ""
        while vidTitle == "":  
            try:
                vidTitle = video.title
            except (KeyError, Exception, error):
                vidTitle = video.streams[0].title
                pass
        vidTitle = re.sub('[^a-zA-Z0-9 \n\.]', '', vidTitle)
        vidTitle = re.sub(' +', ' ', vidTitle)
        mp4_path = "processing/"+vidTitle+".mp4"
        mp3_path = destination_path + "/" + vidTitle + ".mp3"
        
        # download mp4
        if not os.path.isfile(mp3_path):
            video.streams.filter(progressive=True, file_extension='mp4').first().download("processing/", vidTitle+".mp4", None, 1)
            
            # download cover
            img_path = "processing/"+vidTitle+".jpg"
            img_data = requests.get(video.thumbnail_url).content
            with open(img_path, 'wb') as handler:
                handler.write(img_data)
            
            # convert to mp3
            blockPrint()
            video = VideoFileClip(os.path.join(mp4_path))
            video.audio.write_audiofile(os.path.join(mp3_path))
            enablePrint()
            
            # set cover
            song = eyed3.load(mp3_path)
            if (song.tag == None):
                song.initTag()
            song.tag.images.set(ImageFrame.FRONT_COVER, open(img_path,'rb').read(), 'image/jpeg')
            song.tag.save(version=eyed3.id3.ID3_V2_3)
            
            audio = MP3(mp3_path, ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass
            audio.tags.add(
                APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=open(img_path, "rb").read())
            )
            audio.save()
                
    def downloadPlaylist(self, title, url):
        # initialise GUI
        self.gui.clearWindow()
        Label(self.gui.window, text = 'Downloading Playlist: '+ title, font =('Verdana', 15)).pack(side = TOP, pady = 10, expand=True)
        print("Downloading playlist: " + title + "...")
        
        # load playlist
        playlist = Playlist(url)
        playlist_path = "playlists/"+title
        songAmount = len(playlist.video_urls)
        self.counterText.set('0 / '+str(songAmount))
        Label(self.gui.window, textvariable= self.counterText, font =('Verdana', 10)).pack(side = TOP, pady = 10)
        
        # check if playlist directory exists
        if not os.path.isdir(playlist_path):
            os.makedirs(playlist_path)
        
        # download songs
        songCount = 0
        for video in playlist.videos:
            songCount = songCount + 1
            self.downloadVideo(video, playlist_path)
            self.counterText.set(str(songCount) + ' / '+str(songAmount))   
            self.gui.window.update() 
        
        self.counterText.set("Cleaning up files...")
        self.gui.window.update() 
        cleanupFolder("processing")
        print("playlist downloaded")
        
        self.gui.openPlaylistDownloader()
            
    def createPlaylistOption(self, title, url):
        Button(self.gui.window, text = title, width='40', command= lambda: self.downloadPlaylist(title, url)).pack(side = TOP, padx= 20)
    
    def addNewPlaylist(self):
        url = self.urlInput.get()
        playlist = Playlist(url)
        List = [playlist.title, url]
        self.playlists.append(List)
        
        with open(r"data\playlists.csv", 'a', newline='\n') as f_object:
            writer_object = csv.writer(f_object)
            writer_object.writerow("")
            writer_object.writerow(List)
            f_object.close()

        self.openPlaylistList()
    
    def openNewPlaylist(self):
        self.gui.clearWindow()
        Label(self.gui.window, text = 'New Playlist', font =('Verdana', 15)).pack(side = TOP, pady = 10)
        Label(self.gui.window, text = 'Please link your youtube playlist', font =('Verdana', 10)).pack(side = TOP, pady = 10)
        self.urlInput = Entry(self.gui.window, width='45')
        self.urlInput.pack(side = TOP, padx = 20, pady=10, expand=True)
        Button(self.gui.window, text = "Add", width='15', command=self.addNewPlaylist).pack(side = TOP, padx= 40, pady = 10)
    
    def openPlaylistList(self):
        self.gui.clearWindow()
        Label(self.gui.window, text = 'Playlist Downloader', font =('Verdana', 15)).pack(side = TOP, pady = 10)
        Label(self.gui.window, text = 'Select a playlist', font =('Verdana', 10)).pack(side = TOP, pady = 10)
        Button(self.gui.window, text = "New Playlist", width='25', command=self.openNewPlaylist).pack(side = TOP, padx= 40)
        
        for playlist in self.playlists[1:]:
            self.createPlaylistOption(playlist[0], playlist[1])
    
    def guiStart(self, gui):
        self.gui = gui
        self.openPlaylistList()
              
    def getPlaylists(self):
        return self.playlists