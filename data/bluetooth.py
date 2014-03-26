# (c) 2014 Productize <joost@productize.be>

import printers
from attr import Attr

attrs= [

  # services
  Attr([0x18, 0x00], "Generic Access"),
  Attr([0x18, 0x01], "Generic Attribute"),
  Attr([0x18, 0x02], "Immediate Alert"),
  Attr([0x18, 0x03], "Link Loss"),
  Attr([0x18, 0x04], "Tx Power"),
  Attr([0x18, 0x05], "Current Time"),
  Attr([0x18, 0x06], "Reference Time Update"),
  Attr([0x18, 0x07], "Next DST Change Service"),
  Attr([0x18, 0x08], "Glucose"),
  Attr([0x18, 0x09], "Health Thermometer"),
  Attr([0x18, 0x0A], "Device Information"),
  Attr([0x18, 0x0D], "Heart Rate"),
  Attr([0x18, 0x0E], "Phone Alert Status"),
  Attr([0x18, 0x0F], "Battery"),
  Attr([0x18, 0x10], "Blood Pressure"),
  Attr([0x18, 0x11], "Alert Notification"),
  Attr([0x18, 0x12], "Human Interface"),
  Attr([0x18, 0x13], "Scan Parameters"),
  Attr([0x18, 0x14], "Running Speed and Cadence"),
  Attr([0x18, 0x16], "Cycling Speed and Cadence"),
  Attr([0x18, 0x18], "Cycling Power"),
  Attr([0x18, 0x19], "Location and Navigation"),

  # declarations
  Attr([0x28, 0x00], "Primary", printers.Uuid),
  Attr([0x28, 0x01], "Secundary", printers.Uuid),
  Attr([0x28, 0x02], "Include", printers.Uuid),
  Attr([0x28, 0x03], "Characteristic", printers.Char),

  Attr([0x29, 0x00], "Characteristic Extented Properties"),
  Attr([0x29, 0x01], "Characteristic User Description", printers.String),
  Attr([0x29, 0x02], "Client Characteristic Configuration", printers.ClientCharConf),
  Attr([0x29, 0x03], "Server Characteristic Configuration"),
  Attr([0x29, 0x04], "Characteristic Presentation Format"),
  Attr([0x29, 0x05], "Characteristic Aggregate Format"),
  Attr([0x29, 0x06], "Valid Range"),
  Attr([0x29, 0x07], "External Report Reference"),
  Attr([0x29, 0x08], "Report Reference"),

  # characteristics
  Attr([0x2A, 0x00], "Device Name", printers.String),
  Attr([0x2A, 0x01], "Appearance"),
  Attr([0x2A, 0x02], "Peripheral Privacy Flag"),
  Attr([0x2A, 0x03], "Reconnection Address"),
  Attr([0x2A, 0x04], "Peripheral Preferred Connection Parameters"),
  Attr([0x2A, 0x05], "Service Changed"),

  Attr([0x2A, 0x5B], "CSC Measurement", printers.CSCMeasurement),
  Attr([0x2A, 0x5C], "CSC Feature", printers.CSCFeature),
]

class Vendor:

 ids = []
