# (c) 2014 Productize <joost@productize.be>

import services, productize, texas_instruments
from printers import print_default, print_uuid

class UUID:

  def __init__(self):
    self.service = {}
    self.attr = {}
    self.vendor = []
    sources = [services, productize, texas_instruments]
    for source in sources:
     self.service.update(source.service)
     self.attr.update(source.attr)
     self.vendor.append(source.Vendor())
    self.attr_by_uuid = {}
    for v in self.attr.values():
      if len(v) == 2:
        self.attr_by_uuid[print_uuid(v[0])] = (v[1], print_default)
      else:
        self.attr_by_uuid[print_uuid(v[0])] = (v[1], v[2])

  def vendor_to_string(self, data):
    vendor_id = data[0] + 256*data[1]
    for v in self.vendor:
      if vendor_id in v.ids:
        return v.to_string(data[2:])
    return "vendor:%04X" % vendor_id

  def value_to_string_by_uuid(self, uuid, value):
    return self.attr_by_uuid[print_uuid(uuid)][1](value)

  def name_by_uuid(self, uuid):
    return self.attr_by_uuid[print_uuid(uuid)][0]
