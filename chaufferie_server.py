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

""""création de la pression et de l'ajustation"""

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
            # Réduire le niveau des cuves
            niveau_cuve1 = context[slave_id].getValues(3, NIVEAU_REGISTER_CUVE1, count=1)[0]
            niveau_cuve2 = context[slave_id].getValues(3, NIVEAU_REGISTER_CUVE2, count=1)[0]
            niveau_cuve3 = context[slave_id].getValues(3, NIVEAU_REGISTER_CUVE3, count=1)[0]
            context[slave_id].setValues(3, NIVEAU_REGISTER_CUVE1, [max(niveau_cuve1 - 5, 100)])
            context[slave_id].setValues(3, NIVEAU_REGISTER_CUVE2, [max(niveau_cuve2 - 5, 100)])
            context[slave_id].setValues(3, NIVEAU_REGISTER_CUVE3, [max(niveau_cuve3 - 5, 100)])


        """si vanne autoregulation lue dans le registre à l'adresse 11 est à 1 alors diminution de la pression"""
        vanne_autoregulation = context[slave_id].getValues(3, VANNE_AUTOREGULATION, count=1)[0]
        if vanne_autoregulation == 1:
            pressure -= 5
        # Mise à jour du registre
        context[slave_id].setValues(3, PRESSURE_REGISTER, [pressure])
        time.sleep(1)

""""création de la température et de l'ajustation"""
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


        #si température trop basse alors activation du chauffage
        if temperature < 150:
            context[slave_id].setValues(3, 40, [1])  # Activer le chauffage
        #si trop chaud alors recyclement de l'eau qui retourne dans les cuves puis réinjecter dans le système
        if temperature > 250:
            context[slave_id].setValues(3, 41, [1])  # Activer le recyclage
            #alors augmentation niveau des cuves et diminution de la pression
            pressure = context[slave_id].getValues(3, PRESSURE_REGISTER, count=1)[0]
            pressure -= 10
            context[slave_id].setValues(3, PRESSURE_REGISTER, [pressure])
            #augmentation niveau des cuves
            niveau_cuve1 = context[slave_id].getValues(3, NIVEAU_REGISTER_CUVE1, count=1)[0]
            niveau_cuve2 = context[slave_id].getValues(3, NIVEAU_REGISTER_CUVE2, count=1)[0]
            niveau_cuve3 = context[slave_id].getValues(3, NIVEAU_REGISTER_CUVE3, count=1)[0]
            #on regarde le  niveau des cuves et le plus bas augmente, il faut une uniformisation des niveaux
            if niveau_cuve1 <= niveau_cuve2 and niveau_cuve1 <= niveau_cuve3:
                niveau_cuve1 += 50
                niveau_cuve2 -= 20
                niveau_cuve3 -= 30   
            elif niveau_cuve2 <= niveau_cuve1 and niveau_cuve2 <= niveau_cuve3:
                niveau_cuve2 += 50
                niveau_cuve1 -= 30
                niveau_cuve3 -= 20
            elif niveau_cuve3 <= niveau_cuve1 and niveau_cuve3 <= niveau_cuve2:
                niveau_cuve3 += 50
                niveau_cuve1 -= 20
                niveau_cuve2 -= 30

        # Mise à jour du registre
        context[slave_id].setValues(3, TEMPERATURE_REGISTER, [temperature])
        time.sleep(1)

""""création des capteurs de niveau d'eau des 3 cuves"""
def niveau_cuve_simulation(context, cuve_register, slave_id=0x00):
    """Simule la variation du niveau d'une cuve."""
    niveau = 500  # Niveau initial (ex: 50.0%, multiplié par 10)
    while True:
        # Variation aléatoire du niveau
        niveau += random.randint(-5, 5)
        if niveau < 100:
            niveau = 100
        if niveau > 900:
            niveau = 900
        # Mise à jour du registre correspondant à la cuve
        context[slave_id].setValues(3, cuve_register, [niveau])
        time.sleep(1)

"""création du compteur de saison"""
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

"""Différencier température externe et interne, il faut stabiliser la température dans les tuyaux à 60°C"""
def temperature_tuyaux(context, slave_id=0x00):
    """Simule une variation de température toutes les secondes."""
    alerte_temperature = 0
    temperature_tuyaux = 600  # Température initiale (ex: 60.0°C, multipliée par 10)
    while True:
        # Variation aléatoire de la température
        temperature_tuyaux += random.randint(-3, 3)
        if temperature_tuyaux < 500:
            alerte_temperature = 1
        if temperature_tuyaux > 700:
            alerte_temperature = 2
        else:
            alerte_temperature = 0
        # Mise à jour du registre
        context[slave_id].setValues(3, TEMPERATURE_TUYAUX, [temperature_tuyaux])
        time.sleep(1)





if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 100 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [0]*100) 
    )
    context = ModbusServerContext(devices=device, single=True)


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
    # Lancement des threads de simulation des niveaux des cuves
    cuve1_thread = Thread(target=niveau_cuve_simulation, args=(context, NIVEAU_REGISTER_CUVE1))
    cuve1_thread.daemon = True
    cuve1_thread.start()

    cuve2_thread = Thread(target=niveau_cuve_simulation, args=(context, NIVEAU_REGISTER_CUVE2))
    cuve2_thread.daemon = True
    cuve2_thread.start()

    cuve3_thread = Thread(target=niveau_cuve_simulation, args=(context, NIVEAU_REGISTER_CUVE3))
    cuve3_thread.daemon = True
    cuve3_thread.start()


    # Démarrage du serveur Modbus TCP sur le port 502
    print("Serveur Modbus TCP démarré sur le port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))