import services, productize, texas_instruments

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

  def vendor_to_string(self, data):
    vendor_id = data[0] + 256*data[1]
    for v in self.vendor:
      if vendor_id in v.ids:
        return v.to_string(data[2:])
    return "vendor:%04X" % vendor_id
