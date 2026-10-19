"""
Page de prédiction MVP - Meilleur Joueur de la Saison

Cette page affiche la prédiction du meilleur joueur (MVP) pour une saison donnée.
Elle utilise le modèle pré-entraîné chargé depuis utils.py pour générer un classement
des joueurs selon leur probabilité d'être MVP.

Fonctionnalités :
- Affichage du joueur prédit comme MVP avec ses statistiques
- Affichage des métriques clés (points, passes, rebonds, probabilité MVP)
- Affichage du Top 5 des joueurs dans un tableau détaillé
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION DES IMPORTS
# ============================================================================
# Ajouter le répertoire parent au path Python pour pouvoir importer utils.py
# Cela est nécessaire car les pages sont dans un sous-dossier (pages/)
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import des fonctions utilitaires depuis utils.py
from utils import load_mvp_model, load_players_data, predict_mvp_ranking

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
st.set_page_config(
    page_title="Prédiction MVP",
    page_icon="🏆",
    layout="wide"  # Layout large pour utiliser toute la largeur
)

# ============================================================================
# STYLES CSS PERSONNALISÉS
# ============================================================================
# Styles CSS pour améliorer l'apparence de la page
st.markdown("""
<style>
.section-header {
    font-size: 1.8rem;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #3498db;
}
.player-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EN-TÊTE DE LA PAGE
# ============================================================================
# Titre principal de la page
st.markdown('<h1 class="section-header">🏆 Prédiction MVP - Meilleur Joueur</h1>', unsafe_allow_html=True)

# Bouton de navigation pour retourner à la page d'accueil
if st.button("← Retour à l'accueil"):
    st.switch_page("app.py")

st.markdown("---")  # Séparateur horizontal

# ============================================================================
# CHARGEMENT DES DONNÉES ET MODÈLE
# ============================================================================
# Chargement du modèle MVP pré-entraîné et des données des joueurs
# Affichage d'un spinner pendant le chargement
with st.spinner("Chargement des données..."):
    mvp_model = load_mvp_model()
    df_players = load_players_data()

# Vérification que le modèle et les données ont été chargés correctement
if mvp_model is None or df_players is None:
    st.error("❌ Impossible de charger les données nécessaires.")
    st.stop()  # Arrêter l'exécution si les données ne sont pas disponibles

# ============================================================================
# CONFIGURATION DES FEATURES
# ============================================================================
# Liste des features utilisées par le modèle MVP
# Ces features correspondent à celles utilisées lors de l'entraînement du modèle
mvp_features = [
    'Age', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 
    '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 
    'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 
    'Rolling_PPG', 'Rolling_APG', 'Rolling_RPG', 'Rolling_3P%', 'Rolling_FG%', 'PPG_Improvement'
]

# Vérifier quelles features sont disponibles dans les données
# Si certaines features manquent, on les retire de la liste
missing_cols = [col for col in mvp_features if col not in df_players.columns]
if missing_cols:
    mvp_features = [col for col in mvp_features if col in df_players.columns]

# ============================================================================
# SÉLECTION DE LA SAISON
# ============================================================================
# Récupérer la liste des saisons disponibles, triées par ordre décroissant
available_seasons = sorted(df_players['Season'].unique(), reverse=True) if 'Season' in df_players.columns else []

if not available_seasons:
    st.error("❌ Aucune saison disponible")
    st.stop()

# Trouver automatiquement la première saison avec suffisamment de données valides
# On cherche une saison avec au moins 10 joueurs ayant joué au moins 20 matchs
selected_season = None
for s in available_seasons:
    df_season_test = df_players[df_players['Season'] == s].copy()
    # Exclure les lignes "League Average"
    df_season_test = df_season_test[~df_season_test['Player'].astype(str).str.contains('League Average', case=False, na=False)]
    if 'G' in df_season_test.columns:
        # Filtrer les joueurs avec au moins 20 matchs
        df_season_test = df_season_test[df_season_test['G'] >= 20]
        # Vérifier qu'on a au moins 10 joueurs
        if len(df_season_test) >= 10:
            selected_season = s
            break

if selected_season is None:
    st.error("❌ Aucune saison avec suffisamment de données valides")
    st.stop()

season = selected_season

# ============================================================================
# PRÉDICTION MVP
# ============================================================================
# Calcul de la prédiction MVP pour la saison sélectionnée
# La fonction predict_mvp_ranking retourne un DataFrame trié par probabilité MVP
with st.spinner(f"Calcul de la prédiction MVP pour la saison {season}..."):
    ranking = predict_mvp_ranking(df_players, season, mvp_model, mvp_features, min_games=50)

# ============================================================================
# AFFICHAGE DES RÉSULTATS
# ============================================================================
if not ranking.empty:
    # Extraire le meilleur joueur (premier du classement)
    best_player = ranking.iloc[0]
    
    # Carte principale affichant le joueur MVP prédit
    # Utilisation d'un style CSS personnalisé avec dégradé de couleurs
    st.markdown(f"""
    <div class="player-card">
        <h2 style="margin: 0; font-size: 2rem;">🏆 {best_player['Player']}</h2>
        <p style="font-size: 1.2rem; margin-top: 0.5rem;">
            <strong>Équipe:</strong> {best_player['Team']} | 
            <strong>Âge:</strong> {int(best_player['Age'])} ans
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage des métriques clés dans 3 colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Points totaux", f"{int(best_player['PTS']):,}")
    
    with col2:
        st.metric("Passes décisives", f"{int(best_player['AST']):,}")
    
    with col3:
        st.metric("Rebonds", f"{int(best_player['TRB']):,}")
    
    # Section expandable pour afficher le Top 5 des joueurs
    # Le tableau est stylisé avec un gradient de couleurs sur la colonne MVP_Proba
    with st.expander("📋 Voir le Top 5 des joueurs", expanded=False):
        st.dataframe(
            ranking.head(5).style.background_gradient(subset=['MVP_Proba'], cmap='YlOrRd'),
            use_container_width=True,
            hide_index=True
        )
else:
    # Message d'avertissement si aucune donnée n'est disponible
    st.warning(f"⚠️ Aucune donnée disponible pour la saison {season}")


