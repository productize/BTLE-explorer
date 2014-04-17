# (c) 2014 Productize <joost@productize.be>

from attr import Attr
import printers

attrs = [
  Attr("ac842717-f24c-46f7-bf49-5393f0124f8d", "Count Service"),
  Attr("5b97ab09-9065-478c-9ce8-9c9dcb2c5922", "Count", printers.Int32),
]

class Vendor:

  ids = [0xFFFF]

  def _parse_product(self, product_id, data):
    #print data
    if product_id == 1:
      raw_lux = data[0] + 256*data[1]
      luxf = raw_lux*1.24/2048
      luxf = luxf / (10E-6*27.4E3)
      luxf = 10 **luxf
      return "lux:%d" % int(luxf)
    elif product_id == 2:
      raw_temp = data[0] + 256*data[1]
      raw_hum = data[2]
      return "hum:%d temp:%d" % (int(raw_hum), int(raw_temp))
    return "unknown"

  def to_string(self, data):
    product_id = data[0] + 256*data[1]
    return self._parse_product(product_id, data[2:])
    
    
