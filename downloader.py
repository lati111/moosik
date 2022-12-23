import os, shutil
import mutagen.id3  
from pytube import Playlist

from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from string import digits
import requests

import eyed3
from eyed3.id3.frames import ImageFrame

from colorama import Fore, Back, Style

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__
    
def getSong(video, fileName, songTitle, gameSeries, gameTitle):
    try:
        video_path = "processing/"+fileName+".mp4"
        music_path = "songs/"+fileName+".mp3"
            
        if not os.path.isfile(music_path):
            # download cover
            imgpath = 'covers/'+gameSeries+'_'+gameTitle+'.jpg'        
            if not os.path.isfile(imgpath):   
                img_data = requests.get(video.thumbnail_url).content
                with open(imgpath, 'wb') as handler:
                    handler.write(img_data)
            
            # download video
            if not os.path.isfile(video_path):
                print(Fore.RESET+"downloading video...")
                video.streams.filter(progressive=True, file_extension='mp4').first().download("processing/", fileName+".mp4", None, 1)
                print(Fore.LIGHTGREEN_EX + "downloaded video file")
            
            # convert to mp3
            print(Fore.RESET + "generating mp3...")
            blockPrint()
            video = VideoFileClip(os.path.join(video_path))
            video.audio.write_audiofile(os.path.join(music_path))
            enablePrint()
            
            # add metadata
            with open(music_path, 'r+b') as file:
                meta = mutagen.File(file, easy=True)
                meta['title'] = songTitle
                meta['album'] = gameTitle
                meta['artist'] = gameSeries
                meta['albumArtist'] = gameSeries
                meta.save(file)
        
            # set mp3 cover image
            song = eyed3.load(music_path)
            if (song.tag == None):
                song.initTag()
            song.tag.images.set(ImageFrame.FRONT_COVER, open(imgpath,'rb').read(), 'image/jpg')
            song.tag.save(version=eyed3.id3.ID3_V2_3)
            
            print(Fore.LIGHTGREEN_EX + "generated " + fileName)
        else: 
            print(Fore.LIGHTGREEN_EX + "mp3 already exists, skipping...")
        print(Style.RESET_ALL)
    except Exception as e: 
        print(Fore.RED + e)
        print(Style.RESET_ALL)
    
def getSong_format(gameSeries, gameTitle, preText, postText, video):
    songTitle = video.title

    # format song name
    songTitle = songTitle.replace(preText, '')
    songTitle = songTitle.replace(postText, '')
    songTitle = songTitle.replace(".", '')
    songTitle = songTitle.replace("-", '')
    songTitle = songTitle.replace("/", '')
    remove_digits = str.maketrans('', '', digits)
    songTitle = songTitle.translate(remove_digits)
    
    # remove spaces
    prefixed = 0
    while prefixed == 0:
        if songTitle[0] == ' ':
            songTitle = songTitle[1:]
        else:
            prefixed = 1 

    fileName = songTitle + " (" + gameSeries + " " + gameTitle + ")"
    getSong(video, fileName, songTitle, gameTitle, gameSeries)

def getSong_custom(songTitle, gameSeries, gameTitle, video):
    fileName = songTitle + " (" + gameSeries + " " + gameTitle + ")"
    getSong(video, fileName, songTitle, gameSeries, gameTitle)
    
def saveFormats(data):
    with open("storage/format.txt", "w") as txt_file:
        string = ""
        for format in data:
            arr = ""
            first = 1
            for entry in format:
                if first != 1:
                    arr = arr + ","
                else:
                    first = 0
                arr = arr + entry
            string = string + arr + "|"
        txt_file.write(string[:-1])
        
def saveCustoms(data):
    with open("storage/custom.txt", "w") as txt_file:
        string = ""
        for custom in data:
            arr = ""
            first = 1
            for entry in custom:
                if first != 1:
                    arr = arr + ","
                else:
                    first = 0
                arr = arr + entry
            string = string + arr + "|"
        txt_file.write(string[:-1])

def cleanupFolder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

if not os.path.isdir("storage"):
    os.makedirs("storage")
    
if not os.path.isdir("processing"):
    os.makedirs("processing")  
    
if not os.path.isdir("covers"):
    os.makedirs("covers")  
    
if not os.path.isdir("songs"):
    os.makedirs("songs")  

if not os.path.isfile("storage/format.txt"):
    with open("storage/format.txt", 'w') as f:
        f.write("")
        
if not os.path.isfile("storage/custom.txt"):
    with open("storage/custom.txt", 'w') as f:
        f.write("")
        
if not os.path.isfile("storage/blacklist.txt"):
    with open("storage/blacklist.txt", 'w') as f:
        f.write("")

file = open("storage/format.txt", "r")
contents = file.read()
formats = contents.split("|")
formatArr = []
for format in formats:
    formatArr.append(format.split(","))
file.close()

file = open("storage/custom.txt", "r")
contents = file.read()
customs = contents.split("|")
customArr = []
for custom in customs:
    customArr.append(custom.split(","))
file.close()

file = open("storage/blacklist.txt", "r")
contents = file.read()
blacklist = contents.split(",")
file.close()

url = input(Fore.MAGENTA+"Enter playlist URL: ")

playlist = Playlist(url)
print('Number of videos in playlist: %s' % len(playlist.video_urls))
songAmount = len(playlist.video_urls)
currSong = 0
for video in playlist.videos:
    currSong = currSong + 1
    print(str(currSong)+"/"+str(songAmount)+" SONG: "+video.title)
    foundFormat = 0
    print(len(formatArr))
    if os.path.getsize('storage/format.txt') > 0:
        for line in formatArr:
            if ((line[2] in video.title) and (line[3] in video.title)):
                getSong_format(line[0], line[1], line[2], line[3], video)
                foundFormat = 1
            else: 
                continue
            
    if os.path.getsize('storage/custom.txt') > 0: 
        if foundFormat == 0:
            for line in customArr:
                if (line[0] == video.title):
                    getSong_custom(line[1], line[2], line[3], video)
                    foundFormat = 1
                else: 
                    continue
            
    if foundFormat == 0:
        print(Fore.YELLOW + video.title + ' has no saved format')
        print(Style.RESET_ALL)
        answered = 0
        while (answered == 0):
            query = input("Input [f]ormat, input [m]anually or [s]kip song? ")
            if query == "f":
                gameSeries = input(Fore.MAGENTA+"Enter game series: ")
                gameTitle = input(Fore.MAGENTA+"Enter game title: ")
                preText = input(Fore.MAGENTA+"Enter text before song title: ")
                postText = input(Fore.MAGENTA+"Enter text after song title: ")
                formatArr.append([gameSeries, gameTitle, preText, postText])
                saveFormats(formatArr)
                getSong_format(gameSeries, gameTitle, preText, postText, video)
                answered = 1
            elif query == "m":
                songTitle = input(Fore.MAGENTA+"Enter song title: ")
                gameSeries = input(Fore.MAGENTA+"Enter game series: ")
                gameTitle = input(Fore.MAGENTA+"Enter game title: ")
                customArr.append([video.title, songTitle, gameSeries, gameTitle])
                saveCustoms(customArr)
                getSong_custom(songTitle, gameSeries, gameTitle, video)
                answered = 1
            elif query == "s":
                getSong('', '', '', '', video, blacklist)
                with open("storage/blacklist.txt", "w") as txt_file:
                    string = ""
                    for item in blacklist:
                        string = string + item + ","
                    string = string + video.title
                    txt_file.write(string)
                answered = 1
                
# cleanup
print(Fore.RESET + "cleaning up files...")
cleanupFolder("covers")
cleanupFolder("processing")
print(Fore.LIGHTGREEN_EX + "finished downloading playlist!")