
# Finished
def get_mac(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        mac_address = open('/sys/class/net/%s/address' % interface).read()
    except Exception as ex:
        # print(ex)
        mac_address = "C8-21-58-32-A6-54"
    return mac_address[0:17]


