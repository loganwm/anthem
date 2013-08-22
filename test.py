import MusicStructures
import MusicBackend
import tagger
import pygame

from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon

album = MusicStructures.Album()

track = MusicStructures.Track(filepath="./samples/illusive.mp3")
second_track = MusicStructures.Track(filepath="./samples/illusive.mp3", title="Hello World", track_number="10")
third_track = MusicStructures.Track(filepath="./samples/illusive.mp3", title="Fuck You", track_number="1", artist="Kanye West")

album.addTrack(track)
album.addTrack(second_track)
album.addTrack(third_track)

album.printAll()

db = MusicBackend.MusicDatabase("music.db")
db.start()
#db.updateTrack(track)
#db.addTrack(track)
#db.getAllTracks()

print "------------------------"
#db.importFile("./samples/lutece.mp3")
print "------------------------"
#db.importFile("./samples/frank1.mp3")
print "------------------------"
#db.importFile("./samples/frank2.mp3")
print "------------------------"
#db.importFile("./samples/day.mp3")
print "------------------------"
#db.importFile("./samples/acdc.ogg")

tracks = db.importDirectory("testroot")

print "------------------"

#db.getAllTracks()
#albums = db.getAllAlbums()
albums = db.search("byalbum:poetry")

for album_name in albums:
	print album_name
	#albums[album_name].printAll()

#player = MusicBackend.MusicPlayer()
#player.sendMessage("{\"type\":\"PING\"}\n")

tracks = db.search("bytitle:love")
for track in tracks:
	print track.title

db.save()