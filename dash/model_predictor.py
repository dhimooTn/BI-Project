import joblib
import pickle
import pandas as pd
import os

# Import de FrequencyEncoder (doit être disponible)
from frequency_encoder import FrequencyEncoder


class ClusterPredictor:
    def __init__(self, model_path='model_class'):
        """
        Initialise le prédicteur de cluster

        Args:
            model_path: Chemin vers le fichier du modèle (sans extension)
        """
        self.model = None
        self.model_path = model_path
        self.load_model()

    def load_model(self):
        """Charge le modèle depuis différents formats possibles"""
        extensions = ['', '.joblib', '.pkl', '.h5', '.sav']

        for ext in extensions:
            path = f"{self.model_path}{ext}"
            if not os.path.exists(path):
                continue

            try:
                if ext == '.h5':
                    self.model = self._load_from_h5(path)
                elif ext == '.pkl':
                    with open(path, 'rb') as f:
                        self.model = pickle.load(f)
                else:
                    self.model = joblib.load(path)

                print(f"✅ Modèle chargé: {path}")
                print(f"ℹ️  Type: {type(self.model).__name__}")

                if hasattr(self.model, 'steps'):
                    print("📋 Pipeline:")
                    for i, (name, step) in enumerate(self.model.steps, 1):
                        print(f"   {i}. {name}: {type(step).__name__}")

                self.model_path = path
                return

            except Exception as e:
                print(f"⚠️  Erreur avec {path}: {e}")
                continue

        print(f"❌ Aucun modèle trouvé: '{self.model_path}'")
        self.model = None

    def _load_from_h5(self, h5_path):
        """Charge un modèle depuis HDF5"""
        try:
            import h5py
            with h5py.File(h5_path, 'r') as hf:
                if 'model' in hf:
                    return pickle.loads(bytes(hf['model'][()]))
                raise ValueError("Format HDF5 invalide")
        except ImportError:
            raise ImportError("h5py requis: pip install h5py")

    def preprocess_input(self, emploi, entreprise, ville, departement,
                         salaire, categorie_salaire, temps_travail):
        """Prépare les données pour la prédiction"""
        return pd.DataFrame({
            'emploi': [str(emploi)],
            'entreprise': [str(entreprise)],
            'region': [str(ville)],
            'departement': [int(departement)],
            'salaire_annuel': [float(salaire)],
            'categorie_salaire': [int(categorie_salaire)],
            'temps_travail': [int(temps_travail)]
        })

    def predict_cluster(self, emploi, entreprise, ville, departement,
                        salaire, categorie_salaire, temps_travail):
        """
        Prédit le cluster pour une nouvelle offre

        Returns:
            int: Numéro du cluster (0 par défaut si erreur)
        """
        if self.model is None:
            print("❌ Modèle non chargé, cluster par défaut: 0")
            return 0

        try:
            X = self.preprocess_input(emploi, entreprise, ville, departement,
                                      salaire, categorie_salaire, temps_travail)

            cluster = int(self.model.predict(X)[0])

            print(f"✅ Cluster prédit: {cluster}")
            print(f"   📝 {emploi} | 🏢 {entreprise}")
            print(f"   📍 {ville} ({departement}) | 💰 {salaire}€")

            return cluster

        except Exception as e:
            print(f"❌ Erreur prédiction: {e}")
            return 0

    def predict_cluster_with_proba(self, emploi, entreprise, ville, departement,
                                   salaire, categorie_salaire, temps_travail):
        """
        Prédit le cluster avec probabilités

        Returns:
            tuple: (cluster, probabilities_dict)
        """
        if self.model is None:
            return 0, {}

        try:
            X = self.preprocess_input(emploi, entreprise, ville, departement,
                                      salaire, categorie_salaire, temps_travail)

            cluster = int(self.model.predict(X)[0])
            probas_dict = {}

            if hasattr(self.model, 'predict_proba'):
                probas = self.model.predict_proba(X)[0]
                probas_dict = {f"Cluster {i}": float(p) * 100
                               for i, p in enumerate(probas)}
                print("📊 Probabilités:")
                for name, proba in probas_dict.items():
                    print(f"   {name}: {proba:.2f}%")

            return cluster, probas_dict

        except Exception as e:
            print(f"❌ Erreur prédiction avec probas: {e}")
            return 0, {}


# Instance globale
print("\n" + "=" * 60)
print("🚀 INITIALISATION DU PRÉDICTEUR")
print("=" * 60)

try:
    predictor = ClusterPredictor('model_class')
    if predictor.model is not None:
        print("🤖 PRÉDICTEUR PRÊT ✅")
    else:
        print("⚠️  MODE DÉGRADÉ (cluster par défaut = 0)")
except Exception as e:
    print(f"⚠️  Erreur initialisation: {e}")
    predictor = None

print("=" * 60 + "\n")