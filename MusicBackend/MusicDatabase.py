import os
import sqlite3
import tagger
import re
import MusicStructures
import urllib

class MusicDatabase:
	def __init__(self, filename):
		self.filename = filename
	
	def start(self):
		self.connection = sqlite3.connect(self.filename)
		self.cursor = self.connection.cursor()

		print "Connecting to database..."

		self.cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='tracks';''')
		result = self.cursor.fetchone()
		
		#create the tracks table
		if result == None:
			print "Table 'tracks' doesn't exist. Creating..."
			self.cursor.execute('''
				CREATE TABLE tracks
				(
					id INTEGER PRIMARY KEY UNIQUE,
					filepath TEXT UNIQUE NOT NULL,
					title TEXT NOT NULL,
					artist TEXT NOT NULL,
					album TEXT NOT NULL,
					track_number TEXT NOT NULL
				)
			''')

	def save(self):
		print "Saving the database..."

		self.connection.commit()

	def stop(self):
		print "Disconnecting from database..."

		self.connection.close()

	def addTrack(self, track):
		try:
			self.cursor.execute('''
					INSERT INTO tracks
					(
						'filepath',
						'title',
						'artist',
						'album',
						'track_number'
					) VALUES
					(
						?,
						?,
						?,
						?,
						?
					)
				''', [track.filepath, track.title, track.artist, track.album, track.track_number])
		except:
			print "An error ocurred adding track or the track already exists in the database"
			return
		
		print self.cursor.lastrowid
		track.id = self.cursor.lastrowid

	def updateTrack(self, track):
		if track.id == "":
			print "Track needs db ID in order to be updated."
			return
			
		self.cursor.execute('''
				UPDATE tracks SET
					'filepath'=?,
					'title'=?,
					'artist'=?,
					'album'=?
					'track_number'=?
				WHERE
					'id'=?
			''', [track.filepath, track.title, track.artist, track.album, track.track_number, track.id])

	def clearTracks(self):
		self.cursor.execute('''
				DELETE FROM tracks
			''')
			
	def getAllTracks(self):
		tracks = []
	
		self.cursor.execute('''
				SELECT
					title, artist, album, filepath, track_number
				FROM tracks''')

		for row in self.cursor:
			track = MusicStructures.Track()
			track.title = row[0]
			track.artist = row[1]
			track.album = row[2]
			track.filepath = row[3]
			track.track_number = row[4]
			
			tracks.append(track)
			
		return tracks

	def getAllAlbums(self):
		albums = {}
	
		self.cursor.execute('''
				SELECT
					title, artist, album, filepath, track_number
				FROM tracks''')

		for row in self.cursor:
			if not row[2] in albums:
				albums[row[2]] = MusicStructures.Album(title=row[2])
			
			track = MusicStructures.Track()
			track.title = row[0]
			track.artist = row[1]
			track.album = row[2]
			track.filepath = row[3]
			track.track_number = row[4]
			
			albums[row[2]].addTrack(track)

		return albums

	def importDirectory(self, filepath):
		tracks = []

		for root, dirs, files in os.walk(filepath):
			for name in files:
				#print os.path.abspath(os.path.join(root, name))
				file = os.path.abspath(os.path.join(root, name))
				track = self.importFile(file)
				
				if track != None:
					tracks.append(track)
		
		return tracks
	
	def importFile(self, filepath):
		extension = filepath[-3:]

		track = None

		if extension == "mp3":
			track = self.importMP3File(filepath)
		elif extension == "ogg":
			track = self.importOGGFile(filepath)

		if track != None:
			self.addTrack(track)
			return track

	def importMP3File(self, filepath):
		id3 = tagger.ID3v2(filepath)

		frames = {}
		
		for frame in id3.frames:
			if len(frame.strings) != 0:
				frames[frame.fid] = frame.strings[0]
				#print frame.fid + " : " + frames[frame.fid]
		
		track = MusicStructures.Track()

		track.filepath = urllib.quote(filepath)
		if "TIT2" in frames: track.title = frames["TIT2"]
		if "TALB" in frames: track.album = frames["TALB"]
		if "TPE1" in frames: track.artist = frames["TPE1"]
		if "TRCK" in frames:
			track_number = frames["TRCK"]
			
			matches = re.match("([0-9]+)/[0-9]+", track_number)
		
			if matches != None: #match is of form num1/totaltracks
				track.track_number = matches.group(1)
			else: #this is a base track number match
				track.track_number = track_number

		return track

	def importOGGFile(self, filepath):
			id3 = tagger.ID3v2(filepath)

			frames = {}
			
			for frame in id3.frames:			
				if len(frame.strings) != 0:
					frames[frame.fid] = frame.strings[0]
					print frame.fid + " : " + frames[frame.fid]
	

	def search(self, query):
		tracks = []

		parts = query.split(":", 2)
		
		if len(parts) != 2:
			print "Invalid query"
			return []
		
		if parts[0] == "bytitle":
			tracks = self.searchByTitle(parts[1])
		elif parts[0] == "byalbum":
			tracks = self.searchByAlbum(parts[1])
	
		return tracks

	def searchByTitle(self, query):
		tracks = []

		param = "%"+query+"%"
	
		print param
	
		self.cursor.execute(r'''
				SELECT
					id, title, artist, album, filepath, track_number
				FROM tracks
				WHERE
					title LIKE ? ''', [param])

		for row in self.cursor:
			track = MusicStructures.Track()
			track.id = row[0]
			track.title = row[1]
			track.artist = row[2]
			track.album = row[3]
			track.filepath = row[4]
			track.track_number = row[5]
			tracks.append(track)
			
		return tracks

	def searchByArtist(self, query):
		tracks = []

		param = "%"+query+"%"
	
		print param
	
		self.cursor.execute(r'''
				SELECT
					id, title, artist, album, filepath, track_number
				FROM tracks
				WHERE
					artist LIKE ? ''', [param])

		for row in self.cursor:
			track = MusicStructures.Track()
			track.id = row[0]
			track.title = row[1]
			track.artist = row[2]
			track.album = row[3]
			track.filepath = row[4]
			track.track_number = row[5]
			tracks.append(track)
			
		return tracks

	def searchByAlbum(self, query):
		albums = {}
	
		param = "%"+query+"%"
	
		self.cursor.execute(r'''
				SELECT
					id, title, artist, album, filepath, track_number
				FROM tracks
				WHERE
					album LIKE ? ''', [param])

		for row in self.cursor:
			if not row[3] in albums:
				albums[row[3]] = MusicStructures.Album(title=row[3])
			
			track = MusicStructures.Track()
			track.id = row[0]
			track.title = row[1]
			track.artist = row[2]
			track.album = row[3]
			track.filepath = row[4]
			track.track_number = row[5]

			albums[row[3]].addTrack(track)

		return albums
