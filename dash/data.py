import pandas as pd
import os
from gestionnaire import db_manager

# Configuration
CSV_FILE = r"C:\Projects\Project Bi\data\hellowork_clustered.csv"


def import_csv_to_db(csv_path):
    """Importe un CSV dans la base de données"""

    # Vérification
    if not os.path.exists(csv_path):
        print(f"❌ Fichier introuvable: {csv_path}")
        return False

    print(f"✅ CSV trouvé: {csv_path}")

    try:
        # Lecture
        df = pd.read_csv(csv_path)
        print(f"📊 {len(df)} lignes lues")
        print(f"   Colonnes: {df.columns.tolist()}")

        # Mapping des colonnes (adaptez selon votre CSV)
        column_mapping = {
            'intitule': 'emploi',
            'company': 'entreprise',
            'city': 'region',
            'dept': 'departement',
            'salary': 'salaire_annuel',
            'contract': 'temps_travail',
            'cluster': 'cluster'
        }

        df.rename(columns=column_mapping, inplace=True)

        # Nettoyage
        if 'departement' in df.columns:
            df['departement'] = df['departement'].apply(
                lambda x: str(x).zfill(2) if pd.notnull(x) else "00")

        # Colonnes requises
        required = ['emploi', 'entreprise', 'region', 'departement',
                    'salaire_annuel', 'categorie_salaire', 'temps_travail', 'cluster']

        for col in required:
            if col not in df.columns:
                df[col] = None

        # Insertion
        conn = db_manager.get_connection()
        df.to_sql("offres", conn, if_exists="replace", index=False)
        conn.close()

        print(f"🎉 Import réussi: {len(df)} offres")
        print(f"   Base: {db_manager.db_path}")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📥 IMPORT CSV → BASE DE DONNÉES")
    print("=" * 60 + "\n")

    success = import_csv_to_db(CSV_FILE)

    if success:
        stats = db_manager.get_stats()
        print("\n📊 Statistiques:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

    print("\n" + "=" * 60)