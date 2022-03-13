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

iface = 'usb0'
clientPort = 68
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
clientSocket.bind(('127.0.0.1',clientPort))
hw = get_if_hwaddr(iface)
print(hw)
with open('config.json','r+') as f:
    config=json.load(f)
"""y_addr=ser_fct.selectadd(config['network'],config['poolstart'],config['poolend'])
print(y_addr)
Ry_addr= '192.168.1.19'
print(ser_fct.ackornack(Ry_addr, config['network'], config['poolstart'], config['poolend']))"""
#ser_fct.save2pool('192.168.1.12', '0e:44:f5:ee:21:3c')

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
resp.show2()
#clientSocket.sendto(bytes(resp), ('127.0.1.1', 67))
sendp(resp, iface= 'lo', count=1)
    
print("client sending a discover")  
while True:
    print("client en attente de réponse du serveur")
    reponse, ser_add =clientSocket.recvfrom(2048)
    print(reponse)               
