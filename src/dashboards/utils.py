
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# ============================================================================
# CONFIGURATION DES CHEMINS
# ============================================================================
# Définition des chemins relatifs pour accéder aux fichiers de données et modèles
# BASE_DIR pointe vers la racine du projet (3 niveaux au-dessus de ce fichier)
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "features"  # Répertoire contenant les données features
NOTEBOOKS_DIR = BASE_DIR / "notebooks"  # Répertoire contenant les notebooks et modèles

# Chemins des modèles pré-entraînés sauvegardés au format joblib
MVP_MODEL_PATH = NOTEBOOKS_DIR / "best_mvp_model_pipeline.joblib"
MATCH_MODEL_PATH = NOTEBOOKS_DIR / "best_model_pipeline.joblib"
CHAMPION_MODEL_PATH = NOTEBOOKS_DIR / "best_champion_model.joblib"

# Chemins des fichiers CSV contenant les données features
PLAYERS_DATA_PATH = DATA_DIR / "nba_players_features.csv"
TEAMS_DATA_PATH = DATA_DIR / "nba_teams_features.csv"
BOXSCORES_DATA_PATH = DATA_DIR / "nba_boxscores_features.csv"


# ============================================================================
# FONCTIONS DE CHARGEMENT DES MODÈLES
# ============================================================================

def load_mvp_model():
    """
    Charge le modèle pré-entraîné pour la prédiction MVP
    
    Le modèle est un pipeline scikit-learn sauvegardé au format joblib.
    Il contient le préprocessing et le modèle final identifié comme le meilleur
    dans le notebook mvp_prediction_2025.ipynb.
    
    Returns:
        Pipeline ou None: Le modèle MVP chargé, ou None en cas d'erreur
    """
    try:
        return joblib.load(MVP_MODEL_PATH)
    except Exception as e:
        return None


def load_match_model():
    """
    Charge le modèle pré-entraîné pour la prédiction de match
    
    Le modèle est un pipeline scikit-learn sauvegardé au format joblib.
    Il contient le préprocessing et le modèle final identifié comme le meilleur
    dans le notebook match_prediction_2025.ipynb.
    
    Returns:
        Pipeline ou None: Le modèle de match chargé, ou None en cas d'erreur
    """
    try:
        return joblib.load(MATCH_MODEL_PATH)
    except Exception as e:
        return None


def load_champion_model():
    """
    Charge le modèle pré-entraîné pour la prédiction de champion
    
    Le modèle est un LGBMClassifier sauvegardé au format joblib.
    Il a été identifié comme le meilleur modèle dans le notebook champ_prediction_2025.ipynb.
    
    Returns:
        LGBMClassifier ou None: Le modèle champion chargé, ou None en cas d'erreur
    """
    try:
        return joblib.load(CHAMPION_MODEL_PATH)
    except Exception as e:
        return None


# ============================================================================
# FONCTIONS DE CHARGEMENT DES DONNÉES
# ============================================================================

def load_players_data():
    """
    Charge les données des joueurs depuis le fichier CSV
    
    Les données contiennent les statistiques et features des joueurs NBA
    générées par le script PlayersFeatureEngineer.
    
    Returns:
        DataFrame ou None: DataFrame pandas avec les données des joueurs,
                          ou None en cas d'erreur de chargement
    """
    try:
        df = pd.read_csv(PLAYERS_DATA_PATH)
        # Conversion en string pour éviter les problèmes de type
        df["Player"] = df["Player"].astype(str)
        return df
    except Exception as e:
        return None


def load_teams_data():
    """
    Charge les données des équipes depuis le fichier CSV
    
    Les données contiennent les statistiques et features des équipes NBA
    générées par le script TeamsFeatureEngineer.
    
    Returns:
        DataFrame ou None: DataFrame pandas avec les données des équipes,
                          ou None en cas d'erreur de chargement
    """
    try:
        return pd.read_csv(TEAMS_DATA_PATH)
    except Exception as e:
        return None


def load_boxscores_data():
    """
    Charge les données des boxscores (résultats de matchs) depuis le fichier CSV
    
    Les données contiennent les statistiques détaillées de chaque match NBA
    générées par le script BoxscoreFeatureEngineer.
    
    Returns:
        DataFrame ou None: DataFrame pandas avec les données des matchs,
                          ou None en cas d'erreur de chargement
    """
    try:
        df = pd.read_csv(BOXSCORES_DATA_PATH)
        # Conversion de la colonne Date en datetime pour faciliter les opérations temporelles
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except Exception as e:
        return None


# ============================================================================
# FONCTIONS DE PRÉDICTION
# ============================================================================

def predict_mvp_ranking(df_input, season, best_pipeline, features, min_games=50):
    """
    Prédit le classement MVP pour une saison donnée
    
    Cette fonction reproduit la logique du notebook mvp_prediction_2025.ipynb
    pour générer un classement des joueurs selon leur probabilité d'être MVP.
    
    Processus :
    1. Filtrage des données (exclusion League Average, filtrage par saison)
    2. Filtrage par nombre minimum de matchs joués (avec fallback si nécessaire)
    3. Vérification et sélection des features disponibles
    4. Prédiction des probabilités MVP pour chaque joueur
    5. Tri par probabilité décroissante
    
    Args:
        df_input (DataFrame): DataFrame contenant les données des joueurs
        season (str): Saison à prédire (ex: "2025-2026")
        best_pipeline: Pipeline scikit-learn du modèle MVP pré-entraîné
        features (list): Liste des noms de colonnes à utiliser comme features
        min_games (int): Nombre minimum de matchs requis (par défaut 50)
    
    Returns:
        DataFrame: DataFrame contenant le classement avec colonnes :
                  ['Player', 'Age', 'Team', 'PTS', 'AST', 'TRB', 'MVP_Proba']
                  Trié par MVP_Proba décroissante. DataFrame vide si erreur.
    """
    df_input = df_input.copy()
    
    # Exclure les lignes "League Average" qui ne sont pas de vrais joueurs
    df_input = df_input[~df_input['Player'].astype(str).str.contains('League Average', case=False, na=False)]
    
    # Remplacer les valeurs infinies par NaN pour éviter les erreurs de calcul
    df_input.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Filtrer par saison si spécifiée
    if season is not None:
        df_input = df_input[df_input['Season'] == season]
        if df_input.empty:
            return pd.DataFrame()
    
    # Vérifier que la colonne 'G' (Games) existe pour filtrer par nombre de matchs
    if 'G' not in df_input.columns:
        return pd.DataFrame()
    
    # Filtrer les joueurs ayant joué au moins min_games matchs
    df_filtered = df_input[df_input['G'] >= min_games].copy()
    
    # Si aucun joueur ne satisfait le seuil, réduire progressivement le seuil
    # pour trouver une saison avec suffisamment de données
    if df_filtered.empty:
        for threshold in [40, 30, 20, 10]:
            df_filtered = df_input[df_input['G'] >= threshold].copy()
            if not df_filtered.empty:
                min_games = threshold
                break
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Vérifier quelles features sont disponibles dans les données
    missing_features = [f for f in features if f not in df_filtered.columns]
    if missing_features:
        # Utiliser uniquement les features disponibles
        available_features = [f for f in features if f in df_filtered.columns]
        if not available_features:
            return pd.DataFrame()
        features_to_use = available_features
    else:
        features_to_use = features
    
    try:
        # Préparer les données d'entrée pour le modèle
        X_input = df_filtered[features_to_use].copy()
        
        # Remplacer les valeurs manquantes (NaN) par la médiane de la colonne
        # Si la médiane est aussi NaN, remplacer par 0
        for col in X_input.columns:
            if X_input[col].isna().any():
                median_val = X_input[col].median()
                if pd.isna(median_val):
                    X_input[col] = X_input[col].fillna(0)
                else:
                    X_input[col] = X_input[col].fillna(median_val)
        
        # Prédire les probabilités MVP pour chaque joueur
        # predict_proba retourne [probabilité classe 0, probabilité classe 1]
        # On prend la colonne 1 (probabilité d'être MVP)
        df_filtered['MVP_Proba'] = best_pipeline.predict_proba(X_input)[:, 1]
        
        # Créer le classement trié par probabilité MVP décroissante
        ranking = df_filtered.sort_values('MVP_Proba', ascending=False)[
            ['Player', 'Age', 'Team', 'PTS', 'AST', 'TRB', 'MVP_Proba']
        ]
        
        return ranking
    except Exception as e:
        return pd.DataFrame()


def predict_champion_2025_2026(df_teams):
    """
    Prédit l'équipe championne pour la saison 2025-2026
    
    Cette fonction utilise le modèle pré-entraîné chargé depuis best_champion_model.joblib.
    Elle reproduit la logique du notebook champ_prediction_2025.ipynb sans retraîner le modèle.
    
    Processus :
    1. Chargement du modèle pré-entraîné (LGBMClassifier)
    2. Filtrage des équipes actuelles de la NBA (30 équipes)
    3. Calcul de la feature composite "Dynasty_Power"
    4. Prédiction des probabilités avec le modèle chargé
    5. Sélection de l'équipe avec la plus haute probabilité
    
    Args:
        df_teams (DataFrame): DataFrame contenant les données des équipes
    
    Returns:
        tuple: (champ_team, champ_abbr, champ_proba)
            - champ_team (str): Nom complet de l'équipe championne prédite
            - champ_abbr (str): Abréviation de l'équipe championne prédite
            - champ_proba (float): Probabilité de victoire (entre 0 et 1)
    """
    # Charger le modèle pré-entraîné au lieu de le retraîner
    best_model = load_champion_model()
    if best_model is None:
        raise ValueError("Impossible de charger le modèle champion. Vérifiez que best_champion_model.joblib existe dans le dossier notebooks/")
    
    df = df_teams.copy()
    
    # Filtrer uniquement les équipes actuelles de la NBA (30 équipes)
    current_teams = ['BOS','LAL','SAS','OKC','PHO','UTA','MIL','MIA','POR','DEN','HOU','PHI','IND',
                     'CHI','DAL','ATL','NYK','GSW','CLE','DET','TOR','ORL','NOP','SAC',
                     'BKN','MEM','WAS','LAC','MIN','CHA']
    df = df[df['Abbreviation'].isin(current_teams)].copy()
    
    # Créer une feature composite "Dynasty_Power" qui combine plusieurs métriques
    # avec des poids différents pour refléter l'importance de chaque facteur
    # Cette feature doit être calculée de la même manière que lors de l'entraînement
    df['Dynasty_Power'] = (
        df['AllTime_WinRate']*0.40 +      # 40% : Taux de victoire historique
        df['Playoff_Rate']*0.30 +          # 30% : Taux de qualification en playoffs
        df['Champ_Rate']*0.20 +            # 20% : Taux de victoire en championnat
        df['Finals_Rate']*0.10             # 10% : Taux de qualification en finales
    )
    
    # Liste des features utilisées pour la prédiction (doit correspondre à l'entraînement)
    features = ['AllTime_WinRate','Playoff_Rate','Champ_Rate','Finals_Rate',
                'Dynasty_Power','Age','Champ','Has_Relocated','ABA_Origin']
    
    # Vérifier que toutes les features sont présentes
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Features manquantes dans les données: {missing_features}")
    
    X = df[features]
    
    # Prédire les probabilités pour chaque équipe avec le modèle pré-entraîné
    proba = best_model.predict_proba(X)[:, 1]  # Probabilité d'être champion
    
    # Ajouter les probabilités au DataFrame et trier par probabilité décroissante
    df['Win_Probability_2026'] = proba
    df_sorted = df.sort_values('Win_Probability_2026', ascending=False)
    
    # Extraire l'équipe avec la plus haute probabilité
    champ_team = df_sorted.iloc[0]['Team']
    champ_abbr = df_sorted.iloc[0]['Abbreviation']
    champ_proba = df_sorted.iloc[0]['Win_Probability_2026']
    
    return champ_team, champ_abbr, champ_proba


def compute_team_rolling_stats(df_full, team, as_of_date, window=10):
    """
    Calcule les statistiques glissantes (rolling stats) d'une équipe
    
    Cette fonction calcule la moyenne des métriques pour les N derniers matchs
    d'une équipe avant une date donnée. Cela permet de capturer la forme récente
    de l'équipe plutôt que ses statistiques globales.
    
    Args:
        df_full (DataFrame): DataFrame contenant tous les matchs historiques
        team (str): Nom de l'équipe
        as_of_date (datetime): Date de référence (on ne considère que les matchs avant cette date)
        window (int): Nombre de matchs à considérer pour la moyenne (par défaut 10)
    
    Returns:
        dict ou None: Dictionnaire contenant les statistiques glissantes, notamment:
                      - 'Home_Rolling_WinRate' ou 'Away_Rolling_WinRate' selon le contexte
                      Retourne None si pas assez de données
    """
    # Filtrer les matchs avant la date de référence
    hist = df_full[df_full['Date'] < as_of_date]
    
    # Filtrer les matchs où l'équipe a joué (à domicile ou à l'extérieur)
    played = hist[(hist['HomeTeam'] == team) | (hist['AwayTeam'] == team)].sort_values("Date", ascending=False).head(window)
    
    if played.empty:
        return None
    
    # Calculer si l'équipe a gagné pour chaque match
    wins = []
    for _, row in played.iterrows():
        if row['HomeTeam'] == team:
            # L'équipe jouait à domicile : elle gagne si HomePts > AwayPts
            # Utiliser HomeWin si disponible, sinon calculer depuis les points
            if 'HomeWin' in row:
                wins.append(int(row['HomeWin']))
            elif 'HomePts' in row and 'AwayPts' in row:
                wins.append(1 if row['HomePts'] > row['AwayPts'] else 0)
            else:
                wins.append(0)  # Par défaut, considérer comme défaite si données manquantes
        else:
            # L'équipe jouait à l'extérieur : elle gagne si AwayPts > HomePts
            # Si HomeWin = 1, alors l'équipe à domicile a gagné, donc notre équipe a perdu
            if 'HomeWin' in row:
                wins.append(1 - int(row['HomeWin']))  # Inverse de HomeWin
            elif 'HomePts' in row and 'AwayPts' in row:
                wins.append(1 if row['AwayPts'] > row['HomePts'] else 0)
            else:
                wins.append(0)  # Par défaut, considérer comme défaite si données manquantes
    
    # Calculer le taux de victoire glissant
    rolling_winrate = sum(wins) / len(wins) if wins else 0.5
    
    # Retourner un dictionnaire avec la statistique de taux de victoire
    # On utilise 'Home_Rolling_WinRate' comme clé car c'est ce que le modèle attend
    # (le modèle s'attend à cette feature même si l'équipe joue à l'extérieur)
    return {'Home_Rolling_WinRate': rolling_winrate, 'Away_Rolling_WinRate': rolling_winrate}


def predict_match_live(home_team, away_team, df_boxscores, best_pipeline, features, date_as_of=None):
    """
    Prédit le gagnant d'un match entre deux équipes
    
    Cette fonction reproduit la logique du notebook match_prediction_2025.ipynb.
    Elle utilise les statistiques glissantes des deux équipes pour prédire
    quelle équipe a le plus de chances de gagner.
    
    Processus :
    1. Calcul des statistiques glissantes pour chaque équipe (10 derniers matchs)
    2. Construction des features d'entrée pour le modèle
    3. Prédiction de la probabilité de victoire de l'équipe à domicile
    4. Détermination du gagnant prédit (probabilité > 0.5 = domicile gagne)
    
    Args:
        home_team (str): Nom de l'équipe à domicile
        away_team (str): Nom de l'équipe à l'extérieur
        df_boxscores (DataFrame): DataFrame contenant les données des matchs
        best_pipeline: Pipeline scikit-learn du modèle de match pré-entraîné
        features (list): Liste des noms de colonnes à utiliser comme features
        date_as_of (datetime, optional): Date de référence pour le calcul des stats.
                                        Si None, utilise la date du dernier match + 1 jour
    
    Returns:
        dict ou None: Dictionnaire contenant :
            - "home": Nom de l'équipe à domicile
            - "away": Nom de l'équipe à l'extérieur
            - "proba_home": Probabilité de victoire de l'équipe à domicile (0-1)
            - "pred": Prédiction binaire (1 = domicile gagne, 0 = extérieur gagne)
            - "winner": Nom de l'équipe gagnante prédite
            Retourne None si pas assez de données historiques
    """
    # Si aucune date n'est spécifiée, utiliser la date du dernier match + 1 jour
    # Cela permet de prédire pour un match futur
    if date_as_of is None:
        date_as_of = df_boxscores['Date'].max() + pd.Timedelta(days=1)
    
    # Calculer les statistiques glissantes pour chaque équipe
    # Ces stats reflètent la forme récente de l'équipe (10 derniers matchs)
    home_stats = compute_team_rolling_stats(df_boxscores, home_team, date_as_of, window=10)
    away_stats = compute_team_rolling_stats(df_boxscores, away_team, date_as_of, window=10)
    
    # Vérifier qu'on a assez de données historiques pour les deux équipes
    if home_stats is None or away_stats is None:
        return None
    
    # Construire le dictionnaire de features pour le modèle
    # Les features principales sont les taux de victoire glissants des deux équipes
    # home_stats et away_stats sont des dictionnaires retournés par compute_team_rolling_stats
    feat = {
        'Home_Rolling_WinRate': home_stats.get('Home_Rolling_WinRate', 0.5) if isinstance(home_stats, dict) else 0.5,  # Taux de victoire récent équipe domicile
        'Away_Rolling_WinRate': away_stats.get('Away_Rolling_WinRate', 0.5) if isinstance(away_stats, dict) else 0.5,  # Taux de victoire récent équipe extérieur
        'Home_RestAdv': 0  # Avantage du repos (non utilisé pour l'instant, valeur par défaut 0)
    }
    
    # Créer un DataFrame avec les features
    X_input = pd.DataFrame([feat])
    
    # S'assurer que toutes les features requises sont présentes
    # Si une feature manque, utiliser une valeur par défaut
    for col in features:
        if col not in X_input.columns:
            # Valeur par défaut : 0.5 pour les WinRate, 0 pour le reste
            X_input[col] = 0.5 if 'WinRate' in col else 0
    
    # Sélectionner uniquement les features dans l'ordre attendu par le modèle
    X_input = X_input[features]
    
    # Prédire la probabilité de victoire de l'équipe à domicile
    proba = best_pipeline.predict_proba(X_input)[0, 1]  # Probabilité classe 1 (domicile gagne)
    
    # Déterminer la prédiction binaire (seuil à 0.5)
    pred = 1 if proba > 0.5 else 0
    
    # Déterminer le gagnant
    winner = home_team if pred == 1 else away_team
    
    return {
        "home": home_team,
        "away": away_team,
        "proba_home": proba,
        "pred": pred,
        "winner": winner
    }
