# DiabetoWeb : Une application pour l'aide au diagnostic du diabète

DiabetoWeb est une solution web innovante développée pour la startup marocaine spécialisée dans le domaine de la santé. Ce projet a pour objectif d'offrir aux médecins une application web sécurisée et intuitive pour la gestion des patients et l'aide au diagnostic du diabète, en tirant parti d'un modèle de machine learning.

**Table des Matière**
- Contexte du Projet
- Fonctionnalités
- Technologies Utilisées
- Installation et Démarrage
- Structure du Projet
- Déploiement

**Auteur**
Ibtissam SANNAKY

**Contexte du Projet**

Dans le cadre de l'innovation en santé, DiabetoWeb vise à moderniser la gestion des dossiers médicaux. L'application permet aux professionnels de santé de centraliser les informations des patients, de saisir leurs données cliniques, et de bénéficier d'un outil d'aide à la décision qui utilise l'intelligence artificielle pour prédire le risque de diabète. L'objectif final est de renforcer l'efficacité des soins et de faciliter le dépistage précoce.

**Fonctionnalités**

L'application a été développée autour des besoins des médecins, avec les fonctionnalités principales suivantes :

**Authentification Sécurisée :** Les médecins peuvent créer un compte et se connecter à une interface personnelle, garantissant la confidentialité des données.

**Gestion des Patients :** Un formulaire dédié permet d'ajouter de nouveaux patients, de saisir leurs données cliniques (âge, sexe, glucose, IMC, etc.), et de les visualiser dans une liste récapitulative.

**Prédiction Intelligente :** Un modèle de machine learning est intégré pour analyser les données de chaque patient et fournir une prédiction de risque de diabète (diabétique/non-diabétique), agissant comme un outil d'aide à la décision.

**Tableau de Bord :** Les médecins disposent d'une vue d'ensemble de leurs patients, affichant les données essentielles et le résultat de la prédiction du modèle.

**Technologies Utilisées**

*Backend* : FastAPI pour la création de l'API web, gérant les routes et les interactions avec la base de données.

*Frontend*: HTML, CSS avec Jinja2 pour le rendu dynamique des pages web.

*Base de Données* : PostgreSQL pour le stockage des données structurées (médecins, patients, prédictions).

*Hachage des mots de passe* : passlib et bcrypt.

*SQLAlchemy*: pour interagir avec la base de données.

*Machine Learning* : Modèle de type K-Nearest Neighbors (KNN) entraîné sur un jeu de données de référence et sauvegardé sous forme de fichier .pkl.

*Bibliothèques Python* : uvicorn, psycopg2-binary, scikit-learn, joblib.

**Installation et Démarrage**
Prérequis:

Python 3.8 ou supérieur

Un serveur de base de données PostgreSQL

**Étapes d'installation**
Installe les dépendances Python :

pip install fastapi uvicorn Jinja2 sqlalchemy psycopg2-binary passlib joblib scikit-learn

Configuration de la base de données :

Crée une base de données PostgreSQL nommée diabetoweb.

Assure-toi que les identifiants de connexion dans ton fichier app.py sont corrects :


**Démarrage de l'application :**

uvicorn app:app --reload

L'application sera accessible après via un lien sur le terminal.

**Structure du Projet**
.
├── app.py                  # Fichier principal de l'application FastAPI

├── models.py               # Définition des tables de la base de données

├── modele_diabetes.pkl           # Fichier du modèle de prédiction sauvegardé
 
├── templates/              # Dossier des fichiers HTML (Jinja2)
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_patient.html
│   └── list_patients.html
└── static/                 # Dossier des fichiers statiques (CSS, JS)
    └── styles.css

Auteur
Nom : Ibtissam Sannaky

Rôle : Développeuse
