#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from collect import CollectThread
from productize import parse_data

class MainWin(QtGui.QMainWindow):

  def __init__(self):
    super(MainWin, self).__init__()
    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    self.add_action(fileMenu, '&Quit', self.close, 'Ctrl+Q')
    helpMenu = menuBar.addMenu('&Help')
    self.add_action(helpMenu, '&About', self.about)
    self.qtab = QtGui.QTabWidget()
    self.qtab.addTab(self.make_collect_widget(), "collect")
    self.setCentralWidget(self.qtab)
    self.qtab.currentChanged.connect(self.tab_changed)
    self.qtab.setCurrentIndex(0)
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
    self.collect_model = QtGui.QStandardItemModel()
    self.collect_model.setColumnCount(4)
    self.collect_model.setHorizontalHeaderLabels(['time','from', 'name', 'data'])
    self.collect_model_root = self.collect_model.invisibleRootItem()
    self.collect_view.setModel(self.collect_model)
    return self.collect_view

  def tab_changed(self, i):
    print "tab changed", i

  def run_collection(self):
    self.collect_thread = CollectThread("/dev/ttyACM0", 115200)
    self.collect_thread.scan_response.connect(self.scan_response)
    self.collect_thread.start()

  def scan_response(self, args):
    t_field = time.strftime("%H:%M:%S %d/%m/%Y", time.localtime())
    t_field = QtGui.QStandardItem(t_field)
    f_field = ''.join(['%02X' % b for b in args["sender"][::-1]])
    f_field = QtGui.QStandardItem(f_field)
    (n_field, d_field) = parse_data(args['data'])
    d_field = QtGui.QStandardItem(d_field)
    n_field = QtGui.QStandardItem(n_field)
    self.collect_model.insertRow(0, [t_field, f_field, n_field, d_field])
    self.collect_view.resizeColumnToContents(0)
    self.collect_view.resizeColumnToContents(1)
    self.collect_view.resizeColumnToContents(2)
    self.collect_view.resizeColumnToContents(3)
    print args

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
