from socket import *
import binascii
from scapy.all import *
import json
import os
from ipaddress import *
import ser_fct
import datetime

serverPort = 67
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#pour permettre la réutilisation d'adresse et le bind() sur des ports réservés
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serverSocket.bind(('',serverPort))

list_mac=[]
count=0
c=0
while True:# le serveur écoute en boucle
    with open('config.json','r+') as f:
        config=json.load(f)
    ser_fct.poolupdate(config['lease'])# rafraichir le pool régulièrement pour effacer les baux expirés.
    print('The server is listening ...') 
    message, clientAddress = serverSocket.recvfrom(2048) #réception en brut
    message=binascii.hexlify(message).decode('utf-8') #décode le message brut
    
    message = str(message) #génère une chaine de hex
    #print(message)
    hwddr = ser_fct.raw_mac(bytes.fromhex(message[56:68])) #recupère l'@ MAC depuis le paquet brut recu
    #print(hwddr)
    raw_packet = binascii.unhexlify(message) # tranformer le string de hex en bytes 
    new_packet= BOOTP(raw_packet) # recevoir les bytes comme un trame avec une pdu DHCP près à l'utilisation par scapy
    #print(new_packet)
    #print("packet DHCP received. See details below : \n")
    #new_packet.show() # pour afficher les champs détaillé du paquet
    Ry_addr = ser_fct.get_option(new_packet[BOOTP].options, 'requested_addr')
    
    #################################Parade aux attakcs#########################################
    #Vérifier si l'addresse Mac qui envoie à notre serveur est autorisé
    with open("Mac.json","r+") as f:
        d=json.load(f)
        lis=[s[:16] for s in d["autorised"]]
        if (new_packet[BOOTP].chaddr.decode()not in lis):
            continue;
            
            
    #Vérifier si l'addresse Mac qui envoie à notre serveur est blacklisté
    with open("blacklist.json","r+") as f:
        d=json.load(f)
        if new_packet[BOOTP].chaddr.decode() in d["blacklist"]:
            continue;

    if new_packet[DHCP].options[0][1]== 3:
       count+=1
       if count>=c:
           c=count
       if len(list_mac) ==0:
          t=time.time()
       list_mac.append(new_packet[BOOTP].chaddr.decode())
       if (count>100 and (time.time()-t)<=6):
           with open("blacklist.json","r+") as f:
                d=json.load(f)
                d['blacklist'].extend(list_mac)
                f.seek(0)
                d['blacklist']=list(dict.fromkeys(d['blacklist']))
                json.dump(d,f,indent=4)
           with open("attack_logs.txt","r+") as f:
                f.write("Warning an attack was detected by @mac {} at {}".format(list(dict.fromkeys(list_mac)),datetime.datetime.now()))
       elif (time.time()-t)>10:
            t=time.time()
            list_mac=[]
            count=0
##########################Parade aux attacks###############################################################################

    #On répond par offer ou ack selon le message reçu
    
    if new_packet[DHCP].options[0][1]== 1 :   #cas d'un discover
        with open('config.json','r+') as f:
            config=json.load(f)
    
        Ry_addr = ser_fct.get_option(new_packet[DHCP].options, 'requested_addr') #chercher l'adresse requise par le discover
        print(Ry_addr)
        if  Ry_addr != None:                 #si une adresse Ry_addr est requise 

                    # vérifier que cette adresse peut être attribuée
            print(ser_fct.ackornack(Ry_addr, config['network'], config['poolstart'], config['poolend']))
            if ser_fct.ackornack(Ry_addr, config['network'], config['poolstart'], config['poolend']):
                ser_fct.send_offer(new_packet,Ry_addr, config, hwddr) # envoyer un offer pour suggérer cette même adresse requise 

        else :      # sinon si aucune adresse n'est requise on propose une nouvelle adresse depuis sélectionné à partir du pool
            y_addr=ser_fct.selectadd(config['network'],config['poolstart'],config['poolend'])
            ser_fct.send_offer(new_packet, y_addr, config, hwddr)


    elif new_packet[DHCP].options[0][1]== 3 : #cas d'un dhcprequest
        with open('config.json','r+') as f:
            config=json.load(f)

        # recupérer l'adresse requise dans le champ requested adresse

        Ry_addr= ser_fct.get_option(new_packet[DHCP].options, 'requested_addr') 

        #vérifier que l'adresse est permise 

        if ser_fct.ackornack(Ry_addr, config['network'], config['poolstart'], config['poolend']): 
            ser_fct.send_ack(new_packet,config, hwddr)   #accepter d'octroyer l'adresse
            ser_fct.save2pool(Ry_addr, hwddr)            # enregistrer cette adresse et l'ientifiant du client servi 

        else :  
            print("Aucune réponse n'est envoyée")     #sinon si adresse non disponible, en suggérer une autre avec un dhcpoffer
            pass                                      #aucun ack ou nack n'est envoyé serveur revient en écoute  
    else :
        pass

    print(c)
  


  
  
