# (c) 2014 Productize <joost@productize.be>

attrs = []

class Vendor:

  ids = [0x004c]


  def _decode_ibeacon(self, data):
    # see also http://developer.radiusnetworks.com/2013/10/01/reverse-engineering-the-ibeacon-profile.html
    # as linked from http://stackoverflow.com/questions/18906988/what-is-the-ibeacon-bluetooth-profile
    apple_airlocate_service = [0xe2, 0xc5, 0x6d, 0xb5, 0xdf, 0xfb, 0x48, 0xd2, 0xb0, 0x60, 0xd0, 0xf5, 0xa7, 0x10, 0x96, 0xe0]
    
    # 16 bytes give the apple airlocate service uuid
    if data[0:16] == apple_airlocate_service:
      major = data[17] + 256*data[18]
      minor = data[19] + 256*data[20]
      tx_power = data[21]
      # 8-bit 2s complement conversion
      if tx_power > 127:
        tx_power -= 256
      return "ibeacon:%d:%d:%d" % (major, minor, tx_power)
    else:
       return "ibeacon:unknown%s" % (data[0:16])

  def to_string(self, data):
    # first byte identifies data as an ibeacon message
    # second byte is length
    if data[0] == 0x02 and data[1] == 0x15:
      return self._decode_ibeacon(data[2:])
    else:
      return "apple:unknown[%d,%d]" % (data[0], data[1])
    
    
