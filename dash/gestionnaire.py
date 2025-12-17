import sqlite3
import pandas as pd
from datetime import datetime
import os

class GestionnaireOffres:
    def __init__(self, db_name="hellowork.db"):
        # Chemin relatif au dossier courant
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Création de la table avec les bons noms de colonnes
        query = """
                CREATE TABLE IF NOT EXISTS offres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emploi TEXT,
                    entreprise TEXT,
                    region TEXT,
                    departement TEXT,
                    salaire_annuel REAL,
                    categorie_salaire TEXT,
                    temps_travail TEXT,
                    cluster INTEGER,
                    date_publication TEXT
                );
                """
        cursor.execute(query)
        conn.commit()
        conn.close()

    def get_all_data(self):
        conn = self.get_connection()
        try:
            # On récupère tout
            df = pd.read_sql_query("SELECT * FROM offres", conn)
            return df
        except Exception as e:
            print(f"⚠️ Erreur lecture : {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def ajouter(self, emploi, entreprise, region, dept_code, salaire, categorie, temps, cluster=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        date_pub = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Correction ici : on utilise 'region' et 'departement' comme dans la table
        query = """
                INSERT INTO offres (emploi, entreprise, region, departement,
                                    salaire_annuel, categorie_salaire, temps_travail, cluster, date_publication)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
        try:
            cursor.execute(query, (emploi, entreprise, region, dept_code,
                                   salaire, categorie, temps, cluster, date_pub))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erreur ajout : {e}")
            return False
        finally:
            conn.close()

db_manager = GestionnaireOffres()