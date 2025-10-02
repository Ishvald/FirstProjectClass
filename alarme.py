import tkinter as tk
from pymodbus.client import ModbusTcpClient
import time
import threading

class AlarmeFonctionnelle:
    def __init__(self):
        self.surveillance_active = True
        self.fenetre = None
        self.seuil_haut = 80
        self.seuil_bas = 40
        self.root = None
        self.derniere_temperature = 0
        self.label_alarme = None
        
    def creer_fenetre_alarme(self, couleur):
        """Crée une fenêtre d'alarme dans le thread principal"""
        if self.fenetre is not None:
            try:
                self.fenetre.destroy()
            except:
                pass
        
        self.fenetre = tk.Toplevel()
        self.fenetre.title("🚨 ALARME TEMPÉRATURE")
        self.fenetre.geometry("500x200")
        self.fenetre.configure(bg=couleur)
        self.fenetre.attributes('-topmost', True)
        
        # Message d'alarme avec température actualisée
        self.label_alarme = tk.Label(
            self.fenetre,
            text="",  # Le texte sera mis à jour
            font=("Arial", 16, "bold"),
            bg=couleur,
            fg='white',
            wraplength=450
        )
        self.label_alarme.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Gérer la fermeture
        self.fenetre.protocol("WM_DELETE_WINDOW", self.fermer_alarme)
        
        print("🚨 Fenêtre d'alarme créée")
        
        # Démarrer la mise à jour de l'affichage
        self.actualiser_affichage_alarme(couleur)
    
    def actualiser_affichage_alarme(self, couleur):
        """Actualise l'affichage de l'alarme avec la température actuelle"""
        if self.fenetre and self.label_alarme:
            if self.derniere_temperature > self.seuil_haut:
                message = f"🚨 TEMPÉRATURE TROP ÉLEVÉE !\n{self.derniere_temperature:.1f}°C > {self.seuil_haut}°C"
            elif self.derniere_temperature < self.seuil_bas:
                message = f"🚨 TEMPÉRATURE TROP BASSE !\n{self.derniere_temperature:.1f}°C < {self.seuil_bas}°C"
            else:
                message = f"✅ TEMPÉRATURE NORMALE\n{self.derniere_temperature:.1f}°C"
                # Si retour à la normale, on pourrait fermer l'alarme automatiquement
                # Mais vous voulez qu'elle reste ouverte jusqu'à fermeture manuelle
            
            self.label_alarme.config(text=message)
            
            # Vérifier si on doit changer la couleur
            if self.derniere_temperature > self.seuil_haut and couleur != 'red':
                self.fenetre.configure(bg='red')
                self.label_alarme.configure(bg='red')
            elif self.derniere_temperature < self.seuil_bas and couleur != 'blue':
                self.fenetre.configure(bg='blue')
                self.label_alarme.configure(bg='blue')
            elif self.seuil_bas <= self.derniere_temperature <= self.seuil_haut and couleur != 'green':
                self.fenetre.configure(bg='green')
                self.label_alarme.configure(bg='green')
            
            # Continuer à actualiser toutes les secondes si la fenêtre existe
            if self.fenetre:
                self.fenetre.after(1000, lambda: self.actualiser_affichage_alarme(
                    'red' if self.derniere_temperature > self.seuil_haut else 
                    'blue' if self.derniere_temperature < self.seuil_bas else 
                    'green'
                ))
    
    def fermer_alarme(self):
        """Ferme l'alarme seulement si on appuie sur la croix"""
        if self.fenetre:
            self.fenetre.destroy()
            self.fenetre = None
            self.label_alarme = None
            print("✅ Alarme fermée par l'utilisateur")
    
    def surveiller_temperature(self):
        """Surveille la température et affiche l'alarme si nécessaire"""
        while self.surveillance_active:
            try:
                client = ModbusTcpClient('127.0.0.1', port=502)
                client.connect()
                
                # Lire la température des tuyaux (adresse 21)
                rr = client.read_holding_registers(address=21, count=1)
                
                if not rr.isError():
                    temperature = rr.registers[0] / 10.0
                    self.derniere_temperature = temperature
                    
                    print(f"📊 Température actuelle: {temperature:.1f}°C")
                    
                    # Vérifier les seuils
                    if temperature > self.seuil_haut:
                        if self.fenetre is None:  # Only create if not already open
                            # Programmer la création dans le thread principal
                            self.root.after(0, lambda: self.creer_fenetre_alarme('red'))
                        # Si fenêtre existe déjà, l'actualisation se fera automatiquement
                    
                    elif temperature < self.seuil_bas:
                        if self.fenetre is None:  # Only create if not already open
                            self.root.after(0, lambda: self.creer_fenetre_alarme('blue'))
                    
                    # Si retour à la normale mais fenêtre ouverte, on la laisse ouverte
                    # mais on change l'affichage pour indiquer que c'est revenu à la normale
                    elif self.fenetre is not None and self.seuil_bas <= temperature <= self.seuil_haut:
                        print("✅ Température revenue à la normale (fenêtre maintenue)")
                        # L'affichage sera actualisé automatiquement
                
                client.close()
                
            except Exception as e:
                print(f"❌ Erreur connexion: {e}")
                time.sleep(5)
            
            time.sleep(2)  # Vérifier toutes les 2 secondes
    
    def demarrer(self):
        """Démarre la surveillance avec une fenêtre Tkinter principale cachée"""
        # Créer la fenêtre principale cachée
        self.root = tk.Tk()
        self.root.withdraw()  # Cacher la fenêtre principale
        self.root.title("Alarme Température")
        
        print("🔍 Surveillance température démarrée...")
        print(f"📊 Seuils: < {self.seuil_bas}°C | > {self.seuil_haut}°C")
        print("💤 En attente de dépassement...")
        
        # Démarrer la surveillance dans un thread séparé
        thread = threading.Thread(target=self.surveiller_temperature, daemon=True)
        thread.start()
        
        # Lancer le mainloop de Tkinter
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.arreter()
    
    def arreter(self):
        """Arrête la surveillance"""
        self.surveillance_active = False
        if self.root:
            self.root.quit()
        print("🛑 Surveillance arrêtée")

if __name__ == "__main__":
    alarme = AlarmeFonctionnelle()
    alarme.demarrer()
    