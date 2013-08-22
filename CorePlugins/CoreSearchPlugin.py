import PlayerWidgets
import collections

class CoreSearchPlugin:
	_current_tracklist_ = collections.OrderedDict()
	_last_search_ = ""
	def __init__(self):
		print "hello"
	
	def initialize(self, window, db, player):
		menu = window.menu()

		group = PlayerWidgets.MenuGroup("Search")


		menu.addMenuGroup(group)

		group.addMenuEntry(PlayerWidgets.MenuEntry("by title", self.switchToSearchByTitle))
		x = PlayerWidgets.MenuEntry("by artist", self.switchToSearchByArtist)
		group.addMenuEntry(x)
		group.addMenuEntry(PlayerWidgets.MenuEntry("by album", self.switchToSearchByAlbum))

		#group.removeMenuEntry(x)

		self._active_ = False
		self._searchmode_ = ""

		self._window_ = window
		self._db_ = db
		self._tracklist_widget_ = PlayerWidgets.TrackListWidget()
		self._albumlist_widget_ = PlayerWidgets.AlbumListWidget()
		self._player_ = player

		self._tracklist_widget_.onTrackClicked(self.trackSelected)
		self._albumlist_widget_.onTrackClicked(self.trackSelected)

	def searchTyped(self, query):	
		#coerce to string as needed
		query = str(query)
		self._last_search_ = str(query)
		
		if self._searchmode_ == "BYTITLE":
			tracks = self._db_.searchByTitle(query)
			self._tracklist_widget_.clearTracks()
			self._current_tracklist_.clear()

			for track in tracks:
				self._tracklist_widget_.addTrack(track)
				self._current_tracklist_[track.id] = track
				
		elif self._searchmode_ == "BYALBUM":
			albums = self._db_.searchByAlbum(query)
			self._albumlist_widget_.clearAlbums()
			self._current_tracklist_.clear()

			for album_name in albums:
				self._albumlist_widget_.addAlbum(albums[album_name])

				for track in albums[album_name].getTracks():
					self._current_tracklist_[track.id] = track

			for key in self._current_tracklist_.keys():
				print str(key) + ": " + str(self._current_tracklist_[key].title)

	def switchToSearchByTitle(self):
		self._window_.setMainContent(self._tracklist_widget_)

		self._searchmode_ = "BYTITLE"

		self._tracklist_widget_.clearTracks()

		self.searchTyped(self._last_search_)

	def switchToSearchByArtist(self):
		self._window_.setMainContent(self._tracklist_widget_)

		self._searchmode_ = "BYARTIST"

		self._tracklist_widget_.clearTracks()

		self.searchTyped(self._last_search_)

	def switchToSearchByAlbum(self):
		self._window_.setMainContent(self._albumlist_widget_)

		self._searchmode_ = "BYALBUM"
		
		self._albumlist_widget_.clearAlbums()
		
		self.searchTyped(self._last_search_)

		
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
		
		