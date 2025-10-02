import random
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from threading import Thread

# Adresse du registre où la pression sera stockée
PRESSURE_REGISTER = 0
TEMPERATURE_REGISTER = 1
NIVEAU_REGISTER_CUVE1 = 2
NIVEAU_REGISTER_CUVE2 = 3
NIVEAU_REGISTER_CUVE3 = 4
VANNE_VILLE_REGISTER = 10  # adresse de la vanne de ville
VANNE_AUTOREGULATION = 11  # 0 = fermée, 1 = ouverte
POMPE_AUTOREGULATION = 12  # 0 = éteinte, 1 = allumée
SAISON_VARIATION = 20  # 0 = Hiver, 1 = Printemps, 2 = Été, 3 = Automne
TEMPERATURE_TUYAUX = 21  # Température des tuyaux
CHAUFFAGE = 5  # 0 = éteint, 1 = allumé
CHAUFFAGE_MANUEL = 6  # 0 = éteint, 1 = allumé

def pressure_simulation(context, slave_id=0x00):
    """Il y a une diminution de préssion toutes les secondes. et il faut envoyer une information à "pompe1" pour la mettre à 1"""
    pressure = 1000  # Pression initiale (ex: 100.0 kPa, multipliée par 10)
    while True:
        # Lire l'état de la vanne
        vanne_ville = context[slave_id].getValues(3, VANNE_VILLE_REGISTER, count=1)[0]
        if vanne_ville == 1:
            # Si la vanne est ouverte, la pression chute plus vite
            pressure -= 10
        
        if pressure < 800:
            """ecrire dans le registre à l'adresse 12 la valeur 1 pour activer la pompe"""
            context[slave_id].setValues(3, POMPE_AUTOREGULATION, [1])

        if pressure > 1200:
            """ecrire dans le registre à l'adresse 11 la valeur 1 pour activer la vanne autoregulation"""
            context[slave_id].setValues(3, VANNE_AUTOREGULATION, [1])
        
        """si pression entre 900 et 1000 alors arret de pompe et fermeture vanne autoregulation"""
        if pressure >= 900 and pressure <= 1000:
                context[slave_id].setValues(3, POMPE_AUTOREGULATION, [0])
                context[slave_id].setValues(3, VANNE_AUTOREGULATION, [0])

        """si valeur pompe lue dans le registre à l'adresse 12 est à 1 alors augmentation de la pression"""
        pompe_autoregulation = context[slave_id].getValues(3, POMPE_AUTOREGULATION, count=1)[0]
        if pompe_autoregulation == 1:
            pressure += 5

        """si vanne autoregulation lue dans le registre à l'adresse 11 est à 1 alors diminution de la pression"""
        vanne_autoregulation = context[slave_id].getValues(3, VANNE_AUTOREGULATION, count=1)[0]
        if vanne_autoregulation == 1:
            pressure -= 5

        # Mise à jour du registre
        context[slave_id].setValues(3, PRESSURE_REGISTER, [pressure])
        time.sleep(1)

def temperature_simulation(context, slave_id=0x00):
    """Simule une variation de température toutes les secondes."""
    temperature = 200  # Température initiale (ex: 20.0°C, multipliée par 10)
    while True:
        # Variation aléatoire de la température récupération de la saison
        saison = context[slave_id].getValues(3, 20, count=1)[0]
        if saison == 0:  # Hiver
            temperature += random.randint(-8, -2)
        elif saison == 2:  # Été
            temperature += random.randint(2, 8)
        elif saison == 1:  # Printemps
            temperature += random.randint(-2, 7)
        elif saison == 3:  # Automne
            temperature += random.randint(-6, 1)
        if temperature < 30:
            temperature = 30
        if temperature > 400:
            temperature = 400

        # Mise à jour du registre
        context[slave_id].setValues(3, TEMPERATURE_REGISTER, [temperature])
        time.sleep(1)

def gestion_cuves(context, slave_id=0x00):
    """Gère les niveaux des trois cuves dans un seul thread"""
    niveaux = [500, 500, 500]  # Niveaux initiaux des trois cuves
    registres_cuves = [NIVEAU_REGISTER_CUVE1, NIVEAU_REGISTER_CUVE2, NIVEAU_REGISTER_CUVE3]
    
    while True:
        # Vérifier si le coil de remplissage est activé
        coil_remplir_cuves = context[slave_id].getValues(1, 1, count=1)[0]
        if coil_remplir_cuves:
            # Remettre toutes les cuves à 500
            for i in range(3):
                niveaux[i] = 500
                context[slave_id].setValues(3, registres_cuves[i], [niveaux[i]])
            
            # Réinitialiser le coil
            context[slave_id].setValues(1, 1, [0])

        # Vérifier si la pompe est active pour réduire les niveaux
        pompe_autoregul = context[slave_id].getValues(3, POMPE_AUTOREGULATION, count=1)[0]
        if pompe_autoregul == 1:
            for i in range(3):
                niveaux[i] = max(niveaux[i] - 10, 100)
                context[slave_id].setValues(3, registres_cuves[i], [niveaux[i]])

        time.sleep(1)

def compteur_simulation(context, slave_id=0x00):
    compteur = 0
    saison = context[slave_id].getValues(3, 20, count=1)[0]  # récupère la valeur du registre 20
    while True:
        compteur += 1
        if compteur >= 30: # toutes les 30 secondes, changement de saison
            saison += 1
            compteur = 0
        if saison > 3:
            saison = 0
        context[slave_id].setValues(3, 19, [compteur])#affiche valeur du compteur
        context[slave_id].setValues(3, 20, [saison])
        time.sleep(1)

def temperature_tuyaux(context, slave_id=0x00):
    """Simule une variation de température toutes les secondes."""
    alerte_temperature = 0
    temperature_tuyaux = 600  # Température initiale (ex: 60.0°C, multipliée par 10)
    while True:
        # Variation aléatoire de la température
        if temperature_tuyaux < 500:
            alerte_temperature = 1
        if temperature_tuyaux > 700:
            alerte_temperature = 2
        else:
            alerte_temperature = 0

        pompe_autoregulation = context[slave_id].getValues(3, POMPE_AUTOREGULATION, count=1)[0]
        temperature = context[slave_id].getValues(3, TEMPERATURE_REGISTER, count=1)[0]
        if pompe_autoregulation == 1:
            # Pompe active -> refroidissement continu : -10 unités ( = -1.0°C si échelle x10) par tick
            temperature_tuyaux = max(temperature_tuyaux - 10, 0)
            
        if temperature_tuyaux < temperature:
            temperature_tuyaux = temperature

        chauffage_manuel = context[slave_id].getValues(3, CHAUFFAGE_MANUEL, count=1)[0]  # Récupérer l'état du chauffage manuel
        if chauffage_manuel == 1:
                temperature_tuyaux = context[slave_id].getValues(3, TEMPERATURE_TUYAUX, count=1)[0]
                temperature_tuyaux += 5
                context[slave_id].setValues(3, TEMPERATURE_TUYAUX, [temperature_tuyaux])
    
        # Mise à jour du registre
        context[slave_id].setValues(3, TEMPERATURE_TUYAUX, [temperature_tuyaux])
        context[slave_id].setValues(3, 22, [alerte_temperature])  # registre d'alerte
        time.sleep(1)

if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 100 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*10)  # 10 coils pour les commandes
    )
    context = ModbusServerContext(devices=device, single=True)
    context[0].setValues(3, TEMPERATURE_TUYAUX, [600])  # 60°C
    context[0].setValues(3, NIVEAU_REGISTER_CUVE1, [500])  # Cuve 1 à 50%
    context[0].setValues(3, NIVEAU_REGISTER_CUVE2, [500])  # Cuve 2 à 50%
    context[0].setValues(3, NIVEAU_REGISTER_CUVE3, [500])  # Cuve 3 à 50%
    
    # Lancement du thread de simulation de la température des tuyaux
    tuyaux_thread = Thread(target=temperature_tuyaux, args=(context,))
    tuyaux_thread.daemon = True
    tuyaux_thread.start()

    # Lancement du thread de simulation de compteur
    compteur_thread = Thread(target=compteur_simulation, args=(context,))
    compteur_thread.daemon = True
    compteur_thread.start()

    # Lancement du thread de simulation de température
    sim_thread = Thread(target=temperature_simulation, args=(context,))
    sim_thread.daemon = True
    sim_thread.start()
   
    # Lancement du thread de simulation de pression
    pres_thread = Thread(target=pressure_simulation, args=(context,))
    pres_thread.daemon = True
    pres_thread.start()
    
    # Lancement d'un SEUL thread pour gérer les trois cuves
    cuves_thread = Thread(target=gestion_cuves, args=(context,))
    cuves_thread.daemon = True
    cuves_thread.start()

    # Démarrage du serveur Modbus TCP sur le port 502
    print("Serveur Modbus TCP démarré sur le port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))