#!/usr/bin/env python

# loosely based on bglib_test_scanner.py released under MIT license by Jeff Rowberg, who also works for BlueGiga

# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, serial, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

import bglib
from productize import parse_data

class CollectThread(QtCore.QThread):

  scan_response = QtCore.Signal(dict)
  timeout = QtCore.Signal()

  def __init__(self, port, baud_rate, packet_mode = False, parent = None):
    super(CollectThread, self).__init__(parent)
    self._stop = False
    self.port = port
    self.baud_rate = baud_rate
    self.packet_mode = packet_mode
    self.setup_ble()

  def setup_ble(self):
    ble = bglib.BGLib()
    self.ble = ble
    ble.packet_mode = self.packet_mode
    ble.on_timeout += self.timeout
    ble.ble_evt_gap_scan_response += self.handle_scan_response
    ser = serial.Serial(port=self.port, baudrate=self.baud_rate, timeout=1)
    ser.flushInput()
    ser.flushOutput()
    self.ser = ser
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

  def run(self):
    while not self._stop:
      self.ble.check_activity(self.ser)
      time.sleep(0.01)

  def stop(self):
    self._stop = True

  def timeout(self, sender, args):
    # might want to try the following lines to reset, though it probably
    # wouldn't work at this point if it's already timed out:
    #ble.send_command(ser, ble.ble_cmd_system_reset(0))
    #ble.check_activity(ser, 1)
    print "BGAPI parser timed out. Make sure the BLE device is in a known/idle state."
    self.timeout.emit()

  def handle_scan_response(self, sender, args):
    self.scan_response.emit(args)

 
def print_scan_response(args):
  print "gap_scan_response",
  t = datetime.datetime.now()
  disp_list = []
  disp_list.append("%ld.%03ld" % (time.mktime(t.timetuple()), t.microsecond/1000))
  disp_list.append("rssi: %d" % args["rssi"])
  disp_list.append("type: %d" % args["packet_type"])
  disp_list.append("from: %s" % ''.join(['%02X' % b for b in args["sender"][::-1]]))
  disp_list.append("adt: %d" % args["address_type"])
  disp_list.append("bond: %d" % args["bond"])
  disp_list.append("name: %s data: %s" % parse_data(args['data']))
  print ' '.join(disp_list)

def run():
  import signal

  QtCore.QCoreApplication.setOrganizationName("productize")
  QtCore.QCoreApplication.setOrganizationDomain("productize.be")
  QtCore.QCoreApplication.setApplicationName("BTLE tool")
  app = QtGui.QApplication(["BTLE tool"])

  signal.signal(signal.SIGINT, signal.SIG_DFL)

  port_name = "/dev/ttyACM0"
  baud_rate = 115200
  packet_mode = False

  ct = CollectThread(port_name, baud_rate, packet_mode)
  ct.scan_response.connect(print_scan_response)
  ct.start()
  return app.exec_()

if __name__ == '__main__':
  run()
