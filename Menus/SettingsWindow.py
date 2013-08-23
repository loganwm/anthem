from PyQt4 import QtGui, QtCore
import json


class SettingsWindow(QtGui.QDialog):
	_settings_context_ = {}

	def __init__(self):
		super(SettingsWindow, self).__init__()
		self.initUI()
		self.initialize()

	def initUI(self):
		self.setGeometry(20,20,600,600)
		
		layout = QtGui.QVBoxLayout()
		self._tabwidget_ = QtGui.QTabWidget()
		layout.addWidget(self._tabwidget_, 1)

		controls = QtGui.QWidget()
		controls.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)

		controls_layout = QtGui.QHBoxLayout()

		self._cancel_button_ = QtGui.QPushButton("Cancel")
		self._cancel_button_.setMaximumWidth(80)
		
		self._save_button_ = QtGui.QPushButton("Save")
		self._save_button_.setMaximumWidth(80)

		controls_layout.addWidget(self._cancel_button_)
		controls_layout.addWidget(self._save_button_)

		controls.setLayout(controls_layout)

		layout.addWidget(controls)
		
		layout.setMargin(0)		
		self.setLayout(layout)
		
		self._save_button_.clicked.connect(self.save)
		
	def initialize(self):
		self._importsettingspage_ = ImportSettingsPage()
		self._tabwidget_.addTab(self._importsettingspage_, "Import")
	
	def save(self):
		self._importsettingspage_.save(self._settings_context_)
		
		converted_config = json.dumps(self._settings_context_)

		config_file = open("./config.json", "w")
		config_file.write(converted_config)
		config_file.close()
		
	def load(self):
		self._settings_context_ = {}

		config_file = open("./config.json", "r")
		json_config = config_file.read()
		config_file.close()

		try:
			self._settings_context_ = json.loads(json_config)
		except:
			self._settings_context_ = {}

		self._importsettingspage_.load(self._settings_context_)
		
	def getSettingsContext():
		return self._settings_context_

	def closeEvent(self, event):
		event.ignore()
		self.hide()

class ImportSettingsPage(QtGui.QWidget):
	def __init__(self):
		super(ImportSettingsPage, self).__init__()
		self.initUI()
		
	def initUI(self):
		layout = QtGui.QVBoxLayout()

		"""
		This is the Directory management section
		"""
		directory_controls = QtGui.QWidget()
		directory_controls_layout = QtGui.QHBoxLayout()
		self._adddir_button_ = QtGui.QPushButton("Add Directory")
		self._remdir_button_ = QtGui.QPushButton("Remove Directory")
		self._remdir_button_.setEnabled(False)
		directory_controls_layout.addWidget(self._adddir_button_, 1)
		directory_controls_layout.addWidget(self._remdir_button_, 1)
		directory_controls.setLayout(directory_controls_layout)

		groupbox = QtGui.QGroupBox("Scan Directories")
		groupbox_layout = QtGui.QVBoxLayout()
		self._dirlist_ = QtGui.QListWidget()
		groupbox_layout.addWidget(self._dirlist_, 7)
		groupbox_layout.addWidget(directory_controls, 1)

		self._recursivescan_checkbox_ = QtGui.QCheckBox("Scan directories recursively.")
		groupbox_layout.addWidget(self._recursivescan_checkbox_, 1)

		groupbox.setLayout(groupbox_layout)
		
		layout.addWidget(groupbox, 6)


		"""
		This is the Other Options section
		"""
		alt_groupbox = QtGui.QGroupBox("Other Options")
		alt_groupbox_layout = QtGui.QVBoxLayout()
		self._fetchmetadata_checkbox_ = QtGui.QCheckBox("Fetch missing metadata for imported tracks.")
		alt_groupbox_layout.addWidget(self._fetchmetadata_checkbox_, 1)
		alt_groupbox.setLayout(alt_groupbox_layout)

		layout.addWidget(alt_groupbox, 1)		

		self.setLayout(layout)

		"""
		Events
		"""
		self._adddir_button_.clicked.connect(self.addScanDirectory)
		self._remdir_button_.clicked.connect(self.removeScanDirectory)
		self._dirlist_.itemSelectionChanged.connect(self.directorySelectionChanged)
	
	def save(self, settings_context):
		settings_context["import"] = {}
		settings_context["import"]["recursive"] = self._recursivescan_checkbox_.isChecked()
		settings_context["import"]["metadata"] = self._fetchmetadata_checkbox_.isChecked()
		settings_context["import"]["directories"] = []
		
		for index in xrange(self._dirlist_.count()):
			settings_context["import"]["directories"].append(str(self._dirlist_.item(index).text()))

	def load(self, settings_context):
		if not "import" in settings_context:
			return #should set defaults here in future
	
		if "recursive" in settings_context["import"]:
			self._recursivescan_checkbox_.setChecked(settings_context["import"]["recursive"])

		if "metadata" in settings_context["import"]:
			self._fetchmetadata_checkbox_.setChecked(settings_context["import"]["metadata"])
		
		if "directories" in settings_context["import"]:
			for directory in settings_context["import"]["directories"]:
				self._dirlist_.addItem(directory)
	
	def addScanDirectory(self):
		self._dialog_ = QtGui.QFileDialog(self)
		self._dialog_.setFileMode(QtGui.QFileDialog.Directory)
		
		self._dialog_.fileSelected.connect(self.scanDirectorySelected)
		
		self._dialog_.open()

	def removeScanDirectory(self):
		if len(self._dirlist_.selectedItems()) > 0:
			for selection in self._dirlist_.selectedItems():
				self._dirlist_.takeItem(self._dirlist_.row(selection))

	def scanDirectorySelected(self, dir):
		self._dirlist_.addItem(dir)
		print self._dirlist_.item(0).text()
		
	def directorySelectionChanged(self):
		if self._dirlist_.currentItem() == None:
			self._remdir_button_.setEnabled(False)
		else:
			self._remdir_button_.setEnabled(True)
		