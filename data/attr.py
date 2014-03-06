# (c) 2014 Productize <joost@productize.be>

from printers import print_default, print_uuid

class Attr:

  def __init__(self, uuid, name, printer=print_default):
    self.uuid = uuid
    self.name = name
    self.printer = printer
    self.suuid = print_uuid(self.uuid)

  def value_to_string(self, val):
    return self.printer(val)
