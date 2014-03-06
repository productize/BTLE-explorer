#!/usr/bin/env python

# loosely based on bglib_test_scanner.py released under MIT license by Jeff Rowberg, who also works for BlueGiga

# (c) 2014 Joost Yervante Damad <joost@productize.be>

import sys, time, datetime

from PySide import QtGui, QtCore
from PySide.QtCore import Qt

from data import UUID
from ble import BLE, ActivityThread

def print_scan_response(ble, args):
  print "gap_scan_response",
  t = datetime.datetime.now()
  disp_list = []
  disp_list.append("%ld.%03ld" % (time.mktime(t.timetuple()), t.microsecond/1000))
  disp_list.append("rssi: %d" % args["rssi"])
  disp_list.append("type: %d" % args["packet_type"])
  disp_list.append("from: %s" % ''.join(['%02X' % b for b in args["sender"][::-1]]))
  disp_list.append("adt: %d" % args["address_type"])
  disp_list.append("bond: %d" % args["bond"])
  disp_list.append("name: %s data: %s" % ble.data_to_string(args['data']))
  print ' '.join(disp_list)

def run():
  import signal

  QtCore.QCoreApplication.setOrganizationName("productize")
  QtCore.QCoreApplication.setOrganizationDomain("productize.be")
  QtCore.QCoreApplication.setApplicationName("BTLE tool")
  app = QtGui.QApplication(["BTLE tool"])

  signal.signal(signal.SIGINT, signal.SIG_DFL)

  baud_rate = 115200
  ble = BLE(baud_rate)
  ble.start()
  ct = ActivityThread(ble)
  ble.scan_response.connect(lambda x: print_scan_response(ble, x))
  ct.start()
  return app.exec_()

if __name__ == '__main__':
  run()
