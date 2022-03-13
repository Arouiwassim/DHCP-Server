from textwrap import wrap
import datetime
import os
import sys
import json
import ser_fct
import struct
from ipaddress import *
from scapy.all import *
import socket

clientPort = 68
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
clientSocket.bind(('127.0.0.1',clientPort))

with open('config.json','r+') as f:
    config=json.load(f)
with open('Mac.json','r+') as f:
    mac_add=json.load(f)
hw=random.choice(mac_add['autorised'])
print(hw)
i=0
while True:
   hw=mac_add['autorised'][i]
   resp = Ether(src=hw, dst='ff:ff:ff:ff:ff:ff', type=0x800)
   resp/= IP(src='0.0.0.0', dst='255.255.255.255')
   resp/= UDP(sport=68, dport=67)
   resp/= BOOTP(   op=1, 
                xid= 654321,
                chaddr=hw, 
                ciaddr='0.0.0.0', 
                yiaddr= '0.0.0.0', 
                sname="serveur.Nazih-Nassim-Wassim")
   resp/= DHCP(options=[("message-type","request"),
                     ("server_id",(socket.gethostbyname(socket.gethostname()))),
                     ("subnet_mask",ip_network(config['network']).netmask),
                     ("router", config['gateway']),
                     ("name_server", config['dns']),
                     ("lease_time", int(config['lease'])),
                     ("requested_addr", '192.168.1.1'),
                     "end"]) 
                     
   sendp(resp, iface= 'lo', count=1,inter=0.0001)
   #time.sleep(1)
   i+=1
   if(i==len(mac_add['autorised'])-1):
      i=0
