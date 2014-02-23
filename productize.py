GAP_AD_TYPE_FLAGS = 0x01
GAP_AD_TYPE_LOCALNAME_COMPLETE = 0x09
GAP_AD_TYPE_TX_POWER = 0x0A
GAP_AD_TYPE_VENDOR = 0xFF

def parse_product(product_id, data):
  if product_id == 1:
    raw_lux = data[0] + 256*data[1]
    luxf = raw_lux*1.24/2048
    luxf = luxf / (10E-6*27.4E3)
    luxf = 10 **luxf
    return "lux:%d" % int(luxf)
  return "unknown"

def parse_vendor(data):
  vendor = data[0] + 256*data[1]
  if vendor == 0xffff:
    product_id = data[2] + 256*data[3]
    print "product_id", product_id
    return parse_product(product_id, data[4:])
  else:
    return "vendor:%04X" % vendor

def parse_data(data):
  pos = 0
  dl = []
  while pos < len(data):
    field_len = data[pos]
    field_type = data[pos+1]
    field_data = data[pos+2:(pos+2+field_len-1)]
    if field_type == GAP_AD_TYPE_FLAGS:
      dl.append("flags:%02X" % field_data[0])
    elif field_type == GAP_AD_TYPE_LOCALNAME_COMPLETE:
      dl.append("name:%s" % (''.join(['%c' % b for b in field_data])))
    elif field_type == GAP_AD_TYPE_TX_POWER:
      dl.append("tx:%ddB" % (field_data[0]))
    elif field_type == GAP_AD_TYPE_VENDOR:
      dl.append(parse_vendor(field_data))
    else:
      dl.append("unknown:%d" % field_type)
    pos += field_len + 1
  return ' '.join(dl)
