#!/usr/bin/env python

# loosely based on bglib_test_scanner.py released under MIT license by Jeff Rowberg, who also works for BlueGiga

# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from productize import parse_data
from ble import BLE

class CollectThread(QtCore.QThread):

  def __init__(self, ble, parent=None):
    super(CollectThread, self).__init__(parent)
    self._stop = False
    self.ble = ble

  def run(self):
    while not self._stop:
      self.ble.check_activity()
      time.sleep(0.01)

  def stop(self):
    self._stop = True

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

  ble = BLE(port_name, baud_rate)
  ct = CollectThread(ble)
  ble.scan_response.connect(print_scan_response)
  ct.start()
  return app.exec_()

if __name__ == '__main__':
  run()
