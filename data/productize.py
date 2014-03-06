service = dict()

attr = dict()

class Vendor:

  ids = [0xFFFF]

  def _parse_product(self, product_id, data):
    if product_id == 1:
      raw_lux = data[0] + 256*data[1]
      luxf = raw_lux*1.24/2048
      luxf = luxf / (10E-6*27.4E3)
      luxf = 10 **luxf
      return "lux:%d" % int(luxf)
    return "unknown_product"

  def to_string(self, data):
    product_id = data[0] + 256*data[1]
    return self._parse_product(product_id, data[2:])
    
    
