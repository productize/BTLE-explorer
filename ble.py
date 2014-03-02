import serial, time

import bglib
from PySide import QtCore



UUID = dict(

  generic = ([0x18, 0x00], "Generic Access"),
  generic_attr = ([0x18, 0x01], "Generic Attribute"),
  immediate_alert = ([0x18, 0x02], "Immediate Alert"),
  link_loss = ([0x18, 0x03], "Link Loss"),
  time = ([0x18, 0x05], "Current Time"),
  glucose = ([0x18, 0x08], "Glucose"),
  thermo = ([0x18, 0x09], "Health Thermometer"),
  cycle_pow = ([0x18, 0x0A], "Device Information"),
  heart_rate = ([0x18, 0x0D], "Heart Rate"),
  battery = ([0x18, 0x0F], "Battery"),
  blood = ([0x18, 0x10], "Blood Pressure"),
  alert = ([0x18, 0x11], "Alert Notification"),
  human_interface = ([0x18, 0x12], "Human Interface"),
  cycle_speed = ([0x18, 0x16], "Cycling Speed and Cadence"),
  cycle_pow = ([0x18, 0x18], "Cycling Power"),

  primary   = ([0x28, 0x00], "Primary"  ),
  secundary = ([0x28, 0x01], "Secundary"),

  chr_u_dsc = ([0x29, 0x01], "Characteristic User Description"),
  chr_c_cnf = ([0x29, 0x02], "Client Characteristic Configuration"),
)

Immediate Alert	org.bluetooth.service.immediate_alert	0x1802	Adopted
Link Loss	org.bluetooth.service.link_loss	0x1803	Adopted
Location and Navigation	org.bluetooth.service.location_and_navigation	0x1819	Adopted
Next DST Change Service	org.bluetooth.service.next_dst_change	0x1807	Adopted
Phone Alert Status Service	org.bluetooth.service.phone_alert_status	0x180E	Adopted
Reference Time Update Service	org.bluetooth.service.reference_time_update	0x1806	Adopted
Running Speed and Cadence	org.bluetooth.service.running_speed_and_cadence	0x1814	Adopted
Scan Parameters	org.bluetooth.service.scan_parameters	0x1813	Adopted
Tx Power	org.bluetooth.service.tx_power	0x1804	Adopted


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

  CONNECTED = 0

  def __init__(self, baud_rate, packet_mode = False):
    super(BLE, self).__init__()
    self.led = False
    self.port = None
    self.baud_rate = baud_rate
    self.packet_mode = packet_mode
    self.address = None

  def address_response(self, sender, args):
    self.address = ':'.join(['%02X' % b for b in args['address'][::-1]])
    self.auto_detected = True

  def auto_detect_serial(self):
    import glob
    glist = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
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
      ble.check_activity(ser, 1)
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
    ble.on_timeout += self.timeout
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

  def send_command(self, cmd):
    return self.ble.send_command(self.ser, cmd)

  def timeout(self, sender, args):
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
    uuid = ''.join(["%02X" % c for c in reversed(args['uuid'])])
    #print "Found attribute group for service: %s start=%d, end=%d" % (uuid, args['start'], args['end'])
    handle = args['connection']
    self.service_result.emit(handle, uuid, args['start'], args['end'])

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
    self.send_command(self.ble.ble_cmd_attclient_read_by_group_type(handle, 0x0001, 0xFFFF, list(reversed(UUID['primary'][0]))))
