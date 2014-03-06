# (c) 2014 Productize <joost@productize.be>

import printers

class Attr:

  def __init__(self, uuid, name, printer=printers.Default):
    self.uuid = uuid
    self.name = name
    self.printer = printer()
    self.suuid = printers.print_uuid(self.uuid)

  def value_to_string(self, val):
    return self.printer.printv(val)

  def string_to_value(self, s):
    return self.printer.scanv(s)

  def editor(self):
    return self.printer.editor()
