#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from productize import parse_data
import ble
from ble import BLE

class Device:

  def __init__(self, ble, handle, mac):
    self.ble = ble
    self.handle = handle
    self.mac = mac
    self.view = QtGui.QTreeView()
    self.view.setRootIsDecorated(False)
    self.model = QtGui.QStandardItemModel()
    self.model.setColumnCount(5)
    self.model.setHorizontalHeaderLabels(['type', 'service/type','name','handle', 'end/value'])
    self.root = self.model.invisibleRootItem()
    self.view.setModel(self.model)

  def primary(self):
    self.type = 'primary'

  def service_result(self, uuid, start, end):
    def s(x):
      y = QtGui.QStandardItem(x)
      y.setEditable(False)
      return y
    service = ''
    for (i, n) in ble.UUID.values():
      if i == uuid:
        service = n
        break
    uuids = ''.join(["%02X" % c for c in uuid])
    print uuids
    p = s(self.type)
    p.setData(uuid)
    self.model.appendRow([p, s(uuids), s(service), s(str(start)), s(str(end))])
    self.view.resizeColumnToContents(0)
    self.view.resizeColumnToContents(1)
    self.view.resizeColumnToContents(2)
    self.view.resizeColumnToContents(3)
    self.view.resizeColumnToContents(4)

  def scan(self):
    self.scan_pos = 0
    i = 0
    uuid = self.model.item(i, 0).data()
    start = int(self.model.item(i, 3).data(Qt.DisplayRole))
    end = int(self.model.item(i, 4).data(Qt.DisplayRole))
    print uuid, start, end
    self.ble.find_information(self.handle, start, end)

  def continue_scan(self):
    self.scan_pos += 1
    if self.scan_pos == self.model.rowCount():
      return False
    i = self.scan_pos
    uuid = self.model.item(i, 0).data()
    start = int(self.model.item(i, 3).data(Qt.DisplayRole))
    end = int(self.model.item(i, 4).data(Qt.DisplayRole))
    print uuid, start, end
    self.ble.find_information(self.handle, start, end)
    return True

  def info_found(self, char, uuid):
    #print "info_found", char, uuid
    def s(x):
      y = QtGui.QStandardItem(x)
      y.setEditable(False)
      return y
    uuids = ''.join(["%02X" % c for c in uuid])
    name = ''
    for (i, n) in ble.UUID.values():
      if i == uuid:
        name = n
        break
    self.model.item(self.scan_pos).appendRow([s("char"), s(uuids), s(name), s(str(char)), s('')])
    #self.view.expandAll()

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
    self.add_action(deviceMenu, '&Connect', self.connect)
    helpMenu = menuBar.addMenu('&Help')
    self.add_action(helpMenu, '&About', self.about)
    self.qtab = QtGui.QTabWidget()
    self.qtab.addTab(self.make_collect_widget(), "collect")
    self.setCentralWidget(self.qtab)
    self.qtab.currentChanged.connect(self.tab_changed)
    self.qtab.setCurrentIndex(0)
    self.ble = ble.BLE(115200)
    self.ble.start()
    self.setWindowTitle("BTLE tool using device "+self.ble.address)
    self.handle_to_mac = {}
    self.handle_to_device = {}
    self.running = self.PROC_IDLE
    self.run_collection()

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
<p align="center"><b>BTLE tool</b></p>
<p align="center">(c) 2014 <i>productize</i> &lt;joost@productize.be&gt;</p>
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
    _add('&Connect', self.connect)
    self.collect_view.doubleClicked.connect(self.connect)
    self.collect_model = QtGui.QStandardItemModel()
    self.collect_model.setColumnCount(4)
    self.collect_model.setHorizontalHeaderLabels(['time','from', 'name', 'data'])
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
    self.activity_thread.start()

  def scan_response(self, args):
    def s(x):
      y = QtGui.QStandardItem(x)
      y.setEditable(False)
      return y
    time_ = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())
    ftime = s(time_)
    sender = ':'.join(['%02X' % b for b in args["sender"][::-1]])
    name, data = parse_data(args['data'])
    ident = "%s_%s_%s" % (sender, name, data)
    ftime.setData(ident)
    fsender = s(sender)
    fsender.setData(args["sender"])
    replaced = False
    for x in range(0, self.collect_model.rowCount()):
      if self.collect_model.item(x, 0).data() == ident:
        self.collect_model.item(x, 0).setData(time_, Qt.DisplayRole)
        replaced = True
        break # only one identical to remove normally
    if not replaced:
      self.collect_model.insertRow(0, [ftime, fsender, s(name), s(data)])
      self.collect_view.resizeColumnToContents(0)
      self.collect_view.resizeColumnToContents(1)
      self.collect_view.resizeColumnToContents(2)
      self.collect_view.resizeColumnToContents(3)

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
      self.qtab.setCurrentIndex(idx)
      self.running = self.PROC_PRIMARY
      device.primary()
      self.ble.primary_service_discovery(handle)

  def connect(self):
    idx = self.tab_exists(self.selected_device)
    if idx is None:
      if not self.selected_device is None:
        self.ble.connect_direct(self.selected_device_raw)
    else:
      self.qtab.setCurrentIndex(idx)

  def service_result(self, handle, uuid, start, end):
    device = self.handle_to_device[handle]
    device.service_result(uuid, start, end)

  def info_found(self, handle, char, uuid):
    device = self.handle_to_device[handle]
    device.info_found(char, uuid)

  def procedure_completed(self, handle):
    print "procedure completed", handle, self.running
    device = self.handle_to_device[handle]
    if self.running == self.PROC_PRIMARY:
      self.running = self.PROC_ATTR
      device.scan()
    elif self.running == self.PROC_ATTR:
      if not device.continue_scan():
        self.running = self.PROC_IDLE


def main():
  QtCore.QCoreApplication.setOrganizationName("productize")
  QtCore.QCoreApplication.setOrganizationDomain("productize.be")
  QtCore.QCoreApplication.setApplicationName("BTLE tool")
  app = QtGui.QApplication(["BTLE tool"])
  widget = MainWin()
  widget.show()
  return app.exec_()

if __name__ == '__main__':
  sys.exit(main())
