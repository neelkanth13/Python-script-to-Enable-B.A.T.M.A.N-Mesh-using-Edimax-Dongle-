import fcntl, socket, struct
import os
import time

'''
GLOBAL VARIABLES
'''
# In case you are using any other dongle other than Edimax Wi-Fi dongle,
# replace this with the OUI of that dongle's company. For my project I 
# am using Edimax Wi-Fi Dongle.
EDIMAX_MAC_OUI    = "74:da:38"
MESH_NODE_IP_ADDR = "172.27.0.4/16" 
MESH_CELL_ADDRESS = "00:60:1D:01:23:45"

####################################################################
# Function Name: getHwAddr
#
# Description: Get Hardware/MAC address of the interfaces
####################################################################
def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])

#################################################################### 
# Step 1:   
#################################################################### 
# Fetch the mac address of the Wireless interface so that 
# 'batman' mesh can be programmed for the 'Edimax' Wi-Fi
# interface that supports "adhoc" mode.
wlan0_mac = getHwAddr('wlx74da38e1f64c')


#################################################################### 
# Step 2: Get the interface name of Edimax Wi-Fi USB dongle that 
# supports 'adhoc' mode.
#################################################################### 
# Fetch the mac address of the Wireless interface so that 
if EDIMAX_MAC_OUI in wlan0_mac:
    adhoc_wifi_inf = "wlx74da38e1f64c"
    adhoc_wifi_inf_mac = wlan0_mac

print ('Wi-Fi interface name on Raspberry'
       ' pi that supports adhoc mode: [%s] MAC: [%s]'
       %(adhoc_wifi_inf, adhoc_wifi_inf_mac))

# Activate batman-adv
os.system("sudo modprobe batman-adv")

# Disable and configure Wi-Fi interface to adhoc mode.
os.system("sudo ip link set %s down"         %(adhoc_wifi_inf))
os.system("sudo ifconfig %s mtu 1532"        %(adhoc_wifi_inf))
os.system("sudo iwconfig %s mode ad-hoc"     %(adhoc_wifi_inf))
os.system("sudo iwconfig %s essid neel_mesh" %(adhoc_wifi_inf))
os.system("sudo iwconfig %s ap any"          %(adhoc_wifi_inf))
os.system("sudo iwconfig %s channel 8"       %(adhoc_wifi_inf))

# All the nodes in the mesh network should have same CELL address.
# From the man page
# Force the card to register to the access point given by the address, 
#if it is possible.
os.system("sudo iwconfig %s ap %s"           %(adhoc_wifi_inf, 
                                               MESH_CELL_ADDRESS))

time.sleep(1)

os.system("sudo ip link set %s up" %(adhoc_wifi_inf))

time.sleep(1)

# add wlan interface to bat interface    
os.system("sudo batctl if add %s" %(adhoc_wifi_inf))
time.sleep(1)
os.system("sudo ifconfig bat0 up")
time.sleep(5)

# Assign ip address for bat interface which is the mesh interface    
os.system("sudo ifconfig bat0 %s" %(MESH_NODE_IP_ADDR))

