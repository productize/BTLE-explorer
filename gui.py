#!/usr/bin/env python
#
# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

class MainWin(QtGui.QMainWindow):

  def __init__(self):
    super(MainWin, self).__init__()

    menuBar = self.menuBar()
    fileMenu = menuBar.addMenu('&File')
    self.add_action(fileMenu, '&Quit', self.close, 'Ctrl+Q')
    helpMenu = menuBar.addMenu('&Help')
    self.add_action(helpMenu, '&About', self.about)

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
    QtGui.qApp.quit()

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
