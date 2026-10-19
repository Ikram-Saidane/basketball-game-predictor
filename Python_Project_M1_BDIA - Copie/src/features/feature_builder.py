# src/features/feature_builder.py (pour teams)

import pandas as pd
from src.features.teams_abrv import get_abbreviation  # fonction pour récupérer l'abréviation d'une franchise

def build_features(teams_df: pd.DataFrame):
    """
    Construit les 10 features principales pour chaque franchise actuelle.
    Retourne un DataFrame avec 30 lignes (une par franchise actuelle).
    """

    # Copier le DataFrame pour ne pas modifier l'original
    df = teams_df.copy()

    # Regrouper les données par franchise actuelle
    # On somme certaines colonnes, on prend le min/max pour les années
    grouped = df.groupby("Franchise_clean").agg({
        "Yrs": "sum",       # Total des saisons
        "W": "sum",         # Total des victoires
        "L": "sum",         # Total des défaites
        "Champ": "sum",     # Total des titres NBA
        "Conf": "sum",      # Total des finales de conférence
        "Plyfs": "sum",     # Total des participations aux playoffs
        "Div": "sum",       # Total des titres de division
        "From_year": "min", # Première année d'existence de la franchise
        "To_year": "max"    # Dernière année d'existence
    }).reset_index()        # Remet l'index en colonne normale

    # === Calcul des 10 features ===

    # 1. Nombre total de saisons
    grouped["Total_Years"] = grouped["Yrs"]

    # 2. Pourcentage de victoires sur toute l'histoire
    grouped["All_Time_WinRate"] = grouped["W"] / (grouped["W"] + grouped["L"])

    # 3. Nombre total de championnats remportés
    grouped["Total_Championships"] = grouped["Champ"]

    # 4. Nombre total de finales de conférence disputées
    grouped["Total_Finals"] = grouped["Conf"]

    # 5. Taux de participation aux playoffs
    grouped["Playoff_Rate"] = grouped["Plyfs"] / grouped["Total_Years"]

    # 6. Taux de titres de division
    grouped["Division_Titles_Rate"] = grouped["Div"] / grouped["Total_Years"]

    # 7. Années depuis le dernier championnat
    def last_title(team):
        # On récupère toutes les années où la franchise a gagné un championnat
        last_year = df[(df["Franchise_clean"] == team) & (df["Champ"] == 1)]["To_year"]
        if len(last_year) == 0:
            return 999  # Si jamais de championnat, valeur arbitraire
        return 2025 - last_year.max()  # Calcul du nombre d'années depuis le dernier titre

    grouped["Years_Since_Last_Title"] = grouped["Franchise_clean"].apply(last_title)

    # 8. La franchise a-t-elle changé de ville ?
    grouped["Has_Multiple_Cities"] = grouped["Franchise_clean"].apply(
        lambda t: df[df["Franchise_clean"] == t]["Franchise"].nunique() > 1
    )

    # 9. La franchise vient-elle de l'ABA ?
    grouped["ABA_Origin"] = grouped["Franchise_clean"].apply(
        lambda t: 1 if "ABA" in set(df[df["Franchise_clean"] == t]["Lg"]) else 0
    )

    # 10. La franchise a-t-elle eu une "Golden Era" ?
    def has_golden_era(team):
        # Récupérer les années où la franchise a gagné un titre
        years = df[df["Franchise_clean"] == team].sort_values("From_year")
        years_list = []
        for _, row in years.iterrows():
            if row["Champ"] == 1:
                years_list.append(row["To_year"])
        # Si moins de 3 titres, pas de Golden Era
        if len(years_list) < 3:
            return 0
        years_list = sorted(years_list)
        # Vérifie s'il y a 3 titres ou plus en 15 ans maximum
        for i in range(len(years_list) - 2):
            if years_list[i+2] - years_list[i] <= 15:
                return 1
        return 0

    grouped["Golden_Era"] = grouped["Franchise_clean"].apply(has_golden_era)

    # Ajouter l'abréviation de la franchise (utile pour affichage, non feature)
    grouped["Abbreviation"] = grouped["Franchise_clean"].apply(get_abbreviation)

    # Retourner le DataFrame final avec toutes les features
    return grouped
