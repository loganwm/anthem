import PlayerWidgets
import collections

class CorePlayQueuePlugin:
	_current_tracklist_ = collections.OrderedDict()

	def __init__(self):
		print "hello"
	
	def initialize(self, window, db, player):
		menu = window.menu()

		menu.addMenuEntry("Play Queue", self.switchToPlayQueue)

		self._window_ = window
		self._db_ = db
		self._tracklist_widget_ = PlayerWidgets.TrackListWidget()
		self._player_ = player

		self._tracklist_widget_.onTrackClicked(self.trackSelected)

		self._player_.onPlayQueueChanged(self.updatePlayQueue)

	def updatePlayQueue(self):
		tracks = self._player_.getPlayQueue()
		self._tracklist_widget_.clearTracks()
		self._current_tracklist_.clear()

		for track in tracks:
			self._tracklist_widget_.addTrack(track)
			self._current_tracklist_[track.id] = track
		

	def switchToPlayQueue(self):
		self._window_.setMainContent(self._tracklist_widget_)


	def trackSelected(self, track_id):
		tracks = []
		
		#construct the tracklist starting at the track we want. Add everything else after
		found = False
		for key in self._current_tracklist_.keys():
			if key == track_id: found = True

			if found:
				tracks.append(self._current_tracklist_[key])
		
		#add everything that was before the key
		found = False

		for key in self._current_tracklist_.keys():
			if key == track_id: found = True
		
			if not found:
				tracks.append(self._current_tracklist_[key])

		self._player_.queueTracks(tracks)
		self._player_.playNextTrack()
		
		