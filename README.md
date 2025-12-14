# Projet BI : Analyse et Visualisation Dynamique des Offres d'Emploi (Hellowork)

## 📌 Objectif
Le projet vise à construire une solution complète de **Business Intelligence (BI)** et d'**analyse prédictive** pour les offres d'emploi du site **Hellowork.com**.  
Le processus comprend l'extraction, la transformation, l'enrichissement par Machine Learning, et la visualisation interactive des données via un dashboard.

---

## 📂 Structure du Projet

Le projet est organisé en **4 phases principales** :

### Phase 1 : Extraction des Données (Web Scraping)
- **Objectif** : Collecter les informations pertinentes des offres d'emploi (titre, entreprise, localisation, salaire, description, date, etc.).
- **Outils envisagés** :
  - **Selenium** ou **Scrapy** si le contenu est chargé dynamiquement.
  - **BeautifulSoup + Requests** pour les pages statiques.

### Phase 2 : Préparation des Données (ETL)
- **Objectif** : Nettoyer, structurer et transformer les données brutes.
- **Actions** :
  - Extraction de mots-clés depuis les descriptions
  - Standardisation des salaires
  - Gestion des champs manquants
  - Encodage des variables catégorielles
- **Outils** : `pandas`, `scikit-learn` (préprocessing)

### Phase 3 : Modélisation et Enrichissement ML
- **Clustering** : Appliquer **KMeans** sur les descriptions vectorisées pour identifier des groupes de métiers/compétences.
- **Classification** : Développer un modèle (ex: **Régression Logistique**) pour classer les offres (ex: salaire haut/bas, urgence).
- **Sortie** : Ajout des prédictions et clusters comme nouvelles colonnes dans le jeu de données.

### Phase 4 : Dashboard Interactif (Dash)
- **Objectif** : Créer une application web interactive pour visualiser et explorer les données.
- **Fonctionnalités** :
  - Filtres dynamiques sur les colonnes originales
  - Intégration des résultats des modèles ML
  - Visualisations interactives (graphiques, cartes, tableaux)
- **Technologie** : **Dash** (Python)

---

## 🛠️ Technologies Utilisées
- **Python 3.8+**
- **Web Scraping** : Selenium, Scrapy, BeautifulSoup, Requests
- **Traitement des données** : pandas, NumPy
- **Machine Learning** : scikit-learn
- **Visualisation** : Dash, Plotly
- **Gestion de projet** : Git, environnement virtuel (venv/conda)

---

## 📊 Résultats Attendus
1. Un jeu de données structuré et enrichi d’offres d'emploi.
2. Des modèles ML permettant de catégoriser et regrouper les offres.
3. Un dashboard interactif accessible via navigateur pour l’exploration des données.

---

## 📁 Organisation des Fichiers (Recommandée)