#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from collect import CollectThread
from productize import parse_data
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
    self.ble = BLE("/dev/ttyACM0", 115200)
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
    self.collect_thread.stop()
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

  def tab_changed(self, i):
    print "tab changed", i

  def row_changed(self, current, previous):
    self.selected_device = self.collect_model.item(current.row(), 1).data(Qt.DisplayRole)

  def run_collection(self):
    self.collect_thread = CollectThread(self.ble)
    self.ble.scan_response.connect(self.scan_response)
    self.collect_thread.start()

  def scan_response(self, args):
    s = QtGui.QStandardItem
    time_ = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())
    ftime = s(time_)
    sender = ''.join(['%02X' % b for b in args["sender"][::-1]])
    name, data = parse_data(args['data'])
    ident = "%s_%s_%s" % (sender, name, data)
    ftime.setData(ident)
    # TODO: only keep latest x? from one mac
    # or possibly just replace identical doubles
    self.collect_model.insertRow(0, [ftime, s(sender), s(name), s(data)])
    self.collect_view.resizeColumnToContents(0)
    self.collect_view.resizeColumnToContents(1)
    self.collect_view.resizeColumnToContents(2)
    self.collect_view.resizeColumnToContents(3)
    for x in range(1, self.collect_model.rowCount()):
      if self.collect_model.item(x, 0).data() == ident:
        self.collect_model.takeRow(x)
        break # only one identical to remove normally

  def connect(self):
    print self.selected_device

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
