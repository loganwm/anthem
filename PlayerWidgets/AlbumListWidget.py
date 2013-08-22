from PyQt4 import QtGui, QtCore
import MusicStructures
import math

class AlbumListWidget(QtGui.QScrollArea):
	def __init__(self):
		super(AlbumListWidget, self).__init__()
		self.initUI()

	def initUI(self):
		#allow widgets to resize inside frame
		self.setWidgetResizable(True)
	
		albumlist = QtGui.QWidget()		
		
		layout = QtGui.QVBoxLayout()
		layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

		self.album_layout = layout

		self.verticalScrollBar().setSingleStep(8)

		albumlist.setLayout(layout)		

		self.setWidget(albumlist)

	def addAlbum(self, album):
		album_entry = AlbumListEntry()
		print "stub"
		
		album_entry.setAlbumTitle(album.title)
		
		tracks = album.getTracks()
		for track in tracks: album_entry.addTrack(track)

		self.album_layout.addWidget(album_entry)


	def clearAlbums(self):
		while self.album_layout.count() > 0:
			child = self.album_layout.itemAt(0).widget()
			self.album_layout.removeWidget(child)
			child.setParent(None)
			child.destroy()

	def onTrackClicked(self, callback):
		if hasattr(callback, '__call__'):
			self._callback_trackclicked_ = callback
		else:
			print "Please supply a valid callback"
		

class AlbumListEntry(QtGui.QWidget):
	def __init__(self):
		super(AlbumListEntry, self).__init__()
		self.initUI()

	def initUI(self):		
		frame = QtGui.QFrame();
		album_info_layout = QtGui.QVBoxLayout()
		
		album_title = QtGui.QLabel("Untitled Album")
		album_title.setContentsMargins(16,4,4,4)

		font = QtGui.QFont("Helvetica", 16);
		album_title.setFont(font)
		
		tracklist = AlbumlistTracklistWidget()
		self.tracklist_widget = tracklist
		
		album_info_layout.addWidget(album_title)
		album_info_layout.addWidget(tracklist)
		frame.setLayout(album_info_layout)

		self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
		
		layout = QtGui.QHBoxLayout()
		
		layout.addWidget(AlbumArtWidget(), 1)
		layout.addWidget(frame, 4)
		self.setLayout(layout)
		
		self.album_title = album_title
		
	def setAlbumTitle(self, title):
		self.album_title.setText(title)
		
	def addTrack(self, track):
		self.tracklist_widget.addTrack(track)
		


class AlbumArtWidget(QtGui.QLabel):
	def __init__(self):
		super(AlbumArtWidget, self).__init__()
		self.initUI()

	def initUI(self):
		image = QtGui.QPixmap("./graphics/blankalbum.png")
		label = QtGui.QLabel()
		scaled_image = image.scaled(128,128)
		self.setPixmap(scaled_image)
		self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

	
class AlbumlistTracklistWidget(QtGui.QTableWidget):
	def __init__(self):
		super(AlbumlistTracklistWidget, self).__init__()
		self.initUI()

	def initUI(self):
		self.setColumnCount(4)

		self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		self.itemActivated.connect(self.rowSelected)

		self.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem("#"))
		self.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("Track"))
		self.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("Artist"))
		self.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem("Length"))

		self.verticalHeader().hide()
		self.horizontalHeader().hide()
		
		self.resizeToFitRows()
		
		header = self.horizontalHeader();
		
		self.setMinimumWidth(800)

	def rowSelected(self, item):
		#I'm so sorry for this
		owner_widget = self.parent().parent().parent().parent().parent()

		if "_callback_trackclicked_" in dir(owner_widget):
			owner_widget._callback_trackclicked_(item.track)
	
	def resizeEvent(self, event):
		total_width = event.size().width()
		
		#track number width
		self.setColumnWidth(0, 40)
		
		#track length width
		self.setColumnWidth(3, 40)
		
		remaining_length = total_width - 80
		
		track_name_length = math.floor(0.75 * remaining_length)
		track_artist_length = remaining_length - track_name_length
		
		self.setColumnWidth(1, track_name_length)	
		self.setColumnWidth(2, track_artist_length)		

	
	def resizeToFitRows(self):
		height = (self.rowCount()*self.rowHeight(0)) + (2 * self.frameWidth())	
		self.setMinimumHeight(height)
		self.setMaximumHeight(height)
		
	def selectionChanged(self, selected, previously_selected):
		super(AlbumlistTracklistWidget, self).selectionChanged(selected, previously_selected)
		
		print "changed"

	def mouseMoveEvent(self, event):
		#drop selection if holding mouse button and moving mouse
		if self.state() == QtGui.QAbstractItemView.DragSelectingState:
			super(AlbumlistTracklistWidget, self).mouseMoveEvent(event)

	def focusOutEvent(self, event):
		super(AlbumlistTracklistWidget, self).focusOutEvent(event)
		self.clearSelection()
		print "lost focus"
	
	
	def addTrack(self, track):
		row_index = self.rowCount()
		self.setRowCount(row_index+1)

		track_number = QtGui.QTableWidgetItem(track.track_number)
		track_number.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
		track_number.track_id = track.id #THIS CAN BE RECTIFIED LATER
		self.setItem(row_index, 0, track_number)

		title = QtGui.QTableWidgetItem(track.title)
		title.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
		title.track_id = track.id #THIS CAN BE RECTIFIED LATER
		self.setItem(row_index, 1, title)

		artist = QtGui.QTableWidgetItem(track.artist)
		artist.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
		artist.track_id = track.id #THIS CAN BE RECTIFIED LATER
		self.setItem(row_index, 2, artist)

		length = QtGui.QTableWidgetItem(track.length)
		length.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
		length.track_id = track.id #THIS CAN BE RECTIFIED LATER
		self.setItem(row_index, 3, length)
		
		#adjust to new row
		self.resizeToFitRows()
		
