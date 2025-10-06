# Système de Gestion d'Aqueduc Modbus

## 🏗️ Architecture Globale du Système

Ce projet simule un **système complet de distribution d'eau** avec régulation automatique et supervision humaine. L'architecture repose sur trois composants interconnectés qui communiquent via le protocole Modbus TCP :

```
┌─────────────────┐    Modbus TCP    ┌──────────────────┐
│   Interface     │ ←──────────────→ │    Serveur de    │
│    Client       │     Port 502     │   Simulation     │
│   (Contrôle)    │ ←──────────────→ │   (Données)      │
└─────────────────┘                  └──────────────────┘
         ↑                                    ↑
         │                                    │
         └───────────┐              ┌─────────┘
                     │    Lecture   │
               ┌─────────────┐      │
               │  Système    │ ─────┘
               │ d'Alarmes   │
               │ (Surveillance)│
               └─────────────┘
```

## 📋 Prérequis Système

- **Python 3.8+** (testé avec 3.8, 3.9, 3.10)
- **Modules requis** :
  - pymodbus >= 3.0.0
  - tkinter (inclus avec Python généralement)
- **Ports réseau** : Port 502 doit être disponible
- **Système d'exploitation** : Windows, Linux, macOS

## 📦 Installation

```bash
# Méthode avec uv (recommandée)
uv add pymodbus

# Méthode avec pip
pip install pymodbus

# Vérification de l'installation
python -c "from pymodbus.client import ModbusTcpClient; print('Modbus OK')"
```

## 📁 Structure du Projet

```
projet-aqueduc/
├── server.py          # Serveur Modbus principal
├── client.py          # Interface graphique
├── alarmes.py         # Système de surveillance
└── README.md          # Documentation
```

## 🚀 Démarrage du Système

### Méthode recommandée (Terminal/CMD) :
```bash
# Terminal 1 - Démarrer le serveur
uv run server.py

# Terminal 2 - Démarrer le système d'alarme  
uv run alarmes.py

# Terminal 3 - Démarrer l'interface client
python client.py
```

### Méthode alternative (VS Code) :
Vous pouvez également lancer les programmes directement dans VS Code :

1. **Serveur** : Ouvrir `server.py` et exécuter avec `uv run server.py` dans le terminal intégré
2. **Alarmes** : Ouvrir `alarmes.py` et exécuter avec `uv run alarmes.py` dans un nouveau terminal
3. **Client** : Ouvrir `client.py` et exécuter normalement avec le bouton "Run" ou `python client.py`

### 📝 Note importante sur `uv run` :
**Oui, cela fait une différence !** Voici pourquoi :

- `uv run` garantit que les dépendances sont résolues correctement via le gestionnaire de paquets `uv`
- Il utilise l'environnement virtuel approprié automatiquement
- Sans `uv run`, vous pourriez avoir des erreurs d'import si les paquets ne sont pas dans le PYTHONPATH
- Pour le client, `python client.py` fonctionne car il n'a pas de dépendances externes critiques

## 🎯 Scénarios d'Utilisation

### 6.4.2.1 Scénario 1: Régulation Automatique de Pression

**Situation Initiale:**
- Pression normale (100.0 kPa)
- Vanne ville fermée
- Pompe éteinte

**Déroulement:**
1. L'utilisateur ouvre la vanne ville via l'IHM
2. La pression commence à baisser progressivement
3. Quand la pression passe sous 80.0 kPa, le système active automatiquement la pompe
4. La pompe remonte la pression jusqu'à 90.0-100.0 kPa
5. Une fois la pression stabilisée, la pompe s'éteint automatiquement

**Résultat:** Maintien automatique de la pression dans la plage optimale.

### 6.4.2.1 Scénario 2: Gestion des Saisons et Température

**Cycle Automatique:**
- **Hiver (0):** Température baisse rapidement (-0.8°C à -0.2°C/seconde)
- **Printemps (1):** Variations modérées (-0.2°C à +0.7°C/seconde)  
- **Été (2):** Température monte rapidement (+0.2°C à +0.8°C/seconde)
- **Automne (3):** Refroidissement progressif (-0.6°C à +0.1°C/seconde)

**Utilité des Saisons:**
Le système des saisons garantit que **la température des tuyaux ne descend jamais en dessous de la température ambiante**. Cette fonctionnalité cruciale prévient :
- La condensation excessive sur les conduites
- Les chocs thermiques dans le réseau
- Le gel des canalisations en hiver
- Les variations brutales de température

**Intervention Manuel:**
- L'opérateur peut forcer une saison via les boutons dédiés
- Le compteur de saison se réinitialise
- La simulation adapte immédiatement le comportement thermique

### 6.4.2.1 Scénario 3: Alerte Température Critique

**Conditions de Déclenchement:**
- **Alarme BASSE:** Température tuyaux < 50°C → Fenêtre bleue
- **Alarme HAUTE:** Température tuyaux > 70°C → Fenêtre rouge

**Séquence d'Alarme:**
1. Le système d'alarme détecte le dépassement de seuil
2. Une fenêtre d'alerte colorée s'affiche immédiatement
3. Le message indique la température actuelle et le seuil dépassé
4. L'alerte persiste jusqu'à intervention manuelle
5. Si la température revient à la normale, l'affichage devient vert mais reste visible

### 6.4.2.1 Scénario 4: Gestion des Niveaux de Cuves

**Remplissage Manuel:**
- Les cuves se vident progressivement quand la pompe fonctionne
- L'opérateur peut cliquer sur "Remplir Cuves" pour les remettre à 50%
- Action immédiate via coil Modbus (adresse 1)

**Consommation Automatique:**
- Chaque activation de la pompe réduit tous les niveaux de 10%
- Sécurité: niveaux ne descendent jamais en dessous de 10%

### 6.4.2.1 Scénario 5: Chauffage Manuel des Tuyaux

**Problème:** Température des tuyaux trop basse en hiver
**Solution:**
1. L'opérateur active le chauffage manuel via l'IHM
2. La température des tuyaux augmente de +0.5°C/seconde
3. Arrêt manuel nécessaire pour éviter la surchauffe

## 🔧 Détails Techniques Modbus

### Table des Registres (Holding Registers - 4x)
| Adresse | Nom | Description | Plage |
|---------|-----|-------------|-------|
| 0 | Pression | Pression réseau (x10) | 0-2000 |
| 1 | Température | Température ambiante (x10) | 30-400 |
| 2-4 | Niveaux cuves | Niveaux cuves 1-3 (x10) | 100-500 |
| 20 | Saison | 0:Hiver,1:Printemps,2:Été,3:Automne | 0-3 |
| 21 | Température tuyaux | Température conduites (x10) | 0-1000 |

### Table des Coils (0x)
| Adresse | Nom | Description |
|---------|-----|-------------|
| 1 | Remplissage cuves | Remet toutes les cuves à 50% |

## 🎮 Tableau de Contrôle Opérateur

| Élément | Type | Action | Effet |
|---------|------|--------|-------|
| **Vanne Ville** | Interrupteur | Ouverture/Fermeture | Contrôle débit entrée |
| **Chauffage** | Interrupteur | Activation/Désactivation | Chauffe tuyaux |
| **Saisons** | Sélection | Choix manuel | Force conditions météo |
| **Remplissage** | Bouton momentané | Appui unique | Remet cuves à 50% |

## 📊 Métriques de Surveillance

| Paramètre | Plage Normale | Seuil Alarme | Unité |
|-----------|---------------|--------------|-------|
| Pression | 90.0 - 100.0 | < 80.0 | kPa |
| Température ambiante | 3.0 - 40.0 | Aucune | °C |
| Température tuyaux | 50.0 - 70.0 | < 50.0 ou > 70.0 | °C |
| Niveau cuves | 10.0 - 100.0 | < 10.0 | % |

## 🎮 Démonstration Rapide

1. **Lancer les 3 programmes** dans l'ordre
2. **Ouvrir la vanne ville** → Observer la baisse de pression
3. **Attendre** que la pompe s'allume automatiquement
4. **Changer de saison** → Observer l'effet sur la température
5. **Activer le chauffage** → Voir la température des tuyaux augmenter
6. **Remplir les cuves** → Remettre les niveaux à 50%

## 🐛 Dépannage

### Erreur "Address already in use"
- Le port 502 est déjà utilisé
- Solution : Fermer d'autres applications ou redémarrer le serveur

### Erreur "Connection refused"
- Le serveur n'est pas démarré
- Vérifier l'ordre de lancement

### Interface client ne se connecte pas
- Vérifier que le serveur affiche "Serveur Modbus TCP démarré sur le port 502..."

### Alarmes ne se déclenchent pas
- Vérifier que la température des tuyaux dépasse les seuils (50°C / 70°C)
