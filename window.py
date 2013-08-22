from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon

import PlayerWidgets
import MusicBackend
import CorePlugins
import thread
import time

player = MusicBackend.MusicPlayer()

db = MusicBackend.MusicDatabase("music.db")
db.start()
db.clearTracks()
db.importDirectory(".")
__MAIN_WINDOW__ = None


class PlayerWindow(QtGui.QMainWindow):
	def __init__(self):
		super(PlayerWindow, self).__init__()
		
		global __MAIN_WINDOW__
		__MAIN_WINDOW__ = self

		self.initUI()
		self.initializePlugins()

	def initUI(self):
		self.setGeometry(300,300,1200,600)
		self.setWindowTitle("Music Player")
		self.setWindowIcon(QtGui.QIcon("./graphics/media-play.png"))

		menu = PlayerMenu()
		self.setMenuBar(menu)

		rootFrame = QtGui.QFrame()
		layout = QtGui.QVBoxLayout()

		searchBar = PlayerSearchBar()
		contentArea = PlayerContentArea()
		controlBar = PlayerControlBar()

		layout.addWidget(searchBar)
		layout.addWidget(contentArea)
		layout.addWidget(controlBar)

		frame = QtGui.QFrame()
		rootFrame.setLayout(layout)

		self.setCentralWidget(rootFrame)
		
		self.show()
		
		self._contentarea_ = contentArea
		self._menu_ = contentArea.menu()

	def initializePlugins(self):
		self.core_plugins = {}
		self.core_plugins["search"] = CorePlugins.CoreSearchPlugin()
		self.core_plugins["search"].initialize(self, db, player)
	
	def closeEvent(self, event):
		player.close()

	def menu(self):
		return self._menu_

	def setMainContent(self, widget):
		self._contentarea_.setMainContent(widget)

	def searchTyped(self, query):
		for plugin_name in self.core_plugins:
			if "searchTyped" in dir(self.core_plugins[plugin_name]):
				self.core_plugins[plugin_name].searchTyped(query)


class PlayerControlBar(QtGui.QWidget):
	def __init__(self):
		super(PlayerControlBar, self).__init__()
		self.initUI()
		self.initialize()

	def initUI(self):
		self.setMinimumHeight(40);
		self.setMaximumHeight(40);

		playerControls = PlayerControls()
		playerControls.setMaximumWidth(160)
		
		playerOrderControls = PlayerOrderControls()
		playerOrderControls.setMaximumWidth(80)
		
		playerTrackControls = PlayerTrackControls()
		
		playerVolumeControls = PlayerVolumeControls()
		playerVolumeControls.setMaximumWidth(80)


		layout = QtGui.QHBoxLayout()
	
		layout.addWidget(playerControls, 1)
		layout.addWidget(playerVolumeControls, 1)
		layout.addWidget(playerTrackControls, 3)
		layout.addWidget(playerOrderControls, 1)

		self.setLayout(layout)
		
		
		self._playertrackcontrols_ = playerTrackControls

	def initialize(self):
		#thread.start_new_thread(self.updateCurrentTimeThread, ())
		print "y"
	
	

class PlayerControls(QtGui.QWidget):
	def __init__(self):
		super(PlayerControls, self).__init__()
		self.initUI()

	def initUI(self):

		previousButton = QtGui.QPushButton("<<");	
		playButton = QtGui.QPushButton(">");		
		nextButton = QtGui.QPushButton(">>");

		layout = QtGui.QHBoxLayout()

		#clear margins
		layout.setMargin(0)

		layout.addWidget(previousButton, 1)	
		layout.addWidget(playButton, 1)
		layout.addWidget(nextButton, 1)

		self.setLayout(layout)
		
		playButton.clicked.connect(self.play)
		nextButton.clicked.connect(self.next)
		previousButton.clicked.connect(self.prev)
		
		
		self.paused = False
		
	def play(self):
		if self.paused:
			player.resumeTrack()
		else:
			player.pauseTrack()
		
		self.paused = not self.paused

	def prev(self):
		player.playPreviousTrack()

	def next(self):
		player.playNextTrack()

class PlayerOrderControls(QtGui.QWidget):
	def __init__(self):
		super(PlayerOrderControls, self).__init__()
		self.initUI()

	def initUI(self):

		shuffleButton = QtGui.QPushButton("~");	
		repeatButton = QtGui.QPushButton("o");

		layout = QtGui.QHBoxLayout()

		#clear margins
		layout.setMargin(0)

		layout.addWidget(shuffleButton, 1)	
		layout.addWidget(repeatButton, 1)

		self.setLayout(layout)

class PlayerVolumeControls(QtGui.QWidget):
	def __init__(self):
		super(PlayerVolumeControls, self).__init__()
		self.initUI()

	def initUI(self):
		volumeBar = QtGui.QSlider(QtCore.Qt.Horizontal)
		self._volumebar_ = volumeBar

		volumeBar.valueChanged.connect(self.volumeChanged)
		volumeBar.setValue(volumeBar.maximum())
		layout = QtGui.QHBoxLayout()

		#clear margins
		layout.setMargin(0)

		layout.addWidget(volumeBar, 1)

		self.setLayout(layout)

	def volumeChanged(self, value):
		normalized_value = value / float(self._volumebar_.maximum())
		
		player.setVolume(normalized_value)

class PlayerTrackControls(QtGui.QWidget):
	def __init__(self):
		super(PlayerTrackControls, self).__init__()
		self.initUI()
		self.update_thread = UpdateTrackTimeThread()
		self.update_thread.start()
		self.initialize()
		
	def initUI(self):

		currentTimeLabel = QtGui.QLabel("0:00")
		progressBar = PlayerTrackProgressbar()
		totalTimeLabel = QtGui.QLabel("0:00")

		progressBar.setMaximum(1000)

		layout = QtGui.QHBoxLayout()

		#clear margins
		layout.setMargin(0)

		currentTimeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

		currentTimeLabel.setMaximumWidth(30)
		totalTimeLabel.setMaximumWidth(30)

		layout.addWidget(currentTimeLabel, 1)	
		layout.addWidget(progressBar, 1)
		layout.addWidget(totalTimeLabel, 1)

		self.setLayout(layout)
		
		self._currenttime_label_ = currentTimeLabel
		self._totaltime_label_ = totalTimeLabel
		self._progressbar_ = progressBar

	def initialize(self):
		self.connect(self.update_thread, QtCore.SIGNAL("trackTimeChanged(QString, QString, float)"), self.trackTimeChanged)

	def trackTimeChanged(self, current_timestring, total_timestring, position):
		self.setCurrentTimeString(current_timestring)
		self.setTotalTimeString(total_timestring)
		self.setNormalizedTrackPosition(position)
	
	def setNormalizedTrackPosition(self, position):
		self._progressbar_.setValue(position * self._progressbar_.maximum())
	
	def setTotalTimeString(self, totaltime):
		self._totaltime_label_.setText(totaltime)

	def setCurrentTimeString(self, currenttime):
		self._currenttime_label_.setText(currenttime)

class PlayerTrackProgressbar(QtGui.QSlider):
	def __init__(self):
		super(PlayerTrackProgressbar, self).__init__(QtCore.Qt.Horizontal)
		self.initUI()
		
	def initUI(self):
		print "live"
		
	def mousePressEvent(self, event):
		print "click"
		
		if event.button() == QtCore.Qt.LeftButton:
			self.setValue(self.minimum() + ((self.maximum()-self.minimum()) * event.x()) / float(self.width()))
			event.accept()
			
		super(PlayerTrackProgressbar, self).mousePressEvent(event)
		
		normalized_position = self.value() / float(self.maximum())
		player.seekTrack(normalized_position)

class PlayerSearchBar(QtGui.QWidget):
	def __init__(self):
		super(PlayerSearchBar, self).__init__()
		self.initUI()

	def initUI(self):	
		self.setMinimumHeight(40);
		self.setMaximumHeight(40);
	
		label = QtGui.QLabel("Music Player")
		label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
		
		searchBox = QtGui.QLineEdit()
		searchBox.textChanged.connect(self.searchTyped)
		
		layout = QtGui.QHBoxLayout()

		layout.addWidget(label, 1)	
		layout.addWidget(searchBox, 10)

		self.setLayout(layout)

	def searchTyped(self, query):
		__MAIN_WINDOW__.searchTyped(query)

class PlayerContentArea(QtGui.QWidget):
	def __init__(self):
		super(PlayerContentArea, self).__init__()
		self.initUI()
		UpdateTrackTimeThread()

	def initUI(self):
		contentSidebar = PlayerContentSidebar()
		contentMain = PlayerContentMain()
		
		layout = QtGui.QHBoxLayout()
		layout.setMargin(0)

		splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
	
		splitter.addWidget(contentSidebar)
		splitter.addWidget(contentMain)
		
		layout.addWidget(splitter, 0)

		self.setLayout(layout)
		
		self._menu_ = contentSidebar.menu()
		self._contentmain_ = contentMain
		
		
	def menu(self):
		return self._menu_
		
	def setMainContent(self, widget):
		self._contentmain_.setContent(widget)

class PlayerContentMain(QtGui.QFrame):
	def __init__(self):
		super(PlayerContentMain, self).__init__()
		self.initUI()

	def initUI(self):
		layout = QtGui.QVBoxLayout()
		
		content = None
		
		#layout.addWidget(content)

		self.setLayout(layout)
		
		self._content_ = content
		self._layout_ = layout

	def setContent(self, widget):
		if widget == None: return

		if self._content_ != None:
			self._layout_.removeWidget(self._content_)
			self._content_.setParent(None)

		self._content_ = widget
		self._layout_.addWidget(self._content_)



class PlayerContentSidebar(QtGui.QWidget):
	def __init__(self):
		super(PlayerContentSidebar, self).__init__()
		self.initUI()

	def initUI(self):
		self.setMaximumWidth(180);

		layout = QtGui.QVBoxLayout()
		
		list = PlayerWidgets.MenuWidget()
		
		layout.addWidget(list)
	
		self.setLayout(layout)
		
		#make the listbox externally accessible
		self._menu_ = list

	def menu(self):
		return self._menu_
		

class PlayerMenu(QtGui.QMenuBar):
	def __init__(self):
		super(PlayerMenu, self).__init__()
		self.initUI()
	
	def initUI(self):
		exit_action = QtGui.QAction("&Exit", self)
		exit_action.setShortcut("Ctrl+Q")
		exit_action.setStatusTip("exit app")
		exit_action.triggered.connect(QtGui.qApp.quit)
		
		file_menu = self.addMenu("&File")
		file_menu.addAction(exit_action)

class UpdateTrackTimeThread(QtCore.QThread):
	def run(self):
		while True:
			trunc_current_time = player.currentTrackTime() / 1000
			current_minutes = trunc_current_time / 60
			current_seconds = trunc_current_time % 60
			current_timestring = str(current_minutes) + ":" + str(current_seconds).zfill(2)

			trunc_total_time = player.totalTrackTime() / 1000
			total_minutes = trunc_total_time / 60
			total_seconds = trunc_total_time % 60
			total_timestring = str(total_minutes) + ":" + str(total_seconds).zfill(2)			
			

			if trunc_total_time != 0:
				normalized_track_position = float(player.currentTrackTime()) / float(player.totalTrackTime())
			else:
				normalized_track_position = 0

			self.emit(QtCore.SIGNAL("trackTimeChanged(QString, QString, float)"), current_timestring, total_timestring, normalized_track_position)

			time.sleep(0.25)
