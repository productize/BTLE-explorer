def print_uuid(val):
  return ''.join(["%02X" % x for x in reversed(val)])

def print_string(val):
  return ''.join(["%c" % x for x in val])  

def print_default(val):
  return str(val)

def print_char(val):
  prop = val[0]
  props = []
  if prop & 0x1 > 0: props += ['Broadcast']
  if prop & 0x2 > 0: props += ['Read']
  if prop & 0x4 > 0: props += ['WriteNR']
  if prop & 0x8 > 0: props += ['Write']
  if prop & 0x10 > 0: props += ['Notify']
  if prop & 0x20 > 0: props += ['Indicate']
  if prop & 0x40 > 0: props += ['SWrite']
  if prop & 0x80 > 0: props += ['EProp']
  prop = '|'.join(props)
  return "%s %d %s" % (prop, val[1] + 256*val[2], print_uuid(val[3:]))
