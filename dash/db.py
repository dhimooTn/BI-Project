import pandas as pd
import sqlite3
import os

# Nom des fichiers
csv_file = "C:/Projects/Project Bi/data/hellowork_clustered.csv"
db_file = "hellowork.db"

# 1. Vérifier si le CSV existe
if not os.path.exists(csv_file):
    print(f"❌ ERREUR : Le fichier '{csv_file}' est introuvable !")
    print("👉 Assurez-vous qu'il est dans le même dossier que ce script.")
    exit()

print("✅ Fichier CSV trouvé. Lecture en cours...")

# 2. Lecture du CSV
try:
    df = pd.read_csv(csv_file)
    print(f"📊 {len(df)} lignes lues dans le CSV.")
except Exception as e:
    print(f"❌ Erreur de lecture CSV : {e}")
    exit()

# 3. Connexion et import en base
try:
    conn = sqlite3.connect(db_file)

    # On écrase la table 'offres' si elle existe déjà pour repartir propre
    df.to_sql("offres", conn, if_exists="replace", index=False)

    # Vérification
    cursor = conn.cursor()
    count = cursor.execute("SELECT count(*) FROM offres").fetchone()[0]
    print(f"🎉 SUCCÈS : {count} offres importées dans '{db_file}'.")

    conn.close()
except Exception as e:
    print(f"❌ Erreur SQLite : {e}")