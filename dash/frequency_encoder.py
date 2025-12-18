"""
Encodeur de fréquence pour les variables catégorielles
Doit être importé AVANT de charger le modèle
"""
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class FrequencyEncoder(BaseEstimator, TransformerMixin):
    """
    Encode les variables catégorielles en utilisant leur fréquence d'apparition
    """
    def __init__(self, columns):
        self.columns = columns
        self.freq_maps_ = {}

    def fit(self, X, y=None):
        X = pd.DataFrame(X, columns=self.columns)
        for col in self.columns:
            self.freq_maps_[col] = X[col].value_counts(normalize=True)
        return self

    def transform(self, X):
        X = pd.DataFrame(X, columns=self.columns)
        X_encoded = pd.DataFrame()
        for col in self.columns:
            X_encoded[col] = X[col].map(self.freq_maps_[col]).fillna(0)
        return X_encoded.values