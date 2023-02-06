import sys
import subprocess
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
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
        import mutagen
    except ImportError:
        install("mutagen")
        import mutagen
        
    try:
        import moviepy
    except ImportError:
        install("moviepy")
        import moviepy
        
    try:
        import eyed3
    except ImportError:
        install("eyed3")
        import eyed3

print("Booting up...")
dependencies()
import scripts.PlaylistDownloader as PlaylistDownloader

class GUI():
    window = tk.Tk()
    playlistPhoto = PhotoImage(file = r"assets\playlist.png").subsample(5, 5)
    
    def __init__(self):
        Label(self.window, text = 'Playlist Downloader', font =('Verdana', 15)).pack(side = TOP, pady = 10)

    def openPlaylistDownloader(self):
        downloader = PlaylistDownloader.PlaylistDownloader()
        downloader.guiStart(self)
        
    def createBtn(self, title, image, command):
        Button(self.window, text = title, image = image,compound = BOTTOM, command= command).pack(side = TOP)
        
    def clearWindow(self):
        for widget in self.window.winfo_children():
            widget.destroy()

print("Launching GUI...")
gui = GUI()
gui.createBtn("Playlist Downloader", gui.playlistPhoto, gui.openPlaylistDownloader)
gui.window.mainloop()

print("Closing...")

    
    