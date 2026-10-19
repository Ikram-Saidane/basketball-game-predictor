# src/ml/train_rf.py (teams)

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from src.features.feature_builder import build_features  # fonction pour construire les features à partir du dataset

def train_model():
    """
    Entraîne un modèle Random Forest pour prédire si une franchise NBA a gagné un championnat depuis 2000.
    Retourne le modèle entraîné et le DataFrame des features.
    """

    #Charger le dataset nettoyé des équipes NBA
    df = pd.read_csv("data/cleaned/nba_teams_clean.csv")

    #Construire les features à partir du dataset
    features_df = build_features(df)

    #Sélectionner les colonnes/features pour l'entraînement
    X = features_df[[  # features explicatives
        "Total_Years",             # nombre total de saisons
        "All_Time_WinRate",        # pourcentage de victoires all-time
        "Total_Championships",     # nombre de titres NBA
        "Total_Finals",            # nombre de finales de conférence
        "Playoff_Rate",            # taux de participation aux playoffs
        "Division_Titles_Rate",    # taux de titres de division
        "Years_Since_Last_Title",  # années depuis le dernier championnat
        "Has_Multiple_Cities",     # 1 si la franchise a changé de ville
        "ABA_Origin",              # 1 si origine ABA
        "Golden_Era"               # 1 si période dominante
    ]]

    #Définir la variable cible (label)
    # y = 1 si la franchise a gagné au moins un championnat depuis l'an 2000
    y = (features_df["Years_Since_Last_Title"] <= (2025 - 2000)).astype(int)

    #Créer et entraîner le modèle Random Forest
    model = RandomForestClassifier(n_estimators=500, random_state=42)
    model.fit(X, y)  # entraînement sur les features X et le label y

    #Affichage du résultat
    print("Modèle entraîné !")
    print("Feature importance :")  # montrer quelles features ont le plus contribué
    for name, importance in zip(X.columns, model.feature_importances_):
        print(f"{name:25s}  → {importance:.3f}")  # importance normalisée de chaque feature

    #Retourner le modèle et le DataFrame des features
    return model, features_df
