from import printers import print_uuid, print_string

service = dict(

  generic = ([0x18, 0x00], "Generic Access"),
  generic_attr = ([0x18, 0x01], "Generic Attribute"),
  immediate_alert = ([0x18, 0x02], "Immediate Alert"),
  link_loss = ([0x18, 0x03], "Link Loss"),
  tx_power = ([0x18, 0x04], "Tx Power"),
  time = ([0x18, 0x05], "Current Time"),
  ref_time = ([0x18, 0x06], "Reference Time Update"),
  next_dst = ([0x18, 0x07], "Next DST Change Service"),
  glucose = ([0x18, 0x08], "Glucose"),
  thermo = ([0x18, 0x09], "Health Thermometer"),
  device_info = ([0x18, 0x0A], "Device Information"),
  heart_rate = ([0x18, 0x0D], "Heart Rate"),
  phone_alert = ([0x18, 0x0E], "Phone Alert Status"),
  battery = ([0x18, 0x0F], "Battery"),
  blood = ([0x18, 0x10], "Blood Pressure"),
  alert = ([0x18, 0x11], "Alert Notification"),
  human_interface = ([0x18, 0x12], "Human Interface"),
  scan_para = ([0x18, 0x13], "Scan Parameters"),
  run_speed = ([0x18, 0x14], "Running Speed and Cadence"),
  cycle_speed = ([0x18, 0x16], "Cycling Speed and Cadence"),
  cycle_pow = ([0x18, 0x18], "Cycling Power"),
  loc_nav = ([0x18, 0x19], "Location and Navigation"),

)

attr = dict(

  primary   = ([0x28, 0x00], "Primary", print_uuid),
  secundary = ([0x28, 0x01], "Secundary", print_uuid),
  include   = ([0x28, 0x02], "Include", print_uuid),
  char      = ([0x28, 0x03], "Characteristic"),

  chr_e_pro = ([0x29, 0x00], "Characteristic Extented Properties"),
  chr_u_dsc = ([0x29, 0x01], "Characteristic User Description"),
  chr_c_cnf = ([0x29, 0x02], "Client Characteristic Configuration"),
  chr_s_cnf = ([0x29, 0x03], "Server Characteristic Configuration"),
  chr_p_for = ([0x29, 0x04], "Characteristic Presentation Format"),
  chr_a_for = ([0x29, 0x05], "Characteristic Aggregate Format"),
  chr_valid = ([0x29, 0x06], "Valid Range"),
  chr_exter = ([0x29, 0x07], "External Report Reference"),
  chr_repor = ([0x29, 0x08], "Report Reference"),

  devi_name = ([0x2A, 0x00], "Device Name", print_string),
  appearanc = ([0x2A, 0x01], "Appearance"),
  per_pri_f = ([0x2A, 0x02], "Peripheral Privacy Flag"),
  reconnect = ([0x2A, 0x03], "Reconnection Address"),
  per_pref_ = ([0x2A, 0x04], "Peripheral Preferred Connection Parameters"),
)

class Vendor:

 ids = []
