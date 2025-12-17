import pandas as pd
import sqlite3
import os
from gestionnaire import db_manager  # On utilise le chemin du gestionnaire

# --- CONFIGURATION ---
# Mettez ici le chemin vers votre CSV
csv_file = "C:/Users/Manai/PycharmProjects/BI-Project/data/hellowork_clustered.csv"

# Vérification présence CSV
if not os.path.exists(csv_file):
    print(f"❌ ERREUR : Fichier introuvable : {csv_file}")
    exit()

print("✅ CSV trouvé. Traitement en cours...")

try:
    # 1. Lecture
    df = pd.read_csv(csv_file)
    print(f"📊 Lignes lues : {len(df)}")
    print(f"   Colonnes initiales : {df.columns.tolist()}")

    # 2. RENOMMAGE DES COLONNES (Mapping)
    # À GAUCHE : Les noms dans VOTRE CSV / À DROITE : Les noms pour l'APP
    # Adaptez la partie gauche si votre CSV est différent (ex: 'Job Title' au lieu de 'intitule')
    mapping = {
        'intitule': 'emploi',
        'company': 'entreprise',
        'city': 'region',
        'dept': 'departement',
        'salary': 'salaire_annuel',
        'contract': 'temps_travail',
        'cluster': 'cluster'
    }

    # On renomme uniquement ce qui existe
    df.rename(columns=mapping, inplace=True)

    # 3. Nettoyage rapide avant insertion
    # Forcer le code département en string (ex: "01" et pas 1)
    if 'departement' in df.columns:
        df['departement'] = df['departement'].apply(lambda x: str(x).zfill(2) if pd.notnull(x) else "00")

    # S'assurer que les colonnes manquantes existent pour éviter le crash SQL
    required_cols = ['emploi', 'entreprise', 'region', 'departement',
                     'salaire_annuel', 'categorie_salaire', 'temps_travail', 'cluster']

    for col in required_cols:
        if col not in df.columns:
            df[col] = None  # On remplit avec vide si manquant

    # 4. Insertion via SQLite direct (sur le même chemin que le gestionnaire)
    conn = db_manager.get_connection()

    # On vide et on remplace
    df.to_sql("offres", conn, if_exists="replace", index=False)

    print(f"🎉 SUCCÈS : Données importées dans {db_manager.db_path}")
    conn.close()

except Exception as e:
    print(f"❌ CRASH : {e}")