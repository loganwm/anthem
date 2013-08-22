import subprocess
import thread
import time
import json
import Queue
import random
from collections import deque

class MusicPlayer:
	def __init__(self):
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		self.process = subprocess.Popen(["AudioServ/AudioServ.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False, startupinfo=startupinfo)
		self.running = True
		
		self.outbound_messages = Queue.Queue()
		
		self.incoming_thread = thread.start_new_thread(self.dispatchIncomingMessages, ())
		self.outgoing_thread = thread.start_new_thread(self.dispatchOutgoingMessages, ())
		self.sync_thread = thread.start_new_thread(self.syncThread, ())
		self.time_thread = thread.start_new_thread(self.timeThread, ())

		self.current_track = None
		self.current_track_time = 0
		self.current_track_totaltime = 0
		self.track_playing = False

		self.previously_played = deque()
		self.play_queue = deque()
		
		self.shuffle = True
		self.loop = True

	def dispatchIncomingMessages(self):
		while self.running:
			line = self.process.stdout.readline()
			#print line

			try:
				message = json.loads(line)
			except:
				continue
				
			if message["type"] == "TRACKPOSITION":
				self.current_track_time = message["position"]
			if message["type"] == "TRACKPLAYING":
				self.current_track_totaltime = message["totaltime"]
			if message["type"] == "TRACKFINISHED":
				self.current_track_time = self.current_track_totaltime #just make sure this matches
				self.track_playing = False
				self.playNextTrack()

			time.sleep(0.01)

	def dispatchOutgoingMessages(self):
		while self.running:
			if not self.outbound_messages.empty():
				message = self.outbound_messages.get()
				self.process.stdin.write(message)
			time.sleep(0.01)

	def syncThread(self):
		while self.running:
			self.sendMessage("{ \"type\":\"GETPOSITION\"}\n")
			time.sleep(1)

	def timeThread(self):
		while self.running:
			if self.track_playing:
				self.current_track_time = self.current_track_time + 1000
				print "a" + str(self.current_track_time)
				print self.track_playing
			
			time.sleep(1)

	def currentTrackTime(self):
		return self.current_track_time

	def totalTrackTime(self):
		return self.current_track_totaltime

	def close(self):
		self.running = False
		self.process.terminate()
	
	def sendMessage(self, message):
		self.outbound_messages.put(message)
		#print message

	def queueTracks(self, tracks):
		self.play_queue = deque()

		if not self.shuffle:
			for track in tracks:
				self.play_queue.append(track)
		else:
			first_track = tracks[0]
			shuffled_tracks = tracks[1:]
			random.shuffle(shuffled_tracks)
			shuffled_tracks.insert(0, first_track)

			for track in shuffled_tracks:
				self.play_queue.append(track)

		print "--Playlist--"
		for track in self.play_queue:
			print track.title

	def playTrack(self, track):
		self.sendMessage("{\"type\":\"PLAYTRACK\", \"path\":\"" + track.filepath + "\"}\n")
		self.current_track_time = 0
		self.current_track = track
		self.track_playing = True

	def playNextTrack(self):
		if len(self.play_queue) != 0:
			track = self.play_queue.popleft()
			
			if self.current_track != None:
				self.previously_played.appendleft(self.current_track)
			
			self.playTrack(track)
		else:
			print "No more tracks"

	def playPreviousTrack(self):
		print self.previously_played

		if len(self.previously_played) != 0:
			track = self.previously_played.popleft()
			self.play_queue.appendleft(self.current_track)
			self.playTrack(track)
		else:
			print "No more tracks"


	def pauseTrack(self):
		if self.current_track != None:
			self.sendMessage("{\"type\":\"PAUSETRACK\"}\n")
			self.track_playing = False

	def resumeTrack(self):
		if self.current_track != None:
			self.sendMessage("{\"type\":\"RESUMETRACK\"}\n")
			self.track_playing = True

	def seekTrack(self, normalized_position):
		position = normalized_position * self.current_track_totaltime
		self.sendMessage("{\"type\":\"SETPOSITION\", \"position\":" + str(position) + "}\n")

	def setVolume(self, volume):
		self.sendMessage("{\"type\":\"SETVOLUME\", \"volume\":" + str(volume) + "}\n")
		