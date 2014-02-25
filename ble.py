import serial, time

import bglib
from PySide import QtCore

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

  uuid_primary = [0x28, 0x00] # 0x2800
  uuid_secundary = [0x28, 0x01] # 0x2801
  uuid_client_characteristic_configuration = [0x29, 0x02] # 0x2902

  def __init__(self, port, baud_rate, packet_mode = False):
    super(BLE, self).__init__()
    self.led = False
    self.port = port
    self.baud_rate = baud_rate
    self.packet_mode = packet_mode
    self.ble = bglib.BGLib()
    ble = self.ble
    ble.packet_mode = self.packet_mode
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
    print sender, args
    if (args['flags'] & 0x05) == 0x05:
      f = ':'.join(['%02X' % b for b in args['address'][::-1]])
      h = args['connection']
      print "Connected to %d %s" % (h, f)
      self.connection_status.emit(h, f, self.CONNECTED)

  def handle_attclient_group_found(self, sender, args):
    uuid = ''.join(["%02X" % c for c in reversed(args['uuid'])])
    print "Found attribute group for service: %s start=%d, end=%d" % (uuid, args['start'], args['end'])
    handle = args['connection']
    self.service_result.emit(handle, uuid, args['start'], args['end'])

  def check_activity(self):
    return self.ble.check_activity(self.ser)

  def connect_direct(self, target):
    print "connecting to", target
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
    print "service discovery for %d  ..." % handle
    self.send_command(self.ble.ble_cmd_attclient_read_by_group_type(handle, 0x0001, 0xFFFF, list(reversed(BLE.uuid_primary))))

