from socket import *
import binascii
import json
import struct
from ipaddress import *
from scapy.all import *

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#fonction qui retourne une adresse pour le OFFER suivant la configuration et le pool d'adresses attribuées.
def selectadd(netadd,borninf,bornsup):
    with open("pool.json",'r+') as f:
        pool=json.load(f)
    addd=list(ip_network(netadd).hosts())
    for n in addd:
        v=0
        if n>=IPv4Address(borninf) and n<=IPv4Address(bornsup):
            for nn in pool:
                if str(ip_address(n))==nn :
                    v=1
                    break
            if v==0:
                return str(ip_address(n))

#============================================================================================

#Mise à jour du pool suivant le lease time.
def poolupdate(leasetime):
    with open("pool.json","r+") as f:
        pool=json.load(f)
    
    blacklist=[]
    
    for n in pool:
        if((pool[n]["timestamp"]+leasetime)>str(datetime.now().timestamp())):
            blacklist.append(n)
    for nn in blacklist:
        del pool[nn]
    
    with open("pool.json","r+") as f:
        json.dump(pool,f)
        f.seek(0)
        json.dump(pool, f, indent=4)
        f.truncate()

#=======================================================================================================
#Enregistrer l'adresse attribuée dans le pool.
def save2pool(ipadd,macadd):
    with open("pool.json",'r+') as f:
        pool=json.load(f)
        pool[ipadd]={'timestamp':str(datetime.now().timestamp()),'l2add':macadd}
        json.dump(pool,f)
        f.seek(0)
        json.dump(pool, f, indent=4)
        f.truncate()

#==============================================================================================
def get_option(dhcp_options, key): # retourner les valeurs des options DHCP avec leur clé

    must_decode = ['hostname', 'domain', 'vendor_class_id']
    try:
        for i in dhcp_options:
            if i[0] == key:
                # If DHCP Server Returned multiple name servers 
                # return all as comma seperated string.
                if key == 'name_server' and len(i) > 2:
                    return ",".join(i[1:])
                # domain and hostname are binary strings,
                # decode to unicode string before returning
                elif key in must_decode:
                    return i[1].decode()
                else: 
                    return i[1]        
    except:
        pass
#==================================================================================================
def ackornack(ipaddd,netadd,borninf,bornsup):
    interval=False
    in_network=False
    not_in_pool=True

    ipaddd4=IPv4Address(str(ipaddd))
    
    addd=list(ip_network(netadd).hosts())
    for n in addd:
        if ipaddd4==n:
            in_network=True
            break
        
    if ipaddd4>=IPv4Address(borninf) and ipaddd4<=IPv4Address(bornsup):
        interval=True
    with open("pool.json",'r+') as f:
        pool=json.load(f)
        for nn in pool:
            if nn==ipaddd4:
                not_in_pool=False
                break
    
    return (in_network and interval and not_in_pool)

#=======================================================================================
def send_offer(disc_pkt, picked_addr, conf, client_id):
    #fonction qui envoie des DHCPOFFER 
    #Les champs sont rempli proprement depuis le paquet discovery recu 
    #iface = scapy.conf.iface
    hw = get_if_hwaddr('usb0')
    resp = Ether(src=hw, dst=client_id, type=0x800)
    resp/= IP(src=(gethostbyname(gethostname())), dst= ip_network(conf['network']).broadcast_address)
    resp/= UDP(sport=67, dport=68)
    resp/= BOOTP(   op=2, 
                    xid=disc_pkt[BOOTP].xid,
                    hops=disc_pkt[BOOTP].hops,
                    chaddr=client_id, 
                    ciaddr=disc_pkt[BOOTP].ciaddr, 
                    yiaddr=picked_addr, 
                    sname=b"serveur.Nazih-Nassim-Wassim")
    resp/= DHCP(options=[("message-type","offer"), 
                        ("server_id",(gethostbyname(gethostname()))),
                        ("subnet_mask",ip_network(conf['network']).netmask),
                        ("router", conf['gateway']),
                        ("name_server", conf['dns']),
                        ("lease_time", int(conf['lease'])),
                        "end"])
    resp.show2()
    print("DHCPDOFFER being sent ...")
    sendp(resp, count=1)
    
    
#===========================================================================================
def send_ack(req_pkt, conf, client_id):
    #fonction qui envoie des DHCPACK
    #Les champs sont rempli proprement depuis le paquet request recu 
    #iface = scapy.conf.iface
    Ry_addr = IPv4Address(get_option(req_pkt[DHCP].options, 'requested_addr'))
    hw = get_if_hwaddr('usb0')
    resp = Ether(src=hw, dst= client_id, type=0x800)
    resp/= IP(src= (gethostbyname(gethostname())), dst=Ry_addr)
    resp/= UDP(sport=67, dport=68)
    resp/= BOOTP(   op=2, 
                    xid=req_pkt[BOOTP].xid,
                    hops=req_pkt[BOOTP].hops ,
                    chaddr=client_id, 
                    ciaddr=req_pkt[BOOTP].ciaddr, 
                    yiaddr= Ry_addr, 
                    sname="serveur.Nazih-Nassim-Wassim")
    resp/= DHCP(options=[("message-type","ack"), 
                        ("server_id",gethostbyname((gethostname()))),
                        ("subnet_mask",ip_network(conf['network']).netmask),
                        ("router", conf['gateway']),
                        ("domain_name_server", conf['dns']),
                        ("lease_time", int(conf['lease'])),
                        "end"])     
    resp.show2()                     
    sendp(resp, count=1)
    print("DHCPACK being sent ...")
    #==========================================================================
def raw_mac(chaine): #décode une adresse mac depuis le paquet reçu en brut
    mac = ':'.join(map(lambda x: hex(x)[2:].zfill(2), struct.unpack('BBBBBB',chaine)))
    return mac

    #===========================================================================

def generatepool(ipaddd,rec_addr):
    d={}
    dd={"allowed":"False","leased":"True"}
    addd=list(ip_network(ipaddd).hosts())
    for n in addd:
        if n == rec_addr:
            d[str(ip_address(n))]=dd
        with open('pool.json','w') as f:
            json.dump(d,f,indent=4)

