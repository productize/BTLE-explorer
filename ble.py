# (c) 2014 Productize <joost@productize.be>

import serial, time

import bglib
from PySide import QtCore

# https://www.bluetooth.org/en-us/specification/assigned-numbers/generic-access-profile
GAP_AD_TYPE_FLAGS = 0x01
GAP_AD_TYPE_LOCALNAME_COMPLETE = 0x09
GAP_AD_TYPE_TX_POWER = 0x0A
GAP_AD_TYPE_SLAVE_CON_INTERVAL_RANGE = 0x12
GAP_AD_TYPE_VENDOR = 0xFF

class ActivityThread(QtCore.QThread):

  def __init__(self, ble, parent=None):
    super(ActivityThread, self).__init__(parent)
    self._stop = False
    self.ble = ble

  def run(self):
    while not self._stop:
      self.ble.check_activity()
      time.sleep(0.01)

  def stop(self):
    self._stop = True


class BLE(QtCore.QObject):
  scan_response = QtCore.Signal(dict)
  connection_status = QtCore.Signal(int, str, int)
  timeout = QtCore.Signal()
  service_result = QtCore.Signal(int, list, int, int)
  procedure_completed = QtCore.Signal(int)
  info_found = QtCore.Signal(int, int, list)
  attr_value = QtCore.Signal(int, int, int, list)

  CONNECTED = 0

  def __init__(self, baud_rate, packet_mode = False):
    import data
    super(BLE, self).__init__()
    self.led = False
    self.port = None
    self.baud_rate = baud_rate
    self.packet_mode = packet_mode
    self.address = None
    self.uuid = data.UUID()
    self.handles_to_read = []

  def address_response(self, sender, args):
    self.address = ':'.join(['%02X' % b for b in args['address'][::-1]])
    self.auto_detected = True

  def auto_detect_serial(self):
    import glob
    glist = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/cu.usbmodem*')
    self.auto_detected = False
    for port in glist:
      print "trying", port
      ble = None
      ble = bglib.BGLib()
      ble.package_mode = self.packet_mode
      ble.ble_rsp_system_address_get += self.address_response
      ser = serial.Serial(port, self.baud_rate, timeout=1)
      ser.flushInput()
      ser.flushOutput()
      ble.send_command(ser, ble.ble_cmd_system_address_get())
      time.sleep(0.1)
      try:
        ble.check_activity(ser, 1)
      except:
        pass
      if self.auto_detected:
        self.port = port
        self.ser = ser
        self.ble = ble
        print "Using serial:", port
        return
      else:
        ser.close()
    raise Exception("Serial port not found")

  def start(self, port = None):
    if port is None:
      self.auto_detect_serial()
    else:
      self.ble = bglib.BGLib()
      self.ble.packet_mode = self.packet_mode
      self.ble.ble_rsp_system_address_get += self.address_response
    ble = self.ble
    ble.on_timeout += self.on_timeout
    ble.ble_evt_gap_scan_response += self.handle_scan_response
    self.ser = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=1)
    self.ser.flushInput()
    self.ser.flushOutput()
    ser = self.ser
    # disconnect if we are connected already
    self.send_command(ble.ble_cmd_connection_disconnect(0))
    ble.check_activity(ser, 1)
    # stop advertising if we are advertising already
    self.send_command(ble.ble_cmd_gap_set_mode(0, 0))
    ble.check_activity(ser, 1)
    # stop scanning if we are scanning already
    self.send_command(ble.ble_cmd_gap_end_procedure())
    ble.check_activity(ser, 1)
    # set scan parameters
    self.send_command(ble.ble_cmd_gap_set_scan_parameters(0xC8, 0xC8, 1))
    ble.check_activity(ser, 1)
    # start scanning now
    self.send_command(ble.ble_cmd_gap_discover(1))
    ble.check_activity(ser, 1)
    # IO port stuff for LED; doesn't work currently
    self.send_command(ble.ble_cmd_hardware_io_port_config_pull(0, 0, 0))
    self.send_command(ble.ble_cmd_hardware_io_port_config_direction(0, 1))
    self.send_command(ble.ble_cmd_hardware_io_port_config_function(0, 0))
    self.send_command(ble.ble_cmd_hardware_io_port_write(0, 1, 0))
    # handle connections
    self.ble.ble_evt_connection_status += self.handle_connection_status
    # handle service info
    self.ble.ble_evt_attclient_group_found += self.handle_attclient_group_found
    # get local address
    ble.send_command(ser, ble.ble_cmd_system_address_get())
    ble.check_activity(ser, 1)
    print "local device:", self.address
    self.ble.ble_evt_attclient_procedure_completed += self.handle_attclient_procedure_completed
    self.ble.ble_evt_attclient_find_information_found += self.handle_attclient_information_found
    self.ble.ble_evt_attclient_attribute_value += self.handle_attclient_attribute_value

  def send_command(self, cmd):
    return self.ble.send_command(self.ser, cmd)

  def on_timeout(self, sender, args):
    # might want to try the following lines to reset, though it probably
    # wouldn't work at this point if it's already timed out:
    #ble.send_command(ser, ble.ble_cmd_system_reset(0))
    #ble.check_activity(ser, 1)
    print "BGAPI parser timed out. Make sure the BLE device is in a known/idle state."
    self.timeout.emit()

  def handle_scan_response(self, sender, args):
    if self.led == False:
      self.send_command(self.ble.ble_cmd_hardware_io_port_write(0, 1, 1))
      self.led = True
    else:
      self.send_command(self.ble.ble_cmd_hardware_io_port_write(0, 1, 0))
      self.led = False
    self.scan_response.emit(args)

  def handle_connection_status(self, sender, args):
    #print sender, args
    if (args['flags'] & 0x05) == 0x05:
      f = ':'.join(['%02X' % b for b in args['address'][::-1]])
      h = args['connection']
      print "Connected to %d %s" % (h, f)
      self.connection_status.emit(h, f, self.CONNECTED)

  def handle_attclient_group_found(self, sender, args):
    #uuid = ''.join(["%02X" % c for c in reversed(args['uuid'])])
    #print "Found attribute group for service: %s start=%d, end=%d" % (uuid, args['start'], args['end'])
    handle = args['connection']
    uuid = args['uuid'][::-1]
    self.service_result.emit(handle, uuid, args['start'], args['end'])

  def handle_attclient_information_found(self, sender, args):
    #print args
    handle = args['connection']
    char = args['chrhandle']
    uuid = args['uuid'][::-1]
    self.info_found.emit(handle, char, uuid)

  def handle_attclient_procedure_completed(self, sender, args):
    handle = args['connection']
    self.procedure_completed.emit(handle)

  def check_activity(self):
    return self.ble.check_activity(self.ser)

  def connect_direct(self, target):
    f = ':'.join(['%02X' % b for b in target[::-1]])
    print "connecting to", f
    address = target
    addr_type = 0 # public
    timeout = 30 # 3 sec
    slave_latency = 0 # disabled
    conn_interval_min = 100/1.25 # in ms
    conn_interval_max = 1000/1.25 # in ms
    self.send_command(self.ble.ble_cmd_gap_connect_direct(
      address, addr_type, conn_interval_min, 
      conn_interval_max, timeout, slave_latency))

  def primary_service_discovery(self, handle):
    # print "service discovery for %d  ..." % handle
    self.send_command(self.ble.ble_cmd_attclient_read_by_group_type(handle, 0x0001, 0xFFFF, list(reversed(self.uuid.attr_by_name['Primary'].uuid))))

  def find_information(self, handle, start, end):
    self.send_command(self.ble.ble_cmd_attclient_find_information(handle, start, end))

  def flags_to_string(self, val):
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

  def data_to_string(self, data):
    pos = 0
    dl = []
    name = ''
    while pos < len(data):
      field_len = data[pos]
      field_type = data[pos+1]
      field_data = data[pos+2:(pos+2+field_len-1)]
      if field_type == GAP_AD_TYPE_FLAGS:
        dl.append("flags:%s" % self.flags_to_string(field_data[0]))
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
        dl.append(self.uuid.vendor_to_string(field_data))
      else:
        dl.append("unknown_field:0x%x" % field_type)
      pos += field_len + 1
    return (name, ' '.join(dl))

  def read_handle(self, handle, chandle):
    self.send_command(self.ble.ble_cmd_attclient_read_by_handle(handle, chandle))

  def read_handles(self, handle, h1, h2):
    self.handles_to_read = range(h1, h2+1)
    self.send_command(self.ble.ble_cmd_attclient_read_by_handle(handle, h1))

  def handle_attclient_attribute_value(self, sender, args):
    chandle = args['atthandle']
    handle = args['connection']
    t = args['type']
    value = args['value']
    self.attr_value.emit(handle, chandle, t, value)
    if self.handles_to_read == []: return
    if chandle in self.handles_to_read:
      self.handles_to_read.remove(chandle)
    if self.handles_to_read == []: return
    self.send_command(self.ble.ble_cmd_attclient_read_by_handle(handle, self.handles_to_read[0]))

  def write_handle(self, handle, chandle, value):
    self.send_command(self.ble.ble_cmd_attclient_write_command(handle, chandle, value))
    time.sleep(0.1)
    self.send_command(self.ble.ble_cmd_attclient_read_by_handle(handle, chandle))
    
