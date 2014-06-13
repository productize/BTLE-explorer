# (c) 2014 Productize <joost@productize.be>

import bluetooth, productize, texas_instruments, apple
from printers import print_uuid

class UUID:

  def __init__(self):
    self.attr = {}
    self.attr_by_name = {}
    self.vendor = []
    sources = [bluetooth, productize, texas_instruments, apple]
    for source in sources:
     for attr in source.attrs:
       self.attr[attr.suuid] = attr
       self.attr_by_name[attr.name] = attr
     self.vendor.append(source.Vendor())

  def vendor_to_string(self, data):
    vendor_id = data[0] + 256*data[1]
    for v in self.vendor:
      if vendor_id in v.ids:
        return v.to_string(data[2:])
    return "vendor:%04X" % vendor_id

  def value_to_string_by_uuid(self, uuid, value):
    return self.attr[print_uuid(uuid)].value_to_string(value)

  def string_to_value_by_uuid(self, uuid, s):
    return self.attr[print_uuid(uuid)].string_to_value(s)

  def name_by_uuid(self, uuid):
    return self.attr[print_uuid(uuid)].name

  def editor_by_uuid(self, uuid):
    return self.attr[print_uuid(uuid)].editor()
