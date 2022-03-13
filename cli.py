import json
import os
import sys
from ipaddress import *
import ser_fct
os.chdir(os.path.dirname(os.path.abspath(__file__)))


while True:
    print("Commandes : \n"+"config -> Configurer le serveur.\n"+  
                            "state -> Etat du Serveur.\n"+   
                            "quit   -> quitter  \n"+             
                            "ippool -> Les adresses libres et allouées. \n")
    while True:
        a=input(">")
        if a=="config":
            while True:
                print("Commandes : \n")
                print("network -> Adresse réseau et masque du sous-réseau local.")
                print("allow   -> La plage d’adresses IP à allouer aux clients.")
                print("gateway -> Adresse du routeur par défaut.")
                print("dns     -> Adresse des serveurs DNS.")
                print("lease   -> Durée du bail.")
                print("exit pour revenir.")
                b=input("Config>$")
                if b=="exit":
                    break
                if b=="network":
                    with open('config.json','r+') as f:
                        config=json.load(f)
                        config['network']=input("Entrez l'adresse du réseau local: x.x.x.x/x :\n")
                        json.dump(config,f)
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate()
                        ser_fct.generatepool(config['network'], '') # créer un pool vide 

                if b=="allow":
                    with open('config.json','r+') as f:
                        config=json.load(f)
                        config['poolstart']=input("Borne inférieure de la plage : x.x.x.x :\n")
                        config['poolend']=input("Borne supérieure de la plage : x.x.x.x :\n")
                        json.dump(config,f)
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate()
                
                if b=="dns":
                    with open('config.json','r+') as f:
                        config=json.load(f)
                        config['dns']=input("adresse du serveur DNS : x.x.x.x :\n")
                        json.dump(config,f)
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate() 
                if b=="gateway":
                    with open('config.json','r+') as f:
                        config=json.load(f)
                        config['gateway']=input("adresse du routeur par défaut : x.x.x.x:\n")
                        json.dump(config,f)
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate()  
                if b=="lease":
                     with open('config.json','r+') as f:
                        config=json.load(f)
                        config['lease']=input("la durée de bail par défaut en secondes:\n")
                        json.dump(config,f)
                        f.seek(0)
                        json.dump(config, f, indent=4)
                        f.truncate()  
        if a =="state" :
            print("l'état actuel du serveur")
            with open('pool.json','r+') as f:
                pool = json.load(f)
            print(pool)

        if a =="quit" :
            print("commande line shut down")
            sys.exit()

        
            
                                   
                        
                    
                



    