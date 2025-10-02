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

## 🎯 Scénarios d'Utilisation

### 🔄 Scénario 1: Régulation Automatique de Pression

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

### 🌡️ Scénario 2: Gestion des Saisons et Température

**Cycle Automatique:**
- **Hiver (0):** Température baisse rapidement (-0.8°C à -0.2°C/seconde)
- **Printemps (1):** Variations modérées (-0.2°C à +0.7°C/seconde)  
- **Été (2):** Température monte rapidement (+0.2°C à +0.8°C/seconde)
- **Automne (3):** Refroidissement progressif (-0.6°C à +0.1°C/seconde)

**Intervention Manuel:**
- L'opérateur peut forcer une saison via les boutons dédiés
- Le compteur de saison se réinitialise
- La simulation adapte immédiatement le comportement thermique

### 🚨 Scénario 3: Alerte Température Critique

**Conditions de Déclenchement:**
- **Alarme BASSE:** Température tuyaux < 50°C → Fenêtre bleue
- **Alarme HAUTE:** Température tuyaux > 70°C → Fenêtre rouge

**Séquence d'Alarme:**
1. Le système d'alarme détecte le dépassement de seuil
2. Une fenêtre d'alerte colorée s'affiche immédiatement
3. Le message indique la température actuelle et le seuil dépassé
4. L'alerte persiste jusqu'à intervention manuelle
5. Si la température revient à la normale, l'affichage devient vert mais reste visible

### 💧 Scénario 4: Gestion des Niveaux de Cuves

**Remplissage Manuel:**
- Les cuves se vident progressivement quand la pompe fonctionne
- L'opérateur peut cliquer sur "Remplir Cuves" pour les remettre à 50%
- Action immédiate via coil Modbus (adresse 1)

**Consommation Automatique:**
- Chaque activation de la pompe réduit tous les niveaux de 10%
- Sécurité: niveaux ne descendent jamais en dessous de 10%

### 🔥 Scénario 5: Chauffage Manuel des Tuyaux

**Problème:** Température des tuyaux trop basse en hiver
**Solution:**
1. L'opérateur active le chauffage manuel via l'IHM
2. La température des tuyaux augmente de +0.5°C/seconde
3. Arrêt manuel nécessaire pour éviter la surchauffe

## 🔄 Boucles de Régulation

### Boucle de Pression
```
Vanne Ville Ouverte → Pression baisse → Pompe s'allume → Pression monte → Pompe s'éteint
```

### Boucle de Température Saisonnière
```
Saison → Variation température → Adaptation comportement système → Changement saison automatique
```

### Boucle de Refroidissement Tuyaux
```
Pompe Active → Eau circule → Température tuyaux baisse → Équilibre avec température ambiante
```

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

## 🔧 Procédures Opérationnelles

### Démarrage du Système
1. ✅ Lancer `server.py` - Initialise la simulation
2. ✅ Lancer `alarmes.py` - Active la surveillance
3. ✅ Lancer `client.py` - Ouvre le poste de contrôle

### Arrêt d'Urgence
- Fermer la vanne ville
- Couper le chauffage
- Arrêter les programmes dans l'ordre inverse

### Maintenance Préventive
- Vérifier régulièrement les niveaux des cuves
- Surveiller l'évolution saisonnière
- Tester régulièrement le système d'alarme

---

Ce système reproduit fidèlement les défis opérationnels d'un réseau de distribution d'eau, avec ses boucles de régulation automatique et la nécessité d'une supervision humaine pour les situations exceptionnelles.
