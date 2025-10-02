import time
from pymodbus.client import ModbusTcpClient
import tkinter as tk
from tkinter import messagebox
import logging

class AlarmManager:
    def __init__(self, host='127.0.0.1', port=502):
        self.host = host
        self.port = port
        self.last_alerts = {}
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alarms.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_alarms(self):
        """Vérifie toutes les alarmes du système"""
        try:
            client = ModbusTcpClient(self.host, self.port)
            client.connect()
            
            # Lecture de tous les registres nécessaires
            rr = client.read_holding_registers(address=0, count=50)
            
            if rr.isError():
                self.logger.error("Erreur de lecture Modbus")
                return
            
            registers = rr.registers
            
            # Extraction des valeurs
            pression = registers[0] / 10.0
            temperature = registers[1] / 10.0
            niveau_cuve1 = registers[2] / 10.0
            niveau_cuve2 = registers[3] / 10.0
            niveau_cuve3 = registers[4] / 10.0
            temperature_tuyaux = registers[21] / 10.0
            alerte_register = registers[22]
            
            client.close()
            
            # Vérification des alarmes
            self._check_temperature_alarm(temperature_tuyaux, alerte_register)
            self._check_pression_alarm(pression)
            self._check_niveau_alarm(niveau_cuve1, niveau_cuve2, niveau_cuve3)
            self._check_temperature_ambiante_alarm(temperature)
            
        except Exception as e:
            self.logger.error(f"Erreur générale: {e}")
    
    def _check_temperature_alarm(self, temp_tuyaux, alerte_register):
        """Vérifie les alarmes de température des tuyaux"""
        alarm_key = "temp_tuyaux"
        
        if alerte_register == 1 and self.last_alerts.get(alarm_key) != "low":
            message = f"❄️ ALARME - Température tuyaux trop basse: {temp_tuyaux}°C"
            self._trigger_alarm(alarm_key, "low", message, "warning")
            
        elif alerte_register == 2 and self.last_alerts.get(alarm_key) != "high":
            message = f"🔥 ALARME - Température tuyaux trop haute: {temp_tuyaux}°C"
            self._trigger_alarm(alarm_key, "high", message, "error")
            
        elif alerte_register == 0 and alarm_key in self.last_alerts:
            self._clear_alarm(alarm_key, "Température tuyaux normale")
    
    def _check_pression_alarm(self, pression):
        """Vérifie les alarmes de pression"""
        alarm_key = "pression"
        
        if pression < 600 and self.last_alerts.get(alarm_key) != "low":
            message = f"📉 ALARME - Pression critique: {pression} kPa"
            self._trigger_alarm(alarm_key, "low", message, "error")
            
        elif pression > 1300 and self.last_alerts.get(alarm_key) != "high":
            message = f"📈 ALARME - Pression dangereuse: {pression} kPa"
            self._trigger_alarm(alarm_key, "high", message, "error")
            
        elif 800 <= pression <= 1100 and alarm_key in self.last_alerts:
            self._clear_alarm(alarm_key, f"Pression normale: {pression} kPa")
    
    def _check_niveau_alarm(self, niveau1, niveau2, niveau3):
        """Vérifie les alarmes de niveau des cuves"""
        for i, niveau in enumerate([niveau1, niveau2, niveau3], 1):
            alarm_key = f"niveau_cuve_{i}"
            
            if niveau < 20 and self.last_alerts.get(alarm_key) != "low":
                message = f"⚠️ ALARME - Cuve {i} niveau critique: {niveau}%"
                self._trigger_alarm(alarm_key, "low", message, "warning")
                
            elif niveau > 90 and self.last_alerts.get(alarm_key) != "high":
                message = f"⚠️ ALARME - Cuve {i} niveau trop haut: {niveau}%"
                self._trigger_alarm(alarm_key, "high", message, "warning")
                
            elif 30 <= niveau <= 80 and alarm_key in self.last_alerts:
                self._clear_alarm(alarm_key, f"Cuve {i} niveau normal: {niveau}%")
    
    def _check_temperature_ambiante_alarm(self, temperature):
        """Vérifie les alarmes de température ambiante"""
        alarm_key = "temp_ambiante"
        
        if temperature < 5 and self.last_alerts.get(alarm_key) != "low":
            message = f"❄️ ALARME - Température ambiante basse: {temperature}°C"
            self._trigger_alarm(alarm_key, "low", message, "warning")
            
        elif temperature > 35 and self.last_alerts.get(alarm_key) != "high":
            message = f"🔥 ALARME - Température ambiante haute: {temperature}°C"
            self._trigger_alarm(alarm_key, "high", message, "warning")
            
        elif 10 <= temperature <= 30 and alarm_key in self.last_alerts:
            self._clear_alarm(alarm_key, f"Température ambiante normale: {temperature}°C")
    
    def _trigger_alarm(self, alarm_key, alarm_type, message, severity="warning"):
        """Déclenche une alarme"""
        self.last_alerts[alarm_key] = alarm_type
        self.logger.warning(f"ALARME: {message}")
        
        # Affichage popup (optionnel)
        try:
            if severity == "error":
                messagebox.showerror("ALARME SYSTÈME", message)
            else:
                messagebox.showwarning("ALERTE SYSTÈME", message)
        except:
            pass  # Si pas d'interface graphique disponible
    
    def _clear_alarm(self, alarm_key, message):
        """Efface une alarme"""
        del self.last_alerts[alarm_key]
        self.logger.info(f"ALARME RESOLUE: {message}")
    
    def start_monitoring(self, interval=3):
        """Démarre la surveillance continue"""
        self.logger.info(f"🚨 Gestionnaire d'alarmes démarré (vérification toutes les {interval}s)")
        
        try:
            while True:
                self.check_alarms()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("🛑 Gestionnaire d'alarmes arrêté")
        except Exception as e:
            self.logger.error(f"💥 Erreur critique: {e}")

if __name__ == "__main__":
    alarm_manager = AlarmManager()
    alarm_manager.start_monitoring(interval=3)  # Vérification toutes les 3 secondes