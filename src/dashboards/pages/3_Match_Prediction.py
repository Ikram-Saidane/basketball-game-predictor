"""
Page de prédiction de match - Gagnant d'un match entre deux équipes

Cette page permet de prédire le gagnant d'un match entre deux équipes NBA.
L'utilisateur sélectionne deux équipes et le modèle calcule la probabilité
de victoire de chaque équipe en se basant sur leurs statistiques récentes.

Fonctionnalités :
- Sélection de deux équipes (domicile et extérieur)
- Calcul de la probabilité de victoire pour chaque équipe
- Affichage visuel du gagnant prédit avec les probabilités
"""

import streamlit as st
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION DES IMPORTS
# ============================================================================
# Ajouter le répertoire parent au path Python pour pouvoir importer utils.py
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import des fonctions utilitaires depuis utils.py
from utils import load_match_model, load_boxscores_data, predict_match_live

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
st.set_page_config(
    page_title="Prédiction Match",
    page_icon="⚔️",
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
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EN-TÊTE DE LA PAGE
# ============================================================================
# Titre principal de la page
st.markdown('<h1 class="section-header">⚔️ Prédiction du Gagnant d\'un Match</h1>', unsafe_allow_html=True)

# Bouton de navigation pour retourner à la page d'accueil
if st.button("← Retour à l'accueil"):
    st.switch_page("app.py")

st.markdown("---")  # Séparateur horizontal

# ============================================================================
# CHARGEMENT DES DONNÉES ET MODÈLE
# ============================================================================
# Chargement du modèle de match pré-entraîné et des données des boxscores
# Affichage d'un spinner pendant le chargement
with st.spinner("Chargement des données..."):
    match_model = load_match_model()
    df_boxscores = load_boxscores_data()

# Vérification que le modèle et les données ont été chargés correctement
if match_model is None or df_boxscores is None:
    st.error("❌ Impossible de charger les données nécessaires.")
    st.stop()  # Arrêter l'exécution si les données ne sont pas disponibles

# ============================================================================
# CONFIGURATION DES FEATURES
# ============================================================================
# Liste des features utilisées par le modèle de match
# Ces features correspondent à celles utilisées lors de l'entraînement du modèle
match_features = [
    'Home_Rolling_WinRate',    # Taux de victoire récent de l'équipe à domicile
    'Away_Rolling_WinRate',    # Taux de victoire récent de l'équipe à l'extérieur
    'Home_RestAdv'             # Avantage du repos (non utilisé pour l'instant)
]

# ============================================================================
# RÉCUPÉRATION DE LA LISTE DES ÉQUIPES
# ============================================================================
# Extraire toutes les équipes uniques des données (domicile et extérieur)
# et créer une liste triée pour les selectbox
try:
    home_teams = sorted(df_boxscores['HomeTeam'].unique().tolist())
    away_teams = sorted(df_boxscores['AwayTeam'].unique().tolist())
    # Combiner les deux listes et supprimer les doublons
    all_teams = sorted(list(set(home_teams + away_teams)))
except:
    all_teams = []

if not all_teams:
    st.error("❌ Impossible de charger la liste des équipes")
    st.stop()

# ============================================================================
# INTERFACE DE SÉLECTION DES ÉQUIPES
# ============================================================================
# Création de deux colonnes pour les selectbox
col1, col2 = st.columns(2)

with col1:
    # Selectbox pour choisir l'équipe à domicile
    home_team = st.selectbox(
        "🏠 Équipe à domicile",
        all_teams,
        key="home_team"
    )

with col2:
    # Selectbox pour choisir l'équipe à l'extérieur
    # Filtrer pour exclure l'équipe à domicile déjà sélectionnée
    away_team = st.selectbox(
        "✈️ Équipe à l'extérieur",
        [t for t in all_teams if t != home_team],
        key="away_team"
    )

# ============================================================================
# INITIALISATION DE LA SESSION STATE
# ============================================================================
# Initialiser la session state pour stocker les résultats de la prédiction
# Cela permet de conserver l'affichage même après une réexécution du script
if 'match_result' not in st.session_state:
    st.session_state.match_result = None
if 'match_home_team' not in st.session_state:
    st.session_state.match_home_team = None
if 'match_away_team' not in st.session_state:
    st.session_state.match_away_team = None

# ============================================================================
# BOUTON DE PRÉDICTION ET AFFICHAGE DES RÉSULTATS
# ============================================================================
# Bouton principal pour lancer la prédiction
if st.button("Prédire le gagnant", type="primary", use_container_width=True):
    # Vérification que deux équipes différentes sont sélectionnées
    if home_team == away_team:
        st.error("❌ Veuillez sélectionner deux équipes différentes")
        st.session_state.match_result = None
    else:
        # Calcul de la prédiction avec affichage d'un spinner
        with st.spinner("Calcul de la prédiction..."):
            try:
                # Appel de la fonction de prédiction
                result = predict_match_live(
                    home_team,
                    away_team,
                    df_boxscores,
                    match_model,
                    match_features
                )
                
                # Vérification que la prédiction a réussi
                if result is None:
                    st.error("❌ Pas assez de données historiques pour l'une des équipes.")
                    st.session_state.match_result = None
                else:
                    # Stocker les résultats dans la session state
                    st.session_state.match_result = result
                    st.session_state.match_home_team = home_team
                    st.session_state.match_away_team = away_team
            
            except Exception as e:
                # Gestion des erreurs lors de la prédiction
                st.error(f"❌ Erreur lors de la prédiction : {e}")
                st.session_state.match_result = None

# ============================================================================
# AFFICHAGE DES RÉSULTATS (si disponibles)
# ============================================================================
# Afficher les résultats s'ils sont disponibles dans la session state
if st.session_state.match_result is not None:
    result = st.session_state.match_result
    home_team_display = st.session_state.match_home_team
    away_team_display = st.session_state.match_away_team
    
    # Extraction des résultats
    winner = result["winner"]
    proba_home = result["proba_home"]
    proba_away = 1 - proba_home  # Probabilité complémentaire
    
    # Affichage du résultat
    st.markdown("### Résultat de la prédiction")
    
    # Création de 3 colonnes pour afficher les deux équipes et "VS"
    col1, col2, col3 = st.columns([2, 1, 2])
    
    # Colonne équipe à domicile
    with col1:
        # Carte avec style conditionnel : vert si gagnant, gris avec meilleur contraste sinon
        is_winner = winner == home_team_display
        bg_color = '#d4edda' if is_winner else '#e9ecef'
        border_color = '#28a745' if is_winner else '#adb5bd'
        border_width = '3px' if is_winner else '2px'
        text_color = '#28a745' if is_winner else '#495057'
        title_color = '#155724' if is_winner else '#212529'
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border: {border_width} solid {border_color};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; text-align: center; color: {title_color}; font-weight: bold;">{home_team_display}</h3>
        </div>
        """, unsafe_allow_html=True)
        # Afficher le statut (gagnant ou perdant) sans pourcentage
        status_text = "🏆 Gagnant" if is_winner else "⚪ Perdant"
        status_color = '#28a745' if is_winner else '#6c757d'
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; margin-top: 0.5rem;">
            <p style="color: {status_color}; font-weight: bold; margin: 0;">{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Colonne centrale avec "VS"
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="margin: 0; color: #6c757d;">VS</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Colonne équipe à l'extérieur
    with col3:
        # Carte avec style conditionnel : vert si gagnant, gris avec meilleur contraste sinon
        is_winner = winner == away_team_display
        bg_color = '#d4edda' if is_winner else '#e9ecef'
        border_color = '#28a745' if is_winner else '#adb5bd'
        border_width = '3px' if is_winner else '2px'
        text_color = '#28a745' if is_winner else '#495057'
        title_color = '#155724' if is_winner else '#212529'
        
        st.markdown(f"""
        <div style="background-color: {bg_color}; 
                    padding: 1.5rem; 
                    border-radius: 10px; 
                    border: {border_width} solid {border_color};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; text-align: center; color: {title_color}; font-weight: bold;">{away_team_display}</h3>
         
        </div>
        """, unsafe_allow_html=True)
        # Afficher le statut (gagnant ou perdant) sans pourcentage
        status_text = "🏆 Gagnant" if is_winner else "⚪ Perdant"
        status_color = '#28a745' if is_winner else '#6c757d'
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; margin-top: 0.5rem;">
            <p style="color: {status_color}; font-weight: bold; margin: 0;">{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Message de résultat avec le gagnant (sans pourcentage)
    st.markdown(f"""
    <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
        <h3 style="color: #856404; margin: 0;">🏆 Gagnant Prédit</h3>
        <p style="color: #856404; margin: 0.5rem 0 0 0;">
            <strong>{winner}</strong> est prédit comme gagnant !
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton pour effacer les résultats
    if st.button("🔄 Nouvelle prédiction", type="secondary"):
        st.session_state.match_result = None
        st.session_state.match_home_team = None
        st.session_state.match_away_team = None
        st.rerun()

