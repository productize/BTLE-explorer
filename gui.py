#!/usr/bin/env python
#
# (c) 2014 Productize <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import ble
from ble import BLE

class WriteDialog(QtGui.QDialog):

  def __init__(self, parent, chandle, name, value, editor):
    super(WriteDialog, self).__init__(parent)
    self.chandle = chandle
    self.setWindowTitle("Write '%s'" % (name))
    self.resize(640,160) # TODO, there must be a better way to do this
    vbox = QtGui.QVBoxLayout()
    fl = QtGui.QFormLayout()
    self.editor = editor
    if editor is None:
      self.value_edit = QtGui.QLineEdit()
      self.value_edit.setText(str(value))
    else:
      self.value_edit = editor(value)
    fl.addRow("Value:", self.value_edit)
    vbox.addLayout(fl)
    buttons = QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
    self.button_box = QtGui.QDialogButtonBox(buttons, QtCore.Qt.Horizontal)
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    #self.button_box.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
    vbox.addWidget(self.button_box)
    self.setLayout(vbox)

  def get_result(self):
    if self.editor is None:
      return self.value_edit.text()
    else:
      return self.value_edit.value()

class Device:

  def __init__(self, ble, handle, mac):
    self.ble = ble
    self.handle = handle
    self.mac = mac
    self.view = QtGui.QTreeView()
    self.view.mac = mac
    self.view.setExpandsOnDoubleClick(True)
    self.view.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self.view)
      self.view.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Read', self.read)
    _add('&Write', self.write)
    self.view.setRootIsDecorated(False)
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(5)
    self.model.setHorizontalHeaderLabels(['type', 'service/type','name','handle', 'value'])
    self.root = self.model.invisibleRootItem()
    self.view.setModel(self.model)
    self.view.doubleClicked.connect(self.double_click)
    self.selection_model = QtGui.QItemSelectionModel(self.model, self.view)
    self.view.setSelectionModel(self.selection_model)
    self.selection_model.currentRowChanged.connect(self.row_changed)
    self.current = None
    self.chandle_to_value_item = {}
    self.chandle_to_uuid = {}
    self.chandle_to_timer = {}
    self.chandle_stored_background = {}

  def row_changed(self, current, previous):
    self.current = current

  def read(self):
    return self.read2(False)
  
  def double_click(self):
    return self.read2(True)

  def read2(self, double_click):
    parent = self.model.itemFromIndex(self.current.parent())
    if parent is None:
      if double_click: return
      t = self.root.child(self.current.row(), 0).data(Qt.DisplayRole)
    else:
      t = parent.child(self.current.row(), 0).data(Qt.DisplayRole)
    if t == 'attr':
      chandle = int(parent.child(self.current.row(), 3).data(Qt.DisplayRole))
      self.ble.read_handle(self.handle, chandle)
    elif t == 'primary':
      handles = self.root.child(self.current.row(), 3).data(Qt.DisplayRole)
      [h1, h2] = handles.split('-')
      h1 = int(h1)
      h2 = int(h2)
      self.ble.read_handles(self.handle, h1, h2)

  def write(self):
    parent = self.model.itemFromIndex(self.current.parent())
    if parent is None: return
    t = parent.child(self.current.row(), 0).data(Qt.DisplayRole)
    if t == 'attr':
      chandle = int(parent.child(self.current.row(), 3).data(Qt.DisplayRole))
      name = parent.child(self.current.row(), 2).data(Qt.DisplayRole)
      uuid = self.chandle_to_uuid[chandle]
      editor = self.ble.uuid.editor_by_uuid(uuid)
      print "write to ", chandle
      try:
        value = self.chandle_to_value_item[chandle].data(Qt.DisplayRole)
      except:
        value = ''
      dialog = WriteDialog(self.view, chandle, name, value, editor)
      if dialog.exec_() != QtGui.QDialog.Accepted: return
      valstr = dialog.get_result()
      value = self.ble.uuid.string_to_value_by_uuid(uuid, valstr)
      self.ble.write_handle(self.handle, chandle, value)

  def primary(self):
    self.type = 'primary'

  def service_result(self, uuid, start, end):
    def s(x):
      y = QtGui.QStandardItem(x)
      y.setEditable(False)
      return y
    try:
      service = self.ble.uuid.name_by_uuid(uuid)
    except:
      service = ''
    uuids = ''.join(["%02X" % c for c in uuid])
    #print uuids
    p = s(self.type)
    p.setData(uuid)
    self.model.appendRow([p, s(uuids), s(service), s("%s-%s" % (start, end)), s('')])
    self.view.resizeColumnToContents(0)
    self.view.resizeColumnToContents(1)
    self.view.resizeColumnToContents(2)
    self.view.resizeColumnToContents(3)
    self.view.resizeColumnToContents(4)

  def scan(self):
    self.scan_pos = 0
    i = 0
    uuid = self.model.item(i, 0).data()
    range_str = self.model.item(i, 3).data(Qt.DisplayRole)
    (starts, ends) = range_str.split('-')
    start = int(starts)
    end = int(ends)
    #print uuid, start, end
    self.ble.find_information(self.handle, start, end)

  def continue_scan(self):
    self.scan_pos += 1
    if self.scan_pos == self.model.rowCount():
      return False
    i = self.scan_pos
    uuid = self.model.item(i, 0).data()
    range_str = self.model.item(i, 3).data(Qt.DisplayRole)
    (starts, ends) = range_str.split('-')
    start = int(starts)
    end = int(ends)
    #print uuid, start, end
    self.ble.find_information(self.handle, start, end)
    return True

  def info_found(self, char, uuid):
    #print "info_found", char, uuid
    def s(x):
      y = QtGui.QStandardItem(x)
      y.setEditable(False)
      return y
    uuids = ''.join(["%02X" % c for c in uuid])
    try:
      name = self.ble.uuid.name_by_uuid(uuid)
    except:
      name = ''
    svalue = s('')
    self.chandle_stored_background[char] = svalue.background()
    self.chandle_to_value_item[char] = svalue
    self.chandle_to_uuid[char] = uuid
    self.chandle_to_timer[char] = QtCore.QTimer()
    self.chandle_to_timer[char].setSingleShot(True)
    self.chandle_to_timer[char].timeout.connect(lambda: self.value_is_older(char))
    self.model.item(self.scan_pos).appendRow([s("attr"), s(uuids), s(name), s(str(char)), svalue])
    #self.view.expandAll()

  def value_is_older(self, chandle):
    svalue = self.chandle_to_value_item[chandle]
    svalue.setBackground(self.chandle_stored_background[chandle])

  def attr_value(self, chandle, t, value):
    uuid = self.chandle_to_uuid[chandle]
    s = self.ble.uuid.value_to_string_by_uuid(uuid, value)
    # TODO temporarely change background to green, and start timer
    # to change it back
    svalue = self.chandle_to_value_item[chandle]
    svalue.setData(s, Qt.DisplayRole)
    svalue.setBackground(QtGui.QBrush(Qt.green))
    self.chandle_to_timer[chandle].start(500.0)

class MainWin(QtGui.QMainWindow):

  PROC_IDLE = 0
  PROC_PRIMARY = 1
  PROC_ATTR = 2

  def __init__(self):
    super(MainWin, self).__init__()
    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    self.add_action(fileMenu, '&Quit', self.close, 'Ctrl+Q')
    deviceMenu = menuBar.addMenu('&Device')
    self.add_action(deviceMenu, '&Connect', self.double_click)
    self.add_action(deviceMenu, '&Disconnect', self.disconnect)
    helpMenu = menuBar.addMenu('&Help')
    self.add_action(helpMenu, '&About', self.about)
    self.qtab = QtGui.QTabWidget()
    self.qtab.addTab(self.make_collect_widget(), "collect")
    self.setCentralWidget(self.qtab)
    self.qtab.currentChanged.connect(self.tab_changed)
    self.qtab.setCurrentIndex(0)
    self.ble = ble.BLE(115200)
    self.ble.start()
    self.setWindowTitle("BTLE-explorer using device "+self.ble.address)
    self.handle_to_mac = {}
    self.handle_to_device = {}
    self.mac_to_handle = {}
    self.running = self.PROC_IDLE
    self.status("Ready.")
    self.run_collection()

  def status(self, msg):
    self.statusBar().showMessage(msg)

  def add_action(self, menu, text, slot, shortcut=None, checkable=False, checked=False):
    action = QtGui.QAction(text, self)
    if checkable:
      action.setCheckable(True)
      if checked:
        action.setChecked(True)
    menu.addAction(action)
    if slot == None:
      action.setDisabled(True)
    else:
      action.triggered.connect(slot)
    if shortcut != None: action.setShortcut(shortcut)
    return action

  def about(self):
    a = """
<p align="center"><b>BTLE-explorer</b></p>
<p align="center">(c) 2014 <i><a href="http://www.productize.be/">productize</a></i> &lt;joost@productize.be&gt;</p>
"""
    QtGui.QMessageBox.about(self, "about BTLE tool", a)

  def close(self):
    self.activity_thread.stop()
    time.sleep(0.1)
    QtGui.qApp.quit()

  def make_collect_widget(self):
    self.collect_view = QtGui.QTreeView()
    self.collect_view.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    self.collect_view.setRootIsDecorated(False)
    def _add(text, slot = None):
      action = QtGui.QAction(text, self)
      self.collect_view.addAction(action)
      if slot != None: action.triggered.connect(slot)
      else: action.setDisabled(True)
    _add('&Connect', self.double_click)
    self.collect_view.doubleClicked.connect(self.double_click)
    self.collect_model = QtGui.QStandardItemModel()
    self.collect_model.setColumnCount(5)
    self.collect_model.setHorizontalHeaderLabels(['time','from', 'type', 'name', 'data', 'rssi'])
    self.collect_model_root = self.collect_model.invisibleRootItem()
    self.collect_view.setModel(self.collect_model)
    self.selection_model = QtGui.QItemSelectionModel(self.collect_model, self.collect_view)
    self.collect_view.setSelectionModel(self.selection_model)
    self.selection_model.currentRowChanged.connect(self.row_changed)
    self.selected_device = None
    return self.collect_view

  def make_device_widget(self, handle, mac):
     device = Device(self.ble, handle, mac)
     self.handle_to_device[handle] = device
     self.handle_to_device[handle] = device
     return device

  def tab_changed(self, i):
    pass

  def row_changed(self, current, previous):
    self.selected_device = self.collect_model.item(current.row(), 1).data(Qt.DisplayRole)
    self.selected_device_raw = self.collect_model.item(current.row(), 1).data()

  def run_collection(self):
    self.activity_thread = ble.ActivityThread(self.ble)
    self.ble.scan_response.connect(self.scan_response)
    self.ble.connection_status.connect(self.connection_status)
    self.ble.service_result.connect(self.service_result)
    self.ble.procedure_completed.connect(self.procedure_completed)
    self.ble.info_found.connect(self.info_found)
    self.ble.attr_value.connect(self.attr_value)
    self.activity_thread.start()
    self.status("Collecting...")

  def scan_response(self, args):
    def s(x):
      y = QtGui.QStandardItem(x)
      y.setEditable(False)
      return y
    time_ = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())
    ftime = s(time_)
    address_type = args['address_type']
    if address_type == 0:
      ats = 'P|'
    else:
      ats = 'R|'
    sender = ats + (':'.join(['%02X' % b for b in args["sender"][::-1]]))
    name, data = self.ble.data_to_string(args['data'])
    ident = "%s_%s_%s" % (sender, name, data)
    ftime.setData(ident)
    fsender = s(sender)
    fsender.setData((args["sender"], args['address_type']))
    rssi = str(args['rssi'])
    packet_type = ble.event_type(args['packet_type'])
    # ~ -70 at 1m distance
    # ~ -80 => 2m
    # at 2m50 no more signal
    replaced = False
    for x in range(0, self.collect_model.rowCount()):
      if self.collect_model.item(x, 0).data() == ident:
        self.collect_model.item(x, 0).setData(time_, Qt.DisplayRole)
        replaced = True
        break # only one identical to remove normally
    if not replaced:
      self.collect_model.insertRow(0, [ftime, fsender, s(packet_type), s(name), s(data), s(rssi)])
      self.collect_view.resizeColumnToContents(0)
      self.collect_view.resizeColumnToContents(1)
      self.collect_view.resizeColumnToContents(2)
      self.collect_view.resizeColumnToContents(3)
      self.collect_view.resizeColumnToContents(4)
      self.collect_view.resizeColumnToContents(5)

  def tab_exists(self, mac):
    found = None
    for i in range(1,self.qtab.count()):
      if self.qtab.widget(i).mac == mac:
         self.qtab.setCurrentIndex(i)
         found = i
         break
    print "found", found
    return found

  def connection_status(self, handle, mac, status):
    print "connection_status called", status
    if status == BLE.CONNECTED:
      device = self.make_device_widget(handle, mac)
      idx = self.qtab.addTab(device.view, mac)
      self.handle_to_mac[handle] = mac
      self.mac_to_handle[mac] = handle
      self.qtab.setCurrentIndex(idx)
      self.running = self.PROC_PRIMARY
      QtGui.QApplication.setOverrideCursor(Qt.WaitCursor)
      device.primary()
      self.status("service discovery running")
      self.ble.primary_service_discovery(handle)
    elif status == BLE.DISCONNECTED:
      try:
        mac = self.handle_to_mac[handle]
        idx = self.tab_exists(mac)
        if not idx is None:
          self.qtab.removeTab(idx)
      except KeyError: # old stale connection
        pass
      self.ble.resume_collection() # TODO

  def double_click(self):
    idx = self.tab_exists(self.selected_device)
    if idx is None:
      if not self.selected_device is None:
        self.status("connecting")
        self.ble.connect_direct(self.selected_device_raw)
    else:
      self.qtab.setCurrentIndex(idx)

  def disconnect(self):
    idx = self.tab_exists(self.selected_device)
    if not idx is None:
      if not self.selected_device is None:
        self.status("disconnecting")
        self.qtab.setCurrentIndex(idx)
        self.ble.disconnect(self.mac_to_handle[self.selected_device])

  def service_result(self, handle, uuid, start, end):
    device = self.handle_to_device[handle]
    device.service_result(uuid, start, end)

  def info_found(self, handle, char, uuid):
    try:
      device = self.handle_to_device[handle]
      device.info_found(char, uuid)
    except KeyError:
      print "ignoring message for unknown handle", handle

  def procedure_completed(self, handle):
    print "procedure completed", handle, self.running
    device = self.handle_to_device[handle]
    if self.running == self.PROC_PRIMARY:
      self.running = self.PROC_ATTR
      self.status("retrieving attributes")
      device.scan()
    elif self.running == self.PROC_ATTR:
      if not device.continue_scan():
        QtGui.QApplication.restoreOverrideCursor()
        self.running = self.PROC_IDLE
        self.status("Idle.")

  def attr_value(self, handle, chandle, t, value):
    try:
      device = self.handle_to_device[handle]
      device.attr_value(chandle, t, value)
    except KeyError:
      print "ignoring message for unknown handle", handle

def main():
  QtCore.QCoreApplication.setOrganizationName("productize")
  QtCore.QCoreApplication.setOrganizationDomain("productize.be")
  QtCore.QCoreApplication.setApplicationName("BTLE-explorer")
  app = QtGui.QApplication(["BTLE-explorer"])
  app.setWindowIcon(QtGui.QIcon('productize_icon.png'))
  widget = MainWin()
  widget.show()
  return app.exec_()

if __name__ == '__main__':
  sys.exit(main())
