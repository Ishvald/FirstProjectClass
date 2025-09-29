"""création des boutons pour activer une vanne appeller Vanne-Ville"""
"""création d'une interface homme machine pour le client"""

import tkinter as tk
from pymodbus.client import ModbusTcpClient

def activer_vanne():
    client = ModbusTcpClient('127.0.0.1', port=502)
    client.connect()
    client.write_register(address=0, value=1)  # 1 = vanne ouverte
    client.close()
    status_label.config(text="Vanne activée !")


# filepath: [chaufferie_client.py](http://_vscodecontentref_/1)
# ...existing code...
root = tk.Tk()
root.title("IHM Vanne-Ville")
root.geometry("400x200")  # Largeur x Hauteur
# ...existing code...
root.title("IHM Vanne-Ville")

btn = tk.Button(root, text="Activer la vanne", command=activer_vanne)
btn.pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()

