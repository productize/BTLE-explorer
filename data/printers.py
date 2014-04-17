# (c) 2014 Productize <joost@productize.be>

import ast

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

def print_uuid(val):
  return ''.join(["%02X" % x for x in reversed(val)])

class Default:
  def printv(self, val):
    return str(val)

  def scanv(self, s):
    return ast.literal_eval(s)

  def editor(self):
    return None

class Uuid:

  def printv(self, val):
    return print_uuid(val)

class String:

  def printv(self, val):
    return ''.join(["%c" % x for x in val])

class Int32:

  def printv(self, val):
    return str(val[0] + 256*val[1] + 256*256*val[2] + 256*256*256*val[3])

class Char(Default):

  def printv(self, val):
    prop = val[0]
    props = []
    if prop & 0x1 > 0: props += ['Broadcast']
    if prop & 0x2 > 0: props += ['Read']
    if prop & 0x4 > 0: props += ['WriteNR']
    if prop & 0x8 > 0: props += ['Write']
    if prop & 0x10 > 0: props += ['Notify']
    if prop & 0x20 > 0: props += ['Indicate']
    if prop & 0x40 > 0: props += ['SWrite']
    if prop & 0x80 > 0: props += ['EProp']
    prop = '|'.join(props)
    return "%s %d %s" % (prop, val[1] + 256*val[2], print_uuid(val[3:]))

class Bool(Default):

  class Editor(QtGui.QCheckBox):
    
    def __init__(self, value):
      super(Bool.Editor, self).__init__("Enabled")
      if str(value) == 'True':
        self.setCheckState(Qt.Checked)
      else:
        self.setCheckState(Qt.Unchecked)

    def value(self):
      return str(self.isChecked())

  def printv(self, val):
    return str(val[0]==1)

  def scanv(self, s):
    if s == "True":
      return [1]
    return [0]

  def editor(self):
    return Bool.Editor

class ClientCharConf(Default):

  n = "Notify"
  i = "Indicate"

  class Editor(QtGui.QWidget):

    def __init__(self, c, value):    
      super(ClientCharConf.Editor, self).__init__()
      self.n = c.n
      self.i = c.i
      vbox = QtGui.QVBoxLayout()
      prop = c.scanv(value)[0]
      notify = prop & 0x1 > 0
      indicate = prop & 0x2 > 0
      self.notify_edit = QtGui.QCheckBox(self.n)
      self.indicate_edit = QtGui.QCheckBox(self.i)
      self.notify_edit.setCheckState(Qt.Unchecked)
      self.indicate_edit.setCheckState(Qt.Unchecked)
      if notify:
        self.notify_edit.setCheckState(Qt.Checked)
      if indicate:
        self.indicate_edit.setCheckState(Qt.Checked)
      vbox.addWidget(self.notify_edit)
      vbox.addWidget(self.indicate_edit)
      self.setLayout(vbox)

    def value(self):
      props = []
      if self.notify_edit.isChecked(): props += [self.n]
      if self.indicate_edit.isChecked(): props += [self.i]
      return '|'.join(props)

  def printv(self, val):
    prop = val[0]
    props = []
    if prop & 0x1 > 0: props += [self.n]
    if prop & 0x2 > 0: props += [self.i]
    return '|'.join(props)

  def scanv(self, s):
    v = 0
    if self.n in s: v += 1
    if self.i in s: v += 2
    return [v, 0]

  def editor(self):
    return (lambda v: ClientCharConf.Editor(self, v))

class CSCFeature(Default):

  def printv(self, val):
    prop = val[0]
    props = []
    if prop & 0x1 > 0: props += ["Wheel"]
    if prop & 0x2 > 0: props += ["Crank"]
    if prop & 0x4 > 0: props += ["Multiple"]
    return '|'.join(props)

class CSCMeasurement(Default):
  def printv(self, val):
    print val
    prop = val[0]
    props = []
    if prop & 0x1 > 0: props += ["Wheel"]
    if prop & 0x2 > 0: props += ["Crank"]
    props = '|'.join(props)
    revo = val[1] + 256*val[2] + 65536*val[3] + 16777216*val[4]
    last = (val[5] + 256*val[6])/1024.0
    return "%s rev:%d last:%02f" % (props, revo, last)
