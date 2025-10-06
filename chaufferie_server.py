import random
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from threading import Thread, Lock

# Adresses des registres où les données seront stockées
PRESSURE_REGISTER = 0
TEMPERATURE_REGISTER = 1
NIVEAU_REGISTER_CUVE1 = 2
NIVEAU_REGISTER_CUVE2 = 3
NIVEAU_REGISTER_CUVE3 = 4
VANNE_VILLE_REGISTER = 10  # Adresse de la vanne de ville
VANNE_AUTOREGULATION = 11  # 0 = fermée, 1 = ouverte
POMPE_AUTOREGULATION = 12  # 0 = éteinte, 1 = allumée
SAISON_VARIATION = 20  # 0 = Hiver, 1 = Printemps, 2 = Été, 3 = Automne
COMPTEUR_SAISON = 19  # Compteur pour le changement automatique de saison
TEMPERATURE_TUYAUX = 21  # Température des tuyaux
CHAUFFAGE = 5  # 0 = éteint, 1 = allumé
CHAUFFAGE_MANUEL = 6  # 0 = éteint, 1 = allumé

# Verrou pour synchroniser l'accès aux saisons
saison_lock = Lock()

def pressure_simulation(context, slave_id=0x00):
    """Simule une diminution de pression toutes les secondes et active la pompe si nécessaire"""
    pressure = 1000  # Pression initiale (ex: 100.0 kPa, multipliée par 10)
    while True:
        # Lire l'état de la vanne
        vanne_ville = context[slave_id].getValues(3, VANNE_VILLE_REGISTER, count=1)[0]
        if vanne_ville == 1:
            # Si la vanne est ouverte, la pression baisse plus rapidement
            pressure -= 10
        
        if pressure < 800:
            # Écrire dans le registre à l'adresse 12 la valeur 1 pour activer la pompe
            context[slave_id].setValues(3, POMPE_AUTOREGULATION, [1])

        if pressure > 1200:
            # Écrire dans le registre à l'adresse 11 la valeur 1 pour activer la vanne d'autorégulation
            context[slave_id].setValues(3, VANNE_AUTOREGULATION, [1])
        
        # Si la pression est entre 900 et 1000, arrêter la pompe et fermer la vanne d'autorégulation
        if pressure >= 900 and pressure <= 1000:
                context[slave_id].setValues(3, POMPE_AUTOREGULATION, [0])
                context[slave_id].setValues(3, VANNE_AUTOREGULATION, [0])

        # Si la pompe lue dans le registre à l'adresse 12 est à 1, augmenter la pression
        pompe_autoregulation = context[slave_id].getValues(3, POMPE_AUTOREGULATION, count=1)[0]
        if pompe_autoregulation == 1:
            pressure += 5

        # Si la vanne d'autorégulation lue dans le registre à l'adresse 11 est à 1, diminuer la pression
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
        # Variation aléatoire de la température selon la saison
        with saison_lock:
            saison = context[slave_id].getValues(3, SAISON_VARIATION, count=1)[0]
        
        if saison == 0:  # Hiver
            temperature += random.randint(-8, -2)
        elif saison == 2:  # Été
            temperature += random.randint(2, 8)
        elif saison == 1:  # Printemps
            temperature += random.randint(-2, 7)
        elif saison == 3:  # Automne
            temperature += random.randint(-6, 1)
        
        # Limites de sécurité pour la température
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

def gestion_saisons(context, slave_id=0x00):
    """Gère les saisons dans un seul thread - version corrigée"""
    compteur = 0
    saison_actuelle = 0  # Saison actuelle
    
    while True:
        # Lire la valeur actuelle du registre 20 (peut avoir été modifiée par l'IHM)
        saison_manuelle = context[slave_id].getValues(3, SAISON_VARIATION, count=1)[0]
        
        # Si la saison manuelle est différente de la saison actuelle, c'est que l'IHM a changé la saison
        if saison_manuelle != saison_actuelle and saison_manuelle in [0, 1, 2, 3]:
            with saison_lock:
                saison_actuelle = saison_manuelle
            compteur = 0  # Réinitialiser le compteur
            print(f"Saison changée manuellement: {saison_actuelle}")
        
        # Changement automatique toutes les 30 secondes
        compteur += 1
        if compteur >= 30:  # Toutes les 30 secondes
            with saison_lock:
                saison_actuelle = (saison_actuelle + 1) % 4
                context[slave_id].setValues(3, SAISON_VARIATION, [saison_actuelle])
            compteur = 0
            print(f"Saison changée automatiquement: {saison_actuelle}")
        
        # Mettre à jour le compteur (affichage seulement)
        context[slave_id].setValues(3, COMPTEUR_SAISON, [compteur])
        
        time.sleep(1)

def temperature_tuyaux(context, slave_id=0x00):
    """Simule une variation de température des tuyaux toutes les secondes."""
    alerte_temperature = 0
    temperature_tuyaux = 600  # Température initiale (ex: 60.0°C, multipliée par 10)
    while True:
        # Déterminer l'état de l'alerte température
        if temperature_tuyaux < 500:
            alerte_temperature = 1  # Température trop basse
        elif temperature_tuyaux > 700:
            alerte_temperature = 2  # Température trop élevée
        else:
            alerte_temperature = 0  # Température normale

        pompe_autoregulation = context[slave_id].getValues(3, POMPE_AUTOREGULATION, count=1)[0]
        temperature = context[slave_id].getValues(3, TEMPERATURE_REGISTER, count=1)[0]
        
        if pompe_autoregulation == 1:
            # Pompe active -> refroidissement continu : -10 unités (= -1.0°C si échelle x10) par cycle
            temperature_tuyaux = max(temperature_tuyaux - 10, 0)
            
        # La température des tuyaux ne peut pas descendre en dessous de la température ambiante
        if temperature_tuyaux < temperature:
            temperature_tuyaux = temperature

        chauffage_manuel = context[slave_id].getValues(3, CHAUFFAGE_MANUEL, count=1)[0]  # Récupérer l'état du chauffage manuel
        if chauffage_manuel == 1:
            temperature_tuyaux = context[slave_id].getValues(3, TEMPERATURE_TUYAUX, count=1)[0]
            temperature_tuyaux += 5
            context[slave_id].setValues(3, TEMPERATURE_TUYAUX, [temperature_tuyaux])
    
        # Mise à jour des registres
        context[slave_id].setValues(3, TEMPERATURE_TUYAUX, [temperature_tuyaux])
        context[slave_id].setValues(3, 22, [alerte_temperature])  # Registre d'alerte
        time.sleep(1)

if __name__ == "__main__":
    # Création du datastore Modbus avec un registre de 100 mots
    device = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [0]*10)  # 10 coils pour les commandes
    )
    context = ModbusServerContext(devices=device, single=True)
    
    # Initialisation des valeurs par défaut
    context[0].setValues(3, TEMPERATURE_TUYAUX, [600])  # 60°C
    context[0].setValues(3, NIVEAU_REGISTER_CUVE1, [500])  # Cuve 1 à 50%
    context[0].setValues(3, NIVEAU_REGISTER_CUVE2, [500])  # Cuve 2 à 50%
    context[0].setValues(3, NIVEAU_REGISTER_CUVE3, [500])  # Cuve 3 à 50%
    context[0].setValues(3, SAISON_VARIATION, [0])  # Saison initiale : Hiver
    
    # Lancement du thread de simulation de la température des tuyaux
    tuyaux_thread = Thread(target=temperature_tuyaux, args=(context,))
    tuyaux_thread.daemon = True
    tuyaux_thread.start()

    # Lancement du thread de gestion des saisons
    saison_thread = Thread(target=gestion_saisons, args=(context,))
    saison_thread.daemon = True
    saison_thread.start()

    # Lancement du thread de simulation de température
    sim_thread = Thread(target=temperature_simulation, args=(context,))
    sim_thread.daemon = True
    sim_thread.start()
   
    # Lancement du thread de simulation de pression
    pres_thread = Thread(target=pressure_simulation, args=(context,))
    pres_thread.daemon = True
    pres_thread.start()
    
    # Lancement d'un seul thread pour gérer les trois cuves
    cuves_thread = Thread(target=gestion_cuves, args=(context,))
    cuves_thread.daemon = True
    cuves_thread.start()

    # Démarrage du serveur Modbus TCP sur le port 502
    print("Serveur Modbus TCP démarré sur le port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))
    