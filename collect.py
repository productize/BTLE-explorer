#!/usr/bin/env python

# loosely based on bglib_test_scanner.py released under MIT license by Jeff Rowberg, who also works for BlueGiga

import bglib, serial, time, datetime

# handler to notify of an API parser timeout condition
def my_timeout(sender, args):
    # might want to try the following lines to reset, though it probably
    # wouldn't work at this point if it's already timed out:
    #ble.send_command(ser, ble.ble_cmd_system_reset(0))
    #ble.check_activity(ser, 1)
    print "BGAPI parser timed out. Make sure the BLE device is in a known/idle state."

GAP_AD_TYPE_FLAGS = 0x01
GAP_AD_TYPE_LOCALNAME_COMPLETE = 0x09
GAP_AD_TYPE_TX_POWER = 0x0A
GAP_AD_TYPE_VENDOR = 0xFF

def parse_product(product_id, data):
  if product_id == 0:
    lux = data[0] + 256*data[1]
    return "lux:%d" % lux

def parse_vendor(data):
  vendor = data[0] + 256*data[1]
  if vendor == 0xffff:
    product_id == data[2]
    return parse_product(product_id, data[3:])
  else:
    return "vendor:%04X" % vendor

def parse_data(data):
  pos = 0
  dl = []
  while pos < len(data):
    field_len = data[pos]
    field_type = data[pos+1]
    field_data = data[pos+2:(pos+2+field_len-1)]
    if field_type == GAP_AD_TYPE_FLAGS:
      dl.append("flags:%02X" % field_data[0])
    elif field_type == GAP_AD_TYPE_LOCALNAME_COMPLETE:
      dl.append("name:%s" % (''.join(['%c' % b for b in field_data]))
    elif field_type == GAP_AD_TYPE_TX_POWER:
      dl.append("tx:%ddB" % (field_data[0]))
    elif field_type == GAP_AD_VENDOR:
      dl_append(parse_vendor(field_data))
    else:
      dl.append("unknown:%d" % field_type)
    pos += field_len + 1
  return ' '.join(dl)
      
      

# handler to print scan responses with a timestamp
def my_ble_evt_gap_scan_response(sender, args):
    print "gap_scan_response",
    t = datetime.datetime.now()
    disp_list = []
    disp_list.append("%ld.%03ld" % (time.mktime(t.timetuple()), t.microsecond/1000))
    disp_list.append("rssi: %d" % args["rssi"])
    disp_list.append("type: %d" % args["packet_type"])
    disp_list.append("from: %s" % ''.join(['%02X' % b for b in args["sender"][::-1]]))
    disp_list.append("adt: %d" % args["address_type"])
    disp_list.append("bond: %d" % args["bond"])
    disp_list.append("data: %s" % parse_data(args['data']))
    print ' '.join(disp_list)

def main():
    port_name = "/dev/ttyACM3"
    baud_rate = 115200
    packet_mode = False

    ble = bglib.BGLib()
    ble.packet_mode = packet_mode

    # add handler for BGAPI timeout condition (hopefully won't happen)
    ble.on_timeout += my_timeout

    # add handler for the gap_scan_response event
    ble.ble_evt_gap_scan_response += my_ble_evt_gap_scan_response

    # create serial port object and flush buffers
    ser = serial.Serial(port=port_name, baudrate=baud_rate, timeout=1)
    ser.flushInput()
    ser.flushOutput()

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

    while (1):
        # check for all incoming data (no timeout, non-blocking)
        ble.check_activity(ser)

        # don't burden the CPU
        time.sleep(0.01)

if __name__ == '__main__':
    main()
