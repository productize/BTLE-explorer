import serial

import bglib
from PySide import QtCore

class BLE(QtCore.QObject):
  scan_response = QtCore.Signal(dict)
  timeout = QtCore.Signal()

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
    ble.send_command(ser, ble.ble_cmd_connection_disconnect(0))
    ble.check_activity(ser, 1)
    # stop advertising if we are advertising already
    ble.send_command(ser, ble.ble_cmd_gap_set_mode(0, 0))
    ble.check_activity(ser, 1)
    # stop scanning if we are scanning already
    ble.send_command(ser, ble.ble_cmd_gap_end_procedure())
    ble.check_activity(ser, 1)
    # set scan parameters
    ble.send_command(ser, ble.ble_cmd_gap_set_scan_parameters(0xC8, 0xC8, 1))
    ble.check_activity(ser, 1)
    # start scanning now
    ble.send_command(ser, ble.ble_cmd_gap_discover(1))
    ble.check_activity(ser, 1)
    # IO port stuff for LED; doesn't work currently
    ble.ble_cmd_hardware_io_port_config_pull(0, 0, 0)
    ble.ble_cmd_hardware_io_port_config_direction(0, 1)
    ble.ble_cmd_hardware_io_port_config_function(0, 0)
    ble.ble_cmd_hardware_io_port_write(0, 1, 0)

  def timeout(self, sender, args):
    # might want to try the following lines to reset, though it probably
    # wouldn't work at this point if it's already timed out:
    #ble.send_command(ser, ble.ble_cmd_system_reset(0))
    #ble.check_activity(ser, 1)
    print "BGAPI parser timed out. Make sure the BLE device is in a known/idle state."
    self.timeout.emit()

  def handle_scan_response(self, sender, args):
    if self.led == False:
      self.ble.ble_cmd_hardware_io_port_write(0, 1, 1)
      self.led = True
    else:
      self.ble.ble_cmd_hardware_io_port_write(0, 1, 0)
      self.led = False
    self.scan_response.emit(args)

  def check_activity(self):
    return self.ble.check_activity(self.ser)
