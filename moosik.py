import sys
import subprocess
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from subprocess import Popen, PIPE, STDOUT

import scripts.playlistDownloader as PlaylistDownloader

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def runCommand(commandArray):
    result = subprocess.run(
        commandArray, 
        stdout=subprocess.PIPE
    )

    result = result.stdout.splitlines()
    result = result[-2]
    result = result.decode('utf-8')
    
    return result

def dependencies():
    try:
        import pytube
    except ImportError:
        install("pytube")
        import pytube

    try:
        import colorama
    except ImportError:
        install("colorama")
        import colorama

    try:
        import youtube_dl
    except ImportError:
        install("youtube_dl")
        import youtube_dl
        
    try:
        import spotdl
    except ImportError:
        install("spotdl")
        import spotdl
        
    try:
        import requests
    except ImportError:
        install("requests")
        import requests
        
    try:
        import bs4
    except ImportError:
        install("bs4")
        import bs4
        
    try:
        import moviepy
    except ImportError:
        install("moviepy")
        import moviepy
        
    p = Popen(["spotdl", "--download-ffmpeg"], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    p.communicate(input='N'.encode(encoding="utf-8"))

print("Booting up...")
dependencies()

class GUI():
    window = tk.Tk()
    playlistPhoto = PhotoImage(file = r"assets\playlist.png").subsample(5, 5)
    returnImage = PhotoImage(file = r"assets\return.png").subsample(15, 15)

    def insertBanner(self, title, targetMethod):
        Button(self.window, width='25', image=self.returnImage,  command=targetMethod).place(anchor='nw')
        Label(self.window, text =title, font =('Verdana', 15)).pack(side=TOP)

    def openPlaylistDownloader(self):
        downloader = PlaylistDownloader.PlaylistDownloader()
        downloader.guiStart(self)
        
    def createBtn(self, title, image, command):
        Button(self.window, text = title, image = image,compound = BOTTOM, command= command).pack(side = TOP)
        
    def clearWindow(self):
        for widget in self.window.winfo_children():
            widget.destroy()
            
    def openMainMenu(self):
        self.clearWindow()
        Label(self.window, text = 'Playlist Downloader', font =('Verdana', 15)).pack(side = TOP)
        self.createBtn("Playlist Downloader", gui.playlistPhoto, gui.openPlaylistDownloader)

print("Launching GUI...")
gui = GUI()
gui.window.title = "Moosik"
gui.openMainMenu()
gui.window.mainloop()

print("Closing...")

    
    