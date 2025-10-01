Projet Chaufferie
User Stories
Gestion de la Pression
En tant qu’opérateur, je veux surveiller la pression générale du circuit afin d’assurer la sécurité du système.


En tant qu’opérateur, je veux que la pompe d’autorégulation démarre automatiquement si la pression descend en dessous du seuil, afin de rétablir la stabilité du réseau.


En tant qu’opérateur, je veux que la vanne d’autorégulation s’ouvre automatiquement si la pression devient trop élevée, afin d’éviter les surpressions.


En tant qu’opérateur, je veux recevoir une alerte visuelle/sonore si la pression sort de la plage normale (900 à 1000 kPa).


Gestion de la Température
En tant qu’opérateur, je veux visualiser la température interne du système pour surveiller son bon fonctionnement.


En tant qu’opérateur, je veux distinguer la température externe (impactée par les saisons) et la température interne (dans les tuyaux) afin de comprendre l’origine des variations.


En tant qu’opérateur, je veux recevoir une alerte si la température des tuyaux est trop basse (< 50 °C) ou trop haute (> 70 °C).


En tant qu’opérateur, je veux que le chauffage s’active automatiquement si la température descend sous un seuil critique.


En tant qu’opérateur, je veux que le recyclage de l’eau s’active automatiquement si la température devient trop élevée, afin de protéger les équipements.


Gestion du Niveau d’Eau dans les 3 Cuves
En tant qu’opérateur, je veux connaître en temps réel le niveau d’eau de chaque cuve.


En tant qu’opérateur, je veux être notifié si le niveau d’une cuve descend trop bas (< 10 %) ou monte trop haut (> 90 %).


En tant qu’opérateur, je veux que les niveaux d’eau se rééquilibrent automatiquement lors du recyclage afin d’éviter les déséquilibres.


En tant qu’opérateur, je veux visualiser graphiquement l’évolution du niveau des cuves pour mieux anticiper les besoins.


Gestion des Saisons
En tant qu’opérateur, je veux pouvoir choisir la saison (hiver, printemps, été, automne) afin de simuler des conditions réelles de fonctionnement.


En tant qu’opérateur, je veux que le système change automatiquement de saison toutes les 30 secondes pour observer l’évolution des températures.


En tant qu’opérateur, je veux visualiser en temps réel dans quelle saison le système se trouve.


Gestion des Vannes et de la Pompe
En tant qu’opérateur, je veux pouvoir ouvrir/fermer la vanne de ville depuis l’IHM afin de contrôler l’arrivée d’eau extérieure.


En tant qu’opérateur, je veux voir l’état de la vanne d’autorégulation (ouverte/fermée).


En tant qu’opérateur, je veux voir l’état de la pompe d’autorégulation (ON/OFF).


Interface Homme-Machine (IHM)
En tant qu’opérateur, je veux une interface graphique simple qui me montre l’ensemble du système (cuves, tuyaux, pompe, vannes) pour une vision globale.


En tant qu’opérateur, je veux que les valeurs de pression, température et niveaux soient affichées directement sur le schéma afin d’éviter de multiplier les écrans.


En tant qu’opérateur, je veux que des alertes (pop-up) apparaissent automatiquement en cas de problème critique (pression trop haute/basse, température anormale, niveau d’eau dangereux).


En tant qu’opérateur, je veux pouvoir interagir avec des boutons pour commander les saisons, la vanne de ville et visualiser les changements en temps réel.



Fonctionnalités Clés
Surveillance en temps réel : Pression, température, niveaux d’eau, état des vannes/pompe.


Régulation automatique : Activation/désactivation automatique de la pompe et de la vanne selon les conditions.


Alertes et notifications : Pop-up de sécurité (pression/ température / niveau).


Simulation avancée : Gestion dynamique des saisons et des variations liées.


IHM graphique : Représentation visuelle des cuves, tuyaux, vannes et pompe.



Principe de Fonctionnement
Le système est composé de 3 cuves d’eau, reliées à une pompe d’autorégulation et une vanne d’autorégulation qui stabilisent la pression.


Une vanne de ville permet d’ouvrir ou fermer l’alimentation extérieure.


La pression chute naturellement ou à cause des vannes, et se rétablit avec la pompe.


La température évolue selon les saisons, et des mécanismes automatiques (chauffage/recyclage) maintiennent l’équilibre.


Les niveaux d’eau fluctuent en fonction de la consommation/recyclage et doivent rester dans une plage de sécurité.


L’IHM permet de visualiser l’ensemble, commander les vannes, changer la saison et recevoir les alertes en direct.

