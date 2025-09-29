import random
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from threading import Thread

# Adresse du registre où la pression sera stockée
PRESSURE_REGISTER = 0

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


