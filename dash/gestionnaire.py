import sqlite3
import pandas as pd
from datetime import datetime
import os


class GestionnaireOffres:
    def __init__(self, db_name="hellowork.db"):
        """Initialise le gestionnaire de base de données"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.init_db()

    def get_connection(self):
        """Retourne une connexion SQLite"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_db(self):
        """Crée la table si elle n'existe pas"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS offres
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           emploi
                           TEXT
                           NOT
                           NULL,
                           entreprise
                           TEXT
                           NOT
                           NULL,
                           date_publication
                           TEXT,
                           temps_travail
                           INTEGER,
                           salaire_annuel
                           REAL,
                           categorie_salaire
                           INTEGER,
                           region
                           TEXT,
                           departement
                           INTEGER,
                           cluster
                           INTEGER
                           DEFAULT
                           0
                       )
                       """)

        conn.commit()
        conn.close()
        print(f"✅ Base de données: {self.db_path}")

    def get_all_data(self):
        """Récupère toutes les offres"""
        conn = self.get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM offres", conn)
            print(f"📊 {len(df)} offres récupérées")
            return df
        except Exception as e:
            print(f"⚠️ Erreur lecture: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def ajouter(self, emploi, entreprise, region, departement,
                salaire, categorie, temps, cluster=0):
        """
        Ajoute une nouvelle offre

        Returns:
            bool: True si succès
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        date_pub = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("""
                           INSERT INTO offres
                           (emploi, entreprise, date_publication, temps_travail,
                            salaire_annuel, categorie_salaire, region, departement, cluster)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, (emploi, entreprise, date_pub, temps, salaire,
                                 categorie, region, departement, cluster))

            conn.commit()

            print("=" * 60)
            print("✅ OFFRE AJOUTÉE")
            print("=" * 60)
            print(f"📝 {emploi} | 🏢 {entreprise}")
            print(f"📍 {region} ({departement})")
            print(f"💰 {salaire}€ | 🎯 Cluster {cluster}")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"❌ Erreur ajout: {e}")
            return False
        finally:
            conn.close()

    def supprimer(self, offre_id):
        """Supprime une offre par ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM offres WHERE id = ?", (offre_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"✅ Offre {offre_id} supprimée")
                return True
            else:
                print(f"⚠️ Offre {offre_id} introuvable")
                return False

        except Exception as e:
            print(f"❌ Erreur suppression: {e}")
            return False
        finally:
            conn.close()

    def modifier(self, offre_id, **kwargs):
        """
        Modifie une offre existante

        Args:
            offre_id: ID de l'offre
            **kwargs: Champs à modifier (emploi, entreprise, etc.)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = ?")
                params.append(value)

        if not updates:
            print("⚠️ Aucune modification")
            return False

        params.append(offre_id)
        query = f"UPDATE offres SET {', '.join(updates)} WHERE id = ?"

        try:
            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount > 0:
                print(f"✅ Offre {offre_id} modifiée")
                return True
            else:
                print(f"⚠️ Offre {offre_id} introuvable")
                return False

        except Exception as e:
            print(f"❌ Erreur modification: {e}")
            return False
        finally:
            conn.close()

    def rechercher(self, **criteres):
        """Recherche des offres selon des critères"""
        conn = self.get_connection()

        try:
            conditions = []
            params = []

            for key, value in criteres.items():
                if value is not None:
                    conditions.append(f"{key} = ?")
                    params.append(value)

            if conditions:
                query = f"SELECT * FROM offres WHERE {' AND '.join(conditions)}"
                df = pd.read_sql_query(query, conn, params=params)
            else:
                df = pd.read_sql_query("SELECT * FROM offres", conn)

            print(f"🔍 {len(df)} offres trouvées")
            return df

        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_stats(self):
        """Récupère des statistiques"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            cursor.execute("SELECT COUNT(*) FROM offres")
            stats['total_offres'] = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(salaire_annuel) FROM offres")
            stats['salaire_moyen'] = cursor.fetchone()[0]

            cursor.execute("SELECT cluster, COUNT(*) FROM offres GROUP BY cluster")
            stats['offres_par_cluster'] = dict(cursor.fetchall())

            cursor.execute("SELECT COUNT(DISTINCT entreprise) FROM offres")
            stats['nb_entreprises'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT departement) FROM offres")
            stats['nb_departements'] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"❌ Erreur stats: {e}")
            return {}
        finally:
            conn.close()


# Instance globale
db_manager = GestionnaireOffres()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 TEST DU GESTIONNAIRE")
    print("=" * 60)

    stats = db_manager.get_stats()
    print("\n📊 Statistiques:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Gestionnaire prêt!")
    print("=" * 60)