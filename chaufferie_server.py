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

""""création de la pression et de l'ajustation"""

def pressure_simulation(context, slave_id=0x00):
    """Il y a une dimminution de préssion toutes les secondes. et il faut envoyer une information à "pompe1" pour la mettre à 1"""
    pressure = 1000  # Pression initiale (ex: 100.0 kPa, multipliée par 10)
    while True:
        # Variation aléatoire de la pression
        pressure -= random.randint(1, 5)
        if pressure < 800:
            pompe1 = 1  # Activer la pompe
        if pressure > 1200:
            vanne1 = 1  # Ouvrir la vanne
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
    # Création du datastore Modbus avec un registre de 10 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [200]*10)  # 20.0°C initial
    )
    context = ModbusServerContext(devices=device, single=True)

    # Lancement du thread de simulation de température
    sim_thread = Thread(target=temperature_simulation, args=(context,))
    sim_thread.daemon = True
    sim_thread.start()

    # Démarrage du serveur Modbus TCP sur le port 502
    print("Serveur Modbus TCP démarré sur le port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))