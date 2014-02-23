#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class CollectThread(QtCore.QThread):
  def __init__(self, parent = None):
    super(CollectThread, self).__init__(parent)

  def run(self):
    while True:
      print "cucu"
      time.sleep(10)


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
<p align="center">(c) 2014 Joost Yervante Damad &lt;joost@productize.be&gt;</p>
"""
    QtGui.QMessageBox.about(self, "about BTLE tool", a)

  def close(self):
    # TODO stop threads
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
    self.collect_thread = CollectThread()
    self.collect_thread.start()

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
