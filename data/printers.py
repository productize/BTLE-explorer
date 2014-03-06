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

  class BoolEditor(QtGui.QCheckBox):
    
    def __init__(self, value):
      super(Bool.BoolEditor, self).__init__("Enabled")
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
    return Bool.BoolEditor
