
def parse_product(product_id, data):
  if product_id == 1:
    raw_lux = data[0] + 256*data[1]
    luxf = raw_lux*1.24/2048
    luxf = luxf / (10E-6*27.4E3)
    luxf = 10 **luxf
    return "lux:%d" % int(luxf)
  return "unknown_product"

def parse_vendor(data):
  vendor = data[0] + 256*data[1]
  if vendor == 0xffff:
    product_id = data[2] + 256*data[3]
    return parse_product(product_id, data[4:])
  else:
    return "vendor:%04X" % vendor

