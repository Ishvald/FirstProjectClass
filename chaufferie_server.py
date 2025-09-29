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
vanne_autoregulation = 0  # 0 = fermée, 1 = ouverte
pompe1 = 0  # 0 = éteinte, 1 = allumée

""""création de la pression et de l'ajustation"""

def pressure_simulation(context, slave_id=0x00):
    """Il y a une dimminution de préssion toutes les secondes. et il faut envoyer une information à "pompe1" pour la mettre à 1"""
    pressure = 1000  # Pression initiale (ex: 100.0 kPa, multipliée par 10)
    while True:
        # Lire l'état de la vanne
        vanne_ville = context[slave_id].getValues(3, VANNE_VILLE_REGISTER, count=1)[0]
        if vanne_ville == 1:
            # Si la vanne est ouverte, la pression chute plus vite
            pressure -= 10
        # Variation aléatoire de la pression
        pressure -= random.randint(1, 5)
        if pressure < 800:
            pompe1 = 1  # Activer la pompe
        if pressure > 1200:
            vanne_autoregulation = 1  # Ouvrir la vanne

        """si pompe allumer alors augmentation de la pression"""
        if pompe1 == 1:
            pressure += 5        
        """si vanne autoregulation ouverte alors diminution de la pression"""
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
        # Variation aléatoire de la température
        temperature += random.randint(-2, 2)
        if temperature < 150:
            temperature = 150
        if temperature > 300:
            temperature = 300
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



if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 100 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [0]*100) 
    )
    context = ModbusServerContext(devices=device, single=True)

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