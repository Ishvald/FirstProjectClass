import tkinter as tk
from pymodbus.client import ModbusTcpClient
import time
from threading import Thread

class AlarmeTemperature:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Système d'Alarme - Température Tuyaux")
        self.root.geometry("400x200")
        self.root.configure(bg='black')
        
        # Label principal d'alarme
        self.alarme_label = tk.Label(
            self.root, 
            text="SURVEILLANCE TEMPÉRATURE TUYAUX", 
            font=("Arial", 16, "bold"), 
            bg='black', 
            fg='white'
        )
        self.alarme_label.pack(pady=20)
        
        # Label de statut
        self.status_label = tk.Label(
            self.root, 
            text="Température: --.- °C", 
            font=("Arial", 14), 
            bg='black', 
            fg='green'
        )
        self.status_label.pack(pady=10)
        
        # Label d'alerte
        self.alert_label = tk.Label(
            self.root, 
            text="NIVEAU NORMAL", 
            font=("Arial", 18, "bold"), 
            bg='black', 
            fg='green'
        )
        self.alert_label.pack(pady=20)
        
        # Démarrer la surveillance
        self.surveillance_active = True
        self.thread_surveillance = Thread(target=self.surveiller_temperature, daemon=True)
        self.thread_surveillance.start()
        
    def declencher_alarme(self, message, couleur):
        """Déclenche une alarme visuelle"""
        self.alert_label.config(text=message, fg=couleur)
        self.root.configure(bg='red')
        self.alarme_label.config(bg='red')
        self.status_label.config(bg='red')
        self.alert_label.config(bg='red')
        
        # Faire clignoter la fenêtre
        self.root.after(500, self.restaurer_couleurs)
        
    def restaurer_couleurs(self):
        """Restaure les couleurs normales"""
        if "NORMAL" in self.alert_label.cget('text'):
            self.root.configure(bg='black')
            self.alarme_label.config(bg='black')
            self.status_label.config(bg='black')
            self.alert_label.config(bg='black')
        else:
            # Si l'alarme est toujours active, continuer le clignotement
            self.root.after(500, lambda: self.declencher_alarme(
                self.alert_label.cget('text'), 
                self.alert_label.cget('fg')
            ))
    
    def normaliser(self):
        """Remet l'interface en état normal"""
        self.alert_label.config(text="NIVEAU NORMAL", fg='green')
        self.root.configure(bg='black')
        self.alarme_label.config(bg='black')
        self.status_label.config(bg='black')
        self.alert_label.config(bg='black')
    
    def surveiller_temperature(self):
        """Surveille en continu la température des tuyaux"""
        while self.surveillance_active:
            try:
                client = ModbusTcpClient('127.0.0.1', port=502)
                client.connect()
                
                # Lire la température des tuyaux (adresse 21)
                rr = client.read_holding_registers(address=21, count=1)
                
                if not rr.isError():
                    temperature_tuyaux = rr.registers[0] / 10.0
                    
                    # Mettre à jour l'interface
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Température: {temperature_tuyaux:.1f} °C"
                    ))
                    
                    # Vérifier les seuils d'alarme
                    if temperature_tuyaux > 80:
                        self.root.after(0, lambda: self.declencher_alarme(
                            "ALARME: TEMPÉRATURE TROP ÉLEVÉE!", 
                            'red'
                        ))
                    elif temperature_tuyaux < 40:
                        self.root.after(0, lambda: self.declencher_alarme(
                            "ALARME: TEMPÉRATURE TROP BASSE!", 
                            'blue'
                        ))
                    else:
                        self.root.after(0, self.normaliser)
                
                client.close()
                
            except Exception as e:
                print(f"Erreur de connexion: {e}")
                self.root.after(0, lambda: self.status_label.config(
                    text="Erreur de connexion au serveur"
                ))
            
            time.sleep(1)  # Vérifier toutes les secondes
    
    def demarrer(self):
        """Démarre l'interface d'alarme"""
        self.root.mainloop()
    
    def arreter(self):
        """Arrête la surveillance"""
        self.surveillance_active = False
        self.root.quit()

if __name__ == "__main__":
    alarme = AlarmeTemperature()
    
    # Gérer la fermeture propre de l'application
    alarme.root.protocol("WM_DELETE_WINDOW", alarme.arreter)
    
    try:
        alarme.demarrer()
    except KeyboardInterrupt:
        alarme.arreter()


