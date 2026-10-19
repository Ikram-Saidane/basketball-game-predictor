"""
Page de prédiction Champion - Équipe Championne 2025-2026

Cette page affiche la prédiction de l'équipe championne NBA pour la saison 2025-2026.
Elle utilise un modèle LightGBM pour prédire quelle équipe a le plus de chances
de remporter le championnat.

Fonctionnalités :
- Affichage de l'équipe championne prédite avec son abréviation
- Affichage de la probabilité de victoire
- Message de félicitations pour l'équipe prédite
"""

import streamlit as st
import sys
import html
from pathlib import Path

# ============================================================================
# CONFIGURATION DES IMPORTS
# ============================================================================
# Ajouter le répertoire parent au path Python pour pouvoir importer utils.py
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import des fonctions utilitaires depuis utils.py
from utils import load_teams_data, predict_champion_2025_2026

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
st.set_page_config(
    page_title="Prédiction Champion",
    page_icon="🥇",
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
.team-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
    margin-bottom: 1rem;
}
.team-card h2 {
    color: #ffffff !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    font-weight: bold;
}
.team-card p {
    color: #ffffff !important;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# EN-TÊTE DE LA PAGE
# ============================================================================
# Titre principal de la page
st.markdown('<h1 class="section-header">🥇 Prédiction Équipe Championne 2025-2026</h1>', unsafe_allow_html=True)

# Bouton de navigation pour retourner à la page d'accueil
if st.button("← Retour à l'accueil"):
    st.switch_page("app.py")

st.markdown("---")  # Séparateur horizontal

# ============================================================================
# CHARGEMENT DES DONNÉES
# ============================================================================
# Chargement des données des équipes
# Affichage d'un spinner pendant le chargement
with st.spinner("Chargement des données..."):
    df_teams = load_teams_data()

# Vérification que les données ont été chargées correctement
if df_teams is None:
    st.error("❌ Impossible de charger les données nécessaires.")
    st.stop()  # Arrêter l'exécution si les données ne sont pas disponibles

# ============================================================================
# PRÉDICTION DU CHAMPION
# ============================================================================
# Calcul de la prédiction du champion pour la saison 2025-2026
# La fonction retourne le nom de l'équipe, son abréviation et sa probabilité
try:
    with st.spinner("Calcul de la prédiction..."):
        champ_team, champ_abbr, champ_proba = predict_champion_2025_2026(df_teams)
    
    # Carte principale affichant l'équipe championne prédite
    # Utilisation d'un style CSS personnalisé avec dégradé de couleurs
    # Échapper les caractères HTML pour éviter l'affichage de balises
    champ_team_escaped = html.escape(str(champ_team))
    champ_abbr_escaped = html.escape(str(champ_abbr))
    
    st.markdown(f"""
    <div class="team-card">
        <h2 style="margin: 0; font-size: 2.5rem; color: #ffffff; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7); font-weight: bold;">🥇 {champ_team_escaped}</h2>
        <p style="font-size: 1.3rem; margin-top: 0.5rem; color: #ffffff; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);">
            <strong>Abréviation:</strong> {champ_abbr_escaped}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Message de félicitations avec style de succès (vert)
    # Échapper le nom de l'équipe pour éviter les problèmes d'affichage
    st.markdown(f"""
    <div style="background-color: #d4edda; border-left: 5px solid #28a745; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
        <h3 style="color: #155724; margin: 0;">🎉 Champion Prédit</h3>
        <p style="color: #155724; margin: 0.5rem 0 0 0;">
            L'équipe <strong>{champ_team_escaped}</strong> est prédite comme championne NBA 2025-2026 !
        </p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    # Gestion des erreurs lors de la prédiction
    st.error(f"❌ Erreur lors de la prédiction du champion : {e}")


