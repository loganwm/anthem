from PyQt4 import QtGui, QtCore

class TrackListWidget(QtGui.QTableWidget):
	def __init__(self):
		super(TrackListWidget, self).__init__()
		self.initUI()

	def initUI(self):
		self.setColumnCount(4)

		self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		self.itemActivated.connect(self.rowSelected)

		self.setSortingEnabled(True)

		self.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("Track"))
		self.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem("Artist"))
		self.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("Length"))
		self.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem("Album"))

		self.verticalHeader().hide()
		
		header = self.horizontalHeader();
		
		self.verticalScrollBar().setSingleStep(0.5)
		
		#self.setColumnHidden(1,True)
		header.setResizeMode(QtGui.QHeaderView.Stretch)

	def rowSelected(self, item):
		if "_callback_trackclicked_" in dir(self):
			self._callback_trackclicked_(item.track_id)

	def mouseMoveEvent(self, event):
		#drop selection if holding mouse button and moving mouse
		if self.state() == QtGui.QAbstractItemView.DragSelectingState:
			super(TrackListWidget, self).mouseMoveEvent(event)

	def focusOutEvent(self, event):
		super(TrackListWidget, self).focusOutEvent(event)
		self.clearSelection()
	
	def clearTracks(self):
		self.setRowCount(0)
	
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
		
	def onTrackClicked(self, callback):
		if hasattr(callback, '__call__'):
			self._callback_trackclicked_ = callback
		else:
			print "Please supply a valid callback"
		