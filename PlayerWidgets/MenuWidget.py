from PyQt4 import QtGui, QtCore
import copy

class MenuWidget(QtGui.QListWidget):
	itemMoved = QtCore.pyqtSignal(int, int, QtGui.QListWidgetItem)

	def __init__(self):
		super(MenuWidget, self).__init__()
		self.initUI()

	def initUI(self):
		self.setMouseTracking(True)
		self.setSelectionRectVisible(False)
		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.setDragDropMode(QtGui.QAbstractItemView.InternalMove);
		
		self.itemClicked.connect(self.menuItemSelected)
		self.itemActivated.connect(self.menuItemSelected)
		#self.itemSelectionChanged.connect(self.menuSelectionChanged)

		self.itemMoved.connect(self.moved)
		self._drag_item_ = None
		self._drag_row_ = None

	def itemDoubleClicked(self, item):
		id = item.row();
		self.editItem(self.item(id))
		print self.item(id).id
	
	def addMenuGroup(self, group):
		self.addItem(group.header())
		group._startindex_ = self.row(group.header())
		group._owner_ = self
	
	def addMenuHeader(self, title):
		header = MenuEntryHeader(title)
		self.addItem(header)
		
	def addMenuEntry(self, title, callback):
		entry = MenuEntry(title, callback)
		self.addItem(entry)
		
	def menuItemSelected(self, item):
		if isinstance(item, MenuEntry):
			item.call()

	def dropEvent(self, event):
		super(MenuWidget, self).dropEvent(event)

		print self.row(self._drag_item_)
		self.itemMoved.emit(self._drag_row_, self.row(self._drag_item_), self._drag_item_)
		self._drag_item_ = None

	def startDrag(self, supportedActions):
		self._drag_item_ = self.currentItem()
		self._drag_row_ = self.row(self._drag_item_)
		super(MenuWidget, self).startDrag(supportedActions)

	def moved(self, original_index, new_index, item):
		group_index = self.row(item._owner_.header())
		num_items = len(item._owner_)
		
		#prevent moving items outside of their group
		if new_index > (group_index + num_items):
			menu_item = self.takeItem(new_index)
			self.insertItem(original_index, menu_item)
		elif new_index < group_index:
			menu_item = self.takeItem(new_index)
			self.insertItem(original_index, menu_item)

class MenuGroup:
	_owner_ = None

	def __init__(self, title):
		self._header_ = MenuEntryHeader(title)
		self._items_ = []

	def addMenuEntry(self, item):
		self._items_.append(item)
		item._owner_ = self
		adjusted_index = self._owner_.row(self._header_) + len(self._items_)
		self._owner_.insertItem(adjusted_index, item)

	def header(self):
		return self._header_
	
	def removeMenuEntry(self, item):
		row_index = self._owner_.row(item)
		self._owner_.takeItem(row_index)
		self._items_.remove(item)
	
	def __len__(self):
		return len(self._items_)

class MenuEntryHeader(QtGui.QListWidgetItem):
	def __init__(self, title):
		super(MenuEntryHeader, self).__init__()
		
		font = QtGui.QFont("Helvetica", 10);
		font.setBold(True)
		self.setFont(font)
		
		self.setFlags(QtCore.Qt.NoItemFlags | QtCore.Qt.ItemIsEnabled)
		#
		self.setText(title)
	
class MenuEntry(QtGui.QListWidgetItem):
	_entry_ = None

	def __init__(self, title, callback):
		super(MenuEntry, self).__init__()
		
		self.setText(title)
		self._callback_ = callback
		
	def call(self):
		if self._callback_ == None:
			print "No callback specified for: " + self.text()
			return

		self._callback_()
	