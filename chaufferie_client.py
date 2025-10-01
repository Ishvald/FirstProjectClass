"""création des boutons pour activer une vanne appeller Vanne-Ville"""
"""création d'une interface homme machine pour le client"""

import tkinter as tk
from pymodbus.client import ModbusTcpClient
from tkinter import messagebox

def activer_vanne():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=10, value=1)  # 1 = vanne ouverte
    client.close()
    status_label.config(text="Vanne activée !")

def desactiver_vanne():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=10, value=0)  # 0 = vanne fermée
    client.close()
    status_label.config(text="Vanne désactivée !")


def update_values():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    # Lire pression (adresse 0), température (1), niveau cuve 1 (2)
    rr = client.read_holding_registers(address=0, count=3)
    if rr.isError():
        label_temp.config(text="Température: --.- °C")
        label_press.config(text="Pression: --.- Pa")
        label_level.config(text="Niveau: --.- %")
    else:
        pression = rr.registers[0] / 10.0
        temperature = rr.registers[1] / 10.0
        niveau = rr.registers[2] / 10.0
        label_press.config(text=f"Pression: {pression:.1f} kPa")
        label_temp.config(text=f"Température: {temperature:.1f} °C")
        label_level.config(text=f"Niveau: {niveau:.1f} %")
    client.close()
    root.after(1000, update_values)  # Relance la fonction toutes les secondes



# Création de la fenêtre principale
root = tk.Tk()
root.title("IHM Vanne-Ville")
root.geometry("1200x1000")  # Largeur x Hauteur

"""création d'un bouton qui change de couleur pour activer/désactiver la vanne placer en haut de la fenêtre à gauche"""
activate_button = tk.Button(root, text="Activer Vanne-Ville", command=activer_vanne, bg="green", fg="white", font=("Arial", 16))
activate_button.pack(pady=10)
deactivate_button = tk.Button(root, text="Désactiver Vanne-Ville", command=desactiver_vanne, bg="red", fg="white", font=("Arial", 16))
deactivate_button.pack(pady=10)
status_label = tk.Label(root, text="Statut: Inconnu", font=("Arial", 14))
status_label.pack(pady=10)




"""4 boutons pour simuler les saisons si en hiver alors température baisse plus vite, si en été alors température monte plus vite,"""
season_frame = tk.Frame(root)
season_frame.pack(pady=10)
def set_winter():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=20, value=0)  # 0 = hiver
    client.close()

def set_summer():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=20, value=2)  # 2 = été
    client.close()

def set_spring():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=20, value=1)  # 1 = printemps
    client.close()

def set_autumn():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=20, value=3)  # 3 = automne
    client.close()

"""création d'un pop-up qui s'ouvre si la température des tuyaux est trop basse ou trop haute"""
def check_temperature_alert():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    rr = client.read_holding_registers(address=0, count=50)
    if rr.isError():
        pass
    else:
        alerte_temperature = rr.registers[21]
        if alerte_temperature == 1:
            messagebox.showwarning("Alerte", "La température des tuyaux est trop basse!")
        elif alerte_temperature == 2:
            messagebox.showwarning("Alerte", "La température des tuyaux est trop haute!")

    client.close()
    root.after(1000, check_temperature_alert)

winter_button = tk.Button(season_frame, text="Hiver", command=set_winter, bg="lightblue", font=("Arial", 12))
winter_button.grid(row=0, column=0, padx=5) 
summer_button = tk.Button(season_frame, text="Été", command=set_summer, bg="orange", font=("Arial", 12))
summer_button.grid(row=0, column=1, padx=5)
spring_button = tk.Button(season_frame, text="Printemps", command=set_spring, bg="lightgreen", font=("Arial", 12))
spring_button.grid(row=0, column=2, padx=5)
autumn_button = tk.Button(season_frame, text="Automne", command=set_autumn, bg="brown", fg="white", font=("Arial", 12))
autumn_button.grid(row=0, column=3, padx=5)





""" ihm avancée pour afficher le système dans sa globalité avec 3 cuves, des tuyaux, 
une pompe autoregulation et une vanne autoregulation, une vanne ville 
et des capteurs de température"""

# création des cuves et des tuyaux, cuves tout en bas de la fenêtre des tuyaux qui partent en haut
canvas = tk.Canvas(root, width=1200, height=1000, bg="lightblue")
canvas.pack() 
# création des cuves
canvas.create_rectangle(50, 300, 150, 400, fill="grey")  # Cuve 1
canvas.create_text(100, 350, text="Cuve 1") 
canvas.create_rectangle(325, 300, 425, 400, fill="grey")  # Cuve 2
canvas.create_text(375, 350, text="Cuve 2")
canvas.create_rectangle(600, 300, 700, 400, fill="grey")  # Cuve 3
canvas.create_text(650, 350, text="Cuve 3")
# création des tuyaux
canvas.create_rectangle(90, 20, 110, 300, fill="brown")  # Tuyau Cuve 1
canvas.create_rectangle(365, 20, 385, 300, fill="brown")  # Tuyau Cuve 2
canvas.create_rectangle(640, 20, 660, 300, fill="brown")  # Tuyau Cuve 3
#tuyau horizontal en haut pour relier les 3 tuyaux verticaux
canvas.create_rectangle(110, 20, 900, 40, fill="brown")  # Tuyau horizontal
canvas.create_rectangle(890, 20, 910, 300, fill="brown")#tuyau vertical en fin de tuyau horizontal
#tuyau horizontal bleu pour représenter l'eau qui rerentre dans les cuves a la fin du tuyau vertical
canvas.create_rectangle(110, 280, 890, 300, fill="blue")  # Tuyau horizontal eau
#trois barre vertes verticales pour représenter un lien entre le bleu et les cuves
canvas.create_rectangle(110, 280, 125, 310, fill="green")  # lien eau cuve 1
canvas.create_rectangle(385, 280, 400, 310, fill="green")  # lien eau cuve 2
canvas.create_rectangle(660, 280, 675, 310, fill="green")  # lien eau cuve 3

# création de la pompe autoregulation placer au milieu du tuyau horizontal
canvas.create_oval(750, 10, 850, 50, fill="red")  # Pompe
canvas.create_text(800, 30, text="Pompe autoregulation", fill="white")  # Lettre P pour Pompe


# création de la vanne autoregulation sur la ligne bleue
canvas.create_rectangle(750, 280, 770, 300, fill="orange")  # Vanne autoregulation
canvas.create_text(760, 290, text="VA", fill="white")  # Lettre VA pour Vanne Autoregulation

#en plein milieu du tuyau vertical le plus a droite, faire un tuyau horizontal vers laa droite
canvas.create_rectangle(910, 150, 1100, 170, fill="brown")  # Tuyau horizontal droite

# création de la vanne ville sur le tuyau horizontal a droite
canvas.create_rectangle(1000, 150, 1020, 170, fill="yellow")  # Vanne ville
canvas.create_text(1010, 160, text="VV", fill="black")  # Lettre VV pour Vanne Ville



# Labels pour afficher les valeurs
label_press = tk.Label(root, text="Pression: --.- kPa", font=("Arial", 16))
label_press.pack(pady=10)
label_temp = tk.Label(root, text="Température: --.- °C", font=("Arial", 16))
label_temp.pack(pady=10)
label_level = tk.Label(root, text="Niveau: --.- %", font=("Arial", 16))
label_level.pack(pady=10)

# Texte sur le canvas pour afficher les valeurs
canvas_press_text = canvas.create_text(1050, 50, text="Pression: --.- kPa", font=("Arial", 16), fill="black")
canvas_temp_text = canvas.create_text(1050, 80, text="Température: --.- °C", font=("Arial", 16), fill="black")
canvas_level_text = canvas.create_text(120, 420, text="Niveau Cuve 1: --.- %", font=("Arial", 16), fill="black")
canvas_level_text2 = canvas.create_text(395, 420, text="Niveau Cuve 2: --.- %", font=("Arial", 16), fill="black")
canvas_level_text3 = canvas.create_text(670, 420, text="Niveau Cuve 3: --.- %", font=("Arial", 16), fill="black")

"""label qui écrit dans quelle saison on est en rcupérant la valeur dans le registre 20"""
canvas_saison_text = canvas.create_text(1050, 110, text="Saison: --", font=("Arial", 16), fill="black")
"""afficher la température des tuyaux"""
canvas_temp_tuyaux_text = canvas.create_text(1050, 140, text="Température Tuyaux: --.- °C", font=("Arial", 16), fill="black")




# Met à jour les valeurs toutes les secondes
def update_values():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    rr = client.read_holding_registers(address=0, count=50)
    if rr.isError():
        label_temp.config(text="Température: --.- °C")
        label_press.config(text="Pression: --.- kPa")
        label_level.config(text="Niveau: --.- %")
        # Met à jour aussi sur le canvas
        canvas.itemconfig(canvas_press_text, text="Pression: --.- kPa")
        canvas.itemconfig(canvas_temp_text, text="Température: --.- °C")
        canvas.itemconfig(canvas_level_text, text="Niveau Cuve 1: --.- %")
        canvas.itemconfig(canvas_level_text, text="Niveau Cuve 2: --.- %")
        canvas.itemconfig(canvas_level_text, text="Niveau Cuve 3: --.- %")
        canvas.itemconfig(canvas_saison_text, text="Saison: --")

    else:
        pression = rr.registers[0] / 10.0
        temperature = rr.registers[1] / 10.0
        niveau_cuve1 = rr.registers[2] / 10.0
        niveau_cuve2 = rr.registers[3] / 10.0
        niveau_cuve3 = rr.registers[4] / 10.0
        saison_val = rr.registers[20]
        temperature_tuyaux = rr.registers[21] / 10.0
        

        # Affichage saison
        if saison_val == 0:
            saison_txt = "Hiver"
        elif saison_val == 1:
            saison_txt = "Printemps"
        elif saison_val == 2:
            saison_txt = "Été"
        elif saison_val == 3:
            saison_txt = "Automne"
        else:
            saison_txt = "--"


        label_press.config(text=f"Pression: {pression:.1f} kPa")
        label_temp.config(text=f"Température: {temperature:.1f} °C")
        label_level.config(text=f"Niveau: {niveau_cuve1:.1f} %")
        label_level.config(text=f"Niveau: {niveau_cuve2:.1f} %")
        label_level.config(text=f"Niveau: {niveau_cuve3:.1f} %")

        # Met à jour aussi sur le canvas
        canvas.itemconfig(canvas_press_text, text=f"Pression: {pression:.1f} kPa")
        canvas.itemconfig(canvas_temp_text, text=f"Température: {temperature:.1f} °C")
        canvas.itemconfig(canvas_level_text, text=f"Niveau Cuve 1: {niveau_cuve1:.1f} %")
        canvas.itemconfig(canvas_level_text2, text=f"Niveau Cuve 2: {niveau_cuve2:.1f} %")
        canvas.itemconfig(canvas_level_text3, text=f"Niveau Cuve 3: {niveau_cuve3:.1f} %")
        canvas.itemconfig(canvas_saison_text, text=f"Saison: {saison_txt}")
        canvas.itemconfig(canvas_temp_tuyaux_text, text=f"Température Tuyaux: {temperature_tuyaux:.1f} °C")

    client.close()
    root.after(1000, update_values)









check_temperature_alert()  # Lancer la vérification des alertes
update_values()  # Lancer la mise à jour des valeurs
root.mainloop()


