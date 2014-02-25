# https://www.bluetooth.org/en-us/specification/assigned-numbers/generic-access-profile

GAP_AD_TYPE_FLAGS = 0x01
GAP_AD_TYPE_LOCALNAME_COMPLETE = 0x09
GAP_AD_TYPE_TX_POWER = 0x0A
GAP_AD_TYPE_SLAVE_CON_INTERVAL_RANGE = 0x12
GAP_AD_TYPE_VENDOR = 0xFF

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

def parse_flags(val):
  flags = []
  if val & (2**0) > 0:
    flags.append('LE_lim')
  if val & (2**1) > 0:
    flags.append('LE_gen')
  if val & (2**2) > 0:
    flags.append('no_BR/EDR')
  if val & (2**3) > 0:
    flags.append('sim1')
  if val & (2**4) > 0:
    flags.append('sim2')
  return '|'.join(flags)

def parse_data(data):
  pos = 0
  dl = []
  name = ''
  while pos < len(data):
    field_len = data[pos]
    field_type = data[pos+1]
    field_data = data[pos+2:(pos+2+field_len-1)]
    if field_type == GAP_AD_TYPE_FLAGS:
      dl.append("flags:%s" % parse_flags(field_data[0]))
    elif field_type == GAP_AD_TYPE_LOCALNAME_COMPLETE:
      name = ''.join(['%c' % b for b in field_data])
      # dl.append("name:%s" % name)
    elif field_type == GAP_AD_TYPE_TX_POWER:
      dl.append("tx:%ddB" % (field_data[0]))
    elif field_type == GAP_AD_TYPE_SLAVE_CON_INTERVAL_RANGE:
      x1 = (field_data[0] + 256*field_data[1])*1.25
      x2 = (field_data[2] + 256*field_data[3])*1.25
      dl.append('slv_con_int_ran:%d-%dms' % (x1, x2))
    elif field_type == GAP_AD_TYPE_VENDOR:
      dl.append(parse_vendor(field_data))
    else:
      dl.append("unknown_field:0x%x" % field_type)
    pos += field_len + 1
  return (name, ' '.join(dl))
