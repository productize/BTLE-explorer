# (c) 2014 Productize <joost@productize.be>

import printers

import uuid

def uuid_to_list(uuidx):
  u = uuid.UUID(uuidx)
  return [ord(x) for x in u.bytes]

class Attr:

  def __init__(self, uuidx, name, printer=printers.Default):
    if type(uuidx) == type("hello"):
      self.uuid = uuid_to_list(uuidx)
    else:
      self.uuid = uuidx
    self.name = name
    self.printer = printer()
    self.suuid = printers.print_uuid(self.uuid)

  def value_to_string(self, val):
    return self.printer.printv(val)

  def string_to_value(self, s):
    return self.printer.scanv(s)

  def editor(self):
    return self.printer.editor()
