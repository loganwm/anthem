
class Album:
	def __init__(self, title="Untitled Album"):
		self._tracks_ = []
		self.title = title

	def addTrack(self, track):
		self._tracks_.append(track)
		
		#if track isn't specified, just put it well above the max ID3 track value of 65535
		self._tracks_.sort(key=lambda x: 999999 if x.track_number=="" else int(x.track_number))
	
	def getTracks(self):
		return self._tracks_
	
	def printAll(self):
		for track in self._tracks_:
			print track.title + " by " + track.artist + " (" + track.track_number + ")"