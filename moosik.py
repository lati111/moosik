import sys
import subprocess
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
def dependencies():
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

class GUI():
    window = tk.Tk()
    playlistPhoto = PhotoImage(file = r"assets\playlist.png").subsample(5, 5)
    
    def __init__(self):
        Label(self.window, text = 'Playlist Downloader', font =('Verdana', 15)).pack(side = TOP, pady = 10)

    def my_command(self):
        print("Clicked!")
        
    def createBtn(self, title, image):
        Button(self.window, text = title, image = image,compound = BOTTOM, command= self.my_command).pack(side = TOP)
        
print("Booting up...")
dependencies()

print("Launching GUI...")
gui = GUI()
gui.createBtn("Playlist Downloader", gui.playlistPhoto)
gui.window.mainloop()

print("Closing...")

    
    