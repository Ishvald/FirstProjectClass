"""création des boutons pour activer une vanne appeller Vanne-Ville"""
"""création d'une interface homme machine pour le client"""

import tkinter as tk
from pymodbus.client import ModbusTcpClient

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

"""création d'un bouton pour activer la vanne"""
btn = tk.Button(root, text="Activer la vanne", command=activer_vanne)
btn.pack(pady=10)
""" et un bouton pour désactiver la vanne"""
btn_desactiver = tk.Button(root, text="Désactiver la vanne", command=desactiver_vanne)
btn_desactiver.pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

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
canvas_level_text = canvas.create_text(1050, 110, text="Niveau Cuve 1: --.- %", font=("Arial", 16), fill="black")

# Met à jour les valeurs toutes les secondes
def update_values():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    rr = client.read_holding_registers(address=0, count=3)
    if rr.isError():
        label_temp.config(text="Température: --.- °C")
        label_press.config(text="Pression: --.- kPa")
        label_level.config(text="Niveau: --.- %")
        # Met à jour aussi sur le canvas
        canvas.itemconfig(canvas_press_text, text="Pression: --.- kPa")
        canvas.itemconfig(canvas_temp_text, text="Température: --.- °C")
        canvas.itemconfig(canvas_level_text, text="Niveau Cuve 1: --.- %")
    else:
        pression = rr.registers[0] / 10.0
        temperature = rr.registers[1] / 10.0
        niveau = rr.registers[2] / 10.0
        label_press.config(text=f"Pression: {pression:.1f} kPa")
        label_temp.config(text=f"Température: {temperature:.1f} °C")
        label_level.config(text=f"Niveau: {niveau:.1f} %")
        # Met à jour aussi sur le canvas
        canvas.itemconfig(canvas_press_text, text=f"Pression: {pression:.1f} kPa")
        canvas.itemconfig(canvas_temp_text, text=f"Température: {temperature:.1f} °C")
        canvas.itemconfig(canvas_level_text, text=f"Niveau Cuve 1: {niveau:.1f} %")
    client.close()
    root.after(1000, update_values)


update_values()  # Lancer la mise à jour des valeurs
root.mainloop()


