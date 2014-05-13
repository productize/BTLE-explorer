# (c) 2014 Productize <joost@productize.be>

from attr import Attr
import printers

class  HumidityPrinter(printers.Default):

  def printv(self, val):
    i = val[0] + 256*val[1]
    return "raw:%d, calc:%d" % (i, -6.0+125.0*i/1024)

class  TemperaturePrinter(printers.Default):

  def printv(self, val):
    i = val[0] + 256*val[1]
    return "raw:%d, calc:%d" % (i, -46.85+175.72*i/4096)
    

attrs = [
  Attr("ac842717-f24c-46f7-bf49-5393f0124f8d", "Count Service"),
  Attr("5b97ab09-9065-478c-9ce8-9c9dcb2c5922", "Count", printers.Int32),
  Attr("47bb55a0-6af8-11e3-981f-0800200c9a66", "Module Temperature", printers.Int8),
  Attr("234b35f7-0bff-47b9-b567-43ff304d62cf", "Module Temperature ADC", printers.Int16),
  Attr("8c1cc1fd-6062-48aa-93e4-35dc351c3487", "Humidity ADC", HumidityPrinter),
  Attr("4f99a937-c182-4956-92ff-34bc8ec10644", "Temperature ADC", TemperaturePrinter),
  Attr("4707d070-5e5c-4e1f-b026-535071b43190", "Blink", printers.Int8),
  Attr("157930d3-1746-40d6-b07c-ed92829e7d54", "ID", printers.String),
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
      print data
      raw_temp = data[0]
      temp = -46.85+175.72*raw_temp/256
      raw_hum = data[1]
      hum = -6+125*raw_hum/256
      mod_temp = data[2]
      return "hum:%d temp:%d mod-temp:%d" % (int(hum), int(temp), int(mod_temp))
    elif product_id == 3:
      print data
      count = data[0] + 256*data[1] + 256*256*data[2] + 256*256*256*data[3]
      return "count:%d" % (count)

    return "unknown"

  def to_string(self, data):
    product_id = data[0] + 256*data[1]
    return self._parse_product(product_id, data[2:])
    
    
