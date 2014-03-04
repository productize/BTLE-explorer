def print_uuid(val):
  return ''.join(["%02X" % x for x in val])

def print_string(val):
  return ''.join(["%c" % x for x in val])  

def print_default(val):
  return str(val)

