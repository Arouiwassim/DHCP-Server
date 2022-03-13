LE code source du serveur comprend 6 fichiers au total :


  ** Server.py : c'est le fichier exécutable celui qu'il faut lancer pour mettre le serveur en écoute.
                 Plusieurs aspects de programmation y sont gérés. l'ouverture du soket sur le port spécifié
                 et la réception de donnée notamment. Ce fichier importe en module le fichier ser_fct.py
                 où sont définies toutes les fonctions responsables de la construction de paquets et de 
                 leur envoi sur le réseau.


  ** ser_ft.py : c'est le fichier où sont définies toutes les fonction auxquelles fait appel le fichier exécutable.
                 Les fonctions en question sont :

                 -  send_offer() : qui prend en argument une adresse tirées du pool, une configuration réseau
                                  (pour en tirer les paramètres réseau qui sont l'adresse de la gateway et du serveur DNS). 
                                  Elle prend en argument aussi le paquet réseau formé au sein de la finction même et l'adresse MAC 
                                  de la destination client. AU final elle envoie avec la méthode sendp() de scapy. 

                 - send_ack() : exactement similaire à send_offer sauf que la paquet que celle-ci envoie est de type DHCP 
                                acknowledgement
                
                 - selectadd() : choisit une adresse du pool à suggérer au client DHP. 

                 - acknoack () : Vérifier la disponibilité d'une adresse requise dans les option du message dhcp. 

                 - save2pool() : enregistre dans le pool une un couple d'adresss : adresse ip et adresse 
                                 MAC du client auquel elle a été attribuée. 
                    
                 - poolupdate() : fonction appelée régulièrement pour remettre à jour le pool en supprimant des couples 
                                  les couple ( IP, MAC) dont le bail est expiré. c'est une fonction de désallocation d'adresses. 
                 

                 - get_option(): reupère les valeurs des options DHP par le nom de leur clé. 

    ** cli.py : c'est le script de l'interface de commandes en ligne. Décrit comment les fichiers config.json et pool.json sont modifié 
                depuis une ligne de commande. 

    ** pool.json : fichier de données créé lors de la configuration d'ue adresse réseau. Il s'agit d'une liste d'adresse avec des attributs : 
                   leased : si elle est déjà attribuée ou allowed si elle est prête à l'octroi. 


    ** config.json : c'est le fameux fichiers de configuration qu'on avec les information entrées en ligne de commande
                     ou en accédant au fichier en mode écriture et le modifier proprement avec les paramèters souhaités. 

    ** TEST.py : socket client avec qui envoi tout type de message DHCP client et qui permet de tester le serveur ne local. 
    
    **Mac.json : Liste des @ Mac que le serveur DHCP est autorisé a répondre
    
    **blacklist.json: Liste des @ Mac qui sont bloqué (Le DHCP sever va dorénavant ignorer leurs messages) pour tentative d'attaques.
    
    **attack_logs.txt: Fichier logs qui permet de garder une trace de chaque attaques signalé en ajoutant les @ mac impliqué et la date et l'heure de la detection de l'attaque.
    
    **Starvation.py: Script qui simule la starvation attack
    
    **Dos_Attacks.py : Script qui simule une attaques DOS .
