#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from productize import parse_data
import ble
from ble import BLE

class MainWin(QtGui.QMainWindow):

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
     w = QtGui.QLabel("%d %s" % (handle, mac))
     w.mac = mac
     return w

  def tab_changed(self, i):
    pass

  def row_changed(self, current, previous):
    self.selected_device = self.collect_model.item(current.row(), 1).data(Qt.DisplayRole)
    self.selected_device_raw = self.collect_model.item(current.row(), 1).data()

  def run_collection(self):
    self.activity_thread = ble.ActivityThread(self.ble)
    self.ble.scan_response.connect(self.scan_response)
    self.ble.connection_status.connect(self.connection_status)
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
      idx = self.qtab.addTab(self.make_device_widget(handle, mac), mac)
      self.qtab.setCurrentIndex(idx)
      self.ble.primary_service_discovery(handle)

  def connect(self):
    idx = self.tab_exists(self.selected_device)
    if idx is None:
      if not self.selected_device is None:
        self.ble.connect_direct(self.selected_device_raw)
    else:
      self.qtab.setCurrentIndex(idx)

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
