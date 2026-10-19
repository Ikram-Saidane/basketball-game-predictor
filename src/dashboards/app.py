"""
Dashboard Streamlit - Page principale

Cette page sert de point d'entrée principal pour le dashboard NBA.
Elle affiche :
- Des statistiques générales sur les données (joueurs, équipes, matchs)
- Des analyses détaillées par catégorie (onglets Joueurs, Matchs, Équipes)
- Des visualisations graphiques
- Des boutons de navigation vers les pages de prédiction (MVP, Champion, Match)

Architecture :
- Multi-page Streamlit app : cette page est la page principale (app.py)
- Les pages de prédiction sont dans le dossier pages/
- Les fonctions utilitaires sont dans utils.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Tentative d'import de Plotly pour des graphiques avancés
# Si Plotly n'est pas disponible, on utilisera les graphiques natifs de Streamlit
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
# Configuration de la page Streamlit (titre, icône, layout)
st.set_page_config(
    page_title="Dashboard NBA - Accueil",
    page_icon="🏀",
    layout="wide",  # Layout large pour utiliser toute la largeur de l'écran
    initial_sidebar_state="expanded"  # Sidebar ouverte par défaut
)

# ============================================================================
# CONFIGURATION DES CHEMINS
# ============================================================================
# Définition des chemins relatifs pour accéder aux fichiers de données
# BASE_DIR pointe vers la racine du projet (3 niveaux au-dessus de ce fichier)
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "features"

# Chemins des fichiers CSV contenant les données features
PLAYERS_DATA_PATH = DATA_DIR / "nba_players_features.csv"
TEAMS_DATA_PATH = DATA_DIR / "nba_teams_features.csv"
BOXSCORES_DATA_PATH = DATA_DIR / "nba_boxscores_features.csv"


# ============================================================================
# FONCTIONS DE CHARGEMENT DES DONNÉES
# ============================================================================
# @st.cache_data : Décorateur Streamlit qui met en cache les résultats
# Cela évite de recharger les données à chaque interaction utilisateur

@st.cache_data
def load_players_data():
    """
    Charge les données des joueurs depuis le fichier CSV
    
    Les données sont mises en cache par Streamlit pour améliorer les performances.
    
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


@st.cache_data
def load_teams_data():
    """
    Charge les données des équipes depuis le fichier CSV
    
    Les données sont mises en cache par Streamlit pour améliorer les performances.
    
    Returns:
        DataFrame ou None: DataFrame pandas avec les données des équipes,
                          ou None en cas d'erreur de chargement
    """
    try:
        return pd.read_csv(TEAMS_DATA_PATH)
    except Exception as e:
        return None


@st.cache_data
def load_boxscores_data():
    """
    Charge les données des boxscores (résultats de matchs) depuis le fichier CSV
    
    Les données sont mises en cache par Streamlit pour améliorer les performances.
    La colonne Date est convertie en datetime pour faciliter les opérations temporelles.
    
    Returns:
        DataFrame ou None: DataFrame pandas avec les données des matchs,
                          ou None en cas d'erreur de chargement
    """
    try:
        df = pd.read_csv(BOXSCORES_DATA_PATH)
        # Conversion de la colonne Date en datetime
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except Exception as e:
        return None


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """
    Fonction principale de la page d'accueil
    
    Cette fonction orchestre l'affichage de toute la page :
    1. Application des styles CSS personnalisés
    2. Chargement des données
    3. Affichage des statistiques générales
    4. Affichage des statistiques détaillées par onglets
    5. Affichage des visualisations graphiques
    6. Affichage des boutons de navigation vers les prédictions
    """
    
    # ========================================================================
    # STYLES CSS PERSONNALISÉS
    # ========================================================================
    # Définition de styles CSS pour améliorer l'apparence du dashboard
    # Les styles sont injectés dans le HTML via st.markdown avec unsafe_allow_html=True
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .nav-button {
        background: linear-gradient(135deg, #d35400 0%, #e67e22 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        text-decoration: none;
        display: block;
        transition: transform 0.2s;
        box-shadow: 0 4px 6px rgba(211, 84, 0, 0.3);
    }
    .nav-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 8px rgba(211, 84, 0, 0.4);
    }
    /* Style pour les boutons Streamlit de navigation */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #d35400 0%, #e67e22 100%);
        border: none;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(211, 84, 0, 0.3);
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #a04000 0%, #d35400 100%);
        box-shadow: 0 6px 8px rgba(211, 84, 0, 0.4);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ========================================================================
    # EN-TÊTE DE LA PAGE
    # ========================================================================
    # Titre principal du dashboard avec style CSS personnalisé
    st.markdown('<h1 class="main-header">🏀 Dashboard Prédictions NBA</h1>', unsafe_allow_html=True)
    st.markdown("---")  # Séparateur horizontal
    
    # ========================================================================
    # CHARGEMENT DES DONNÉES
    # ========================================================================
    # Affichage d'un spinner pendant le chargement pour indiquer à l'utilisateur
    # que l'application est en train de charger les données
    with st.spinner("Chargement des données..."):
        df_players = load_players_data()
        df_teams = load_teams_data()
        df_boxscores = load_boxscores_data()
    
    # Vérification que toutes les données ont été chargées correctement
    # Si une des données est None, afficher une erreur et arrêter l'exécution
    if any(x is None for x in [df_players, df_teams, df_boxscores]):
        st.error("❌ Impossible de charger les données. Vérifiez les chemins des fichiers.")
        return
    
    # ========================================================================
    # STATISTIQUES GÉNÉRALES (VUE D'ENSEMBLE)
    # ========================================================================
    # Section affichant les 4 métriques principales dans des cartes colorées
    st.markdown("## Vue d'ensemble des Données")
    
    # Statistiques principales avec style
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin: 0; font-size: 2.5rem;">{:,}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Total Joueurs</p>
        </div>
        """.format(len(df_players)), unsafe_allow_html=True)
    
    with col2:
        unique_players = df_players['Player'].nunique() if 'Player' in df_players.columns else 0
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin: 0; font-size: 2.5rem;">{:,}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Joueurs Uniques</p>
        </div>
        """.format(unique_players), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin: 0; font-size: 2.5rem;">{:,}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Total Équipes</p>
        </div>
        """.format(len(df_teams)), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                    padding: 1.5rem; border-radius: 10px; text-align: center; color: white;">
            <h3 style="margin: 0; font-size: 2.5rem;">{:,}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">Total Matchs</p>
        </div>
        """.format(len(df_boxscores)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # STATISTIQUES DÉTAILLÉES PAR ONGLETS
    # ========================================================================
    # Utilisation de st.tabs pour organiser les statistiques détaillées
    # Chaque onglet contient des analyses spécifiques à une catégorie
    tab1, tab2, tab3 = st.tabs(["👥 Joueurs", "🏀 Matchs", "🏆 Équipes"])
    
    with tab1:
        st.markdown("### 📈 Statistiques Détaillées des Joueurs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Season' in df_players.columns:
                seasons = sorted(df_players['Season'].unique(), reverse=True)
                st.markdown("**Informations sur les Saisons**")
                st.metric("Nombre de saisons", len(seasons))
                st.write(f"**Dernière saison :** {seasons[0] if seasons else 'N/A'}")
                st.write(f"**Première saison :** {seasons[-1] if seasons else 'N/A'}")
                st.write(f"**Période :** {seasons[-1] if seasons else 'N/A'} - {seasons[0] if seasons else 'N/A'}")
            
            if 'Team' in df_players.columns:
                teams_count = df_players['Team'].nunique()
                st.markdown("**🏀 Informations sur les Équipes**")
                st.metric("Équipes représentées", teams_count)
                
                # Top 5 équipes par nombre de joueurs
                top_teams = df_players['Team'].value_counts().head(5)
                st.markdown("**Top 5 équipes (par nombre de joueurs)**")
                for team, count in top_teams.items():
                    st.write(f"- {team}: {count} joueurs")
        
        with col2:
            if 'PTS' in df_players.columns:
                st.markdown("**Statistiques de Performance**")
                avg_pts = df_players['PTS'].mean()
                max_pts = df_players['PTS'].max()
                median_pts = df_players['PTS'].median()
                std_pts = df_players['PTS'].std()
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Points moyens", f"{avg_pts:.1f}")
                    st.metric("Médiane", f"{median_pts:.1f}")
                with col_b:
                    st.metric("Record", f"{max_pts:.0f}")
                    st.metric("Écart-type", f"{std_pts:.1f}")
                
                # Meilleur marqueur
                if 'Player' in df_players.columns:
                    best_scorer = df_players.loc[df_players['PTS'].idxmax(), 'Player'] if not df_players.empty else 'N/A'
                    st.write(f"**🏆 Meilleur marqueur :** {best_scorer} ({max_pts:.0f} pts)")
            
            if 'AST' in df_players.columns:
                st.markdown("**🎯 Passes Décisives**")
                max_ast = df_players['AST'].max()
                avg_ast = df_players['AST'].mean()
                median_ast = df_players['AST'].median()
                col_ast1, col_ast2 = st.columns(2)
                with col_ast1:
                    st.metric("Moyenne", f"{avg_ast:.1f}")
                    st.metric("Médiane", f"{median_ast:.1f}")
                with col_ast2:
                    st.metric("Record", f"{max_ast:.0f}")
                    if 'Player' in df_players.columns:
                        best_passer = df_players.loc[df_players['AST'].idxmax(), 'Player'] if not df_players.empty else 'N/A'
                        st.caption(f"Par: {best_passer}")
            
            if 'TRB' in df_players.columns:
                st.markdown("**🏀 Rebonds**")
                max_reb = df_players['TRB'].max()
                avg_reb = df_players['TRB'].mean()
                median_reb = df_players['TRB'].median()
                col_reb1, col_reb2 = st.columns(2)
                with col_reb1:
                    st.metric("Moyenne", f"{avg_reb:.1f}")
                    st.metric("Médiane", f"{median_reb:.1f}")
                with col_reb2:
                    st.metric("Record", f"{max_reb:.0f}")
                    if 'Player' in df_players.columns:
                        best_rebounder = df_players.loc[df_players['TRB'].idxmax(), 'Player'] if not df_players.empty else 'N/A'
                        st.caption(f"Par: {best_rebounder}")
    
    with tab2:
        st.markdown("### 🏀 Statistiques Détaillées des Matchs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Date' in df_boxscores.columns:
                st.markdown("**Période de Données**")
                min_date = df_boxscores['Date'].min()
                max_date = df_boxscores['Date'].max()
                date_range_days = (max_date - min_date).days
                st.metric("Période couverte", f"{date_range_days} jours")
                st.write(f"**Du :** {min_date.strftime('%d/%m/%Y')}")
                st.write(f"**Au :** {max_date.strftime('%d/%m/%Y')}")
                
                # Matchs par année
                df_boxscores['Year'] = df_boxscores['Date'].dt.year
                matches_per_year = df_boxscores['Year'].value_counts().sort_index()
                st.markdown("**Matchs par année**")
                st.bar_chart(matches_per_year)
        
        with col2:
            if 'HomeTeam' in df_boxscores.columns and 'AwayTeam' in df_boxscores.columns:
                unique_teams = len(set(df_boxscores['HomeTeam'].unique().tolist() + df_boxscores['AwayTeam'].unique().tolist()))
                st.markdown("**🏆 Informations sur les Équipes**")
                st.metric("Équipes uniques", unique_teams)
                
                # Équipe la plus active
                all_teams_list = df_boxscores['HomeTeam'].tolist() + df_boxscores['AwayTeam'].tolist()
                team_counts = pd.Series(all_teams_list).value_counts()
                if len(team_counts) > 0:
                    most_active = team_counts.index[0]
                    st.write(f"**Équipe la plus active :** {most_active} ({team_counts.iloc[0]} matchs)")
                
                # Top 5 équipes les plus actives
                with st.expander("🏀 Top 5 Équipes les Plus Actives"):
                    top_5_teams = team_counts.head(5)
                    for idx, (team, count) in enumerate(top_5_teams.items(), 1):
                        st.write(f"{idx}. **{team}** : {count} matchs")
            
            if 'HomePts' in df_boxscores.columns and 'AwayPts' in df_boxscores.columns:
                st.markdown("**Statistiques de Points**")
                avg_home_pts = df_boxscores['HomePts'].mean()
                avg_away_pts = df_boxscores['AwayPts'].mean()
                total_avg = (avg_home_pts + avg_away_pts) / 2
                home_advantage = avg_home_pts - avg_away_pts
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Moyenne (domicile)", f"{avg_home_pts:.1f}")
                    st.metric("Moyenne (extérieur)", f"{avg_away_pts:.1f}")
                with col_b:
                    st.metric("Moyenne totale", f"{total_avg:.1f}")
                    st.metric("Avantage domicile", f"+{home_advantage:.1f}")
                
                # Record de points
                max_home_pts = df_boxscores['HomePts'].max()
                max_away_pts = df_boxscores['AwayPts'].max()
                max_total = df_boxscores['HomePts'].max() + df_boxscores['AwayPts'].max()
                st.write(f"**Record domicile :** {max_home_pts:.0f} pts")
                st.write(f"**Record extérieur :** {max_away_pts:.0f} pts")
                st.write(f"**Record total match :** {max_total:.0f} pts")
    
    with tab3:
        st.markdown("### 🏆 Statistiques Détaillées des Équipes")
        
        if 'Team' in df_teams.columns:
            # Statistiques sur les équipes avec graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                if 'AllTime_WinRate' in df_teams.columns:
                    st.markdown("**Taux de Victoire par Équipe**")
                    # Préparer les données pour le graphique
                    winrate_data = df_teams.groupby('Team')['AllTime_WinRate'].mean().sort_values(ascending=False).head(15) * 100
                    
                    if PLOTLY_AVAILABLE and len(winrate_data) > 0:
                        fig = px.bar(
                            x=winrate_data.values,
                            y=winrate_data.index,
                            orientation='h',
                            title="Top 15 Équipes par Taux de Victoire",
                            labels={'x': 'Taux de Victoire (%)', 'y': 'Équipe'}
                        )
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    elif len(winrate_data) > 0:
                        st.bar_chart(winrate_data, height=400)
                    
                    # Métriques résumées
                    avg_winrate = df_teams['AllTime_WinRate'].mean() * 100
                    max_winrate = df_teams['AllTime_WinRate'].max() * 100
                    best_team = df_teams.loc[df_teams['AllTime_WinRate'].idxmax(), 'Team'] if not df_teams.empty else 'N/A'
                    st.metric("Taux de victoire moyen", f"{avg_winrate:.1f}%")
                    st.metric("Meilleur taux", f"{max_winrate:.1f}%")
                    st.write(f"**Meilleure équipe :** {best_team}")
            
            with col2:
                if 'Champ_Rate' in df_teams.columns:
                    st.markdown("**Taux de Championnat par Équipe**")
                    # Préparer les données pour le graphique
                    champ_rate_data = df_teams.groupby('Team')['Champ_Rate'].mean().sort_values(ascending=False).head(15) * 100
                    
                    if PLOTLY_AVAILABLE and len(champ_rate_data) > 0:
                        fig = px.bar(
                            x=champ_rate_data.values,
                            y=champ_rate_data.index,
                            orientation='h',
                            title="Top 15 Équipes par Taux de Championnat",
                            labels={'x': 'Taux de Championnat (%)', 'y': 'Équipe'},
                            color=champ_rate_data.values,
                            color_continuous_scale='YlOrRd'
                        )
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    elif len(champ_rate_data) > 0:
                        st.bar_chart(champ_rate_data, height=400)
                    
                    # Métrique résumée
                    avg_champ_rate = df_teams['Champ_Rate'].mean() * 100
                    st.metric("Taux de championnat moyen", f"{avg_champ_rate:.2f}%")
            
            # Liste des équipes dans un expander
            with st.expander("📋 Liste Complète des Équipes", expanded=False):
                if 'Abbreviation' in df_teams.columns:
                    teams_display = df_teams[['Team', 'Abbreviation']].drop_duplicates().sort_values('Team')
                    st.dataframe(teams_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ========================================================================
    # NAVIGATION VERS LES PAGES DE PRÉDICTION
    # ========================================================================
    # Section avec 3 boutons de navigation vers les pages de prédiction
    # Chaque bouton utilise st.switch_page pour naviguer vers la page correspondante
    st.markdown("## 🎯 Accéder aux Prédictions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-button">
            <h2>🏆 MVP</h2>
            <p>Prédiction du meilleur joueur</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Voir la prédiction MVP", use_container_width=True, type="primary"):
            st.switch_page("pages/1_MVP_Prediction.py")
    
    with col2:
        st.markdown("""
        <div class="nav-button">
            <h2>🥇 Champion</h2>
            <p>Prédiction de l'équipe championne</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Voir la prédiction Champion", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Champion_Prediction.py")
    
    with col3:
        st.markdown("""
        <div class="nav-button">
            <h2>⚔️ Match</h2>
            <p>Prédiction du gagnant d'un match</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Voir la prédiction Match", use_container_width=True, type="primary"):
            st.switch_page("pages/3_Match_Prediction.py")
    
    st.markdown("---")
    
    # ========================================================================
    # VISUALISATIONS GRAPHIQUES ET ANALYSES
    # ========================================================================
    # Section contenant des graphiques et analyses visuelles des données
    # Utilisation de Plotly si disponible, sinon fallback sur les graphiques Streamlit
    st.markdown("## Visualisations et Analyses")
    
    # Création de 2 colonnes pour afficher les graphiques côte à côte
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Season' in df_players.columns:
            st.markdown("### Distribution des Joueurs par Saison")
            season_counts = df_players['Season'].value_counts().sort_index()
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(
                    x=season_counts.index,
                    y=season_counts.values,
                    title="Nombre de Joueurs par Saison",
                    labels={'x': 'Saison', 'y': 'Nombre de Joueurs'}
                )
                fig.update_layout(height=300, showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(season_counts, height=300)
            
            # Statistiques supplémentaires
            with st.expander("📈 Détails par saison", expanded=False):
                if 'PTS' in df_players.columns:
                    season_stats = df_players.groupby('Season').agg({
                        'PTS': ['mean', 'max', 'sum'],
                        'Player': 'count'
                    }).round(1)
                    season_stats.columns = ['PTS Moyens', 'PTS Max', 'PTS Total', 'Nb Joueurs']
                    st.dataframe(season_stats, use_container_width=True)
    
    with col2:
        if 'Team' in df_players.columns:
            st.markdown("### 🏀 Top 10 Équipes (par nombre de joueurs)")
            team_counts = df_players['Team'].value_counts().head(10)
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(
                    x=team_counts.values,
                    y=team_counts.index,
                    orientation='h',
                    title="Top 10 Équipes",
                    labels={'x': 'Nombre de Joueurs', 'y': 'Équipe'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(team_counts, height=300)
            
            # Tableau détaillé
            with st.expander("Détails des équipes", expanded=False):
                if 'PTS' in df_players.columns:
                    team_details = df_players.groupby('Team').agg({
                        'PTS': ['mean', 'max', 'sum'],
                        'Player': 'count'
                    }).round(1)
                    team_details.columns = ['PTS Moyens', 'PTS Max', 'PTS Total', 'Nb Joueurs']
                    team_details = team_details.sort_values('Nb Joueurs', ascending=False).head(15)
                    st.dataframe(
                        team_details.style.background_gradient(subset=['PTS Moyens', 'PTS Total'], cmap='YlOrRd'),
                        use_container_width=True
                    )
    
    st.markdown("---")
    
    # ========================================================================
    # GRAPHIQUES STATIQUES SUPPLÉMENTAIRES
    # ========================================================================
    st.markdown("## 📊 Graphiques Statistiques")
    
    # Graphique 1 : Distribution des points des joueurs
    col1, col2 = st.columns(2)
    
    with col1:
        if 'PTS' in df_players.columns:
            st.markdown("### Distribution des Points des Joueurs")
            # Exclure les valeurs aberrantes et "League Average"
            df_players_clean = df_players[~df_players['Player'].astype(str).str.contains('League Average', case=False, na=False)]
            pts_clean = df_players_clean['PTS'].dropna()
            
            if PLOTLY_AVAILABLE and len(pts_clean) > 0:
                fig = px.histogram(
                    x=pts_clean,
                    nbins=30,
                    title="Distribution des Points",
                    labels={'x': 'Points', 'count': 'Nombre de Joueurs'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            elif len(pts_clean) > 0:
                # Convertir les intervalles en strings pour st.bar_chart
                bins_data = pd.cut(pts_clean, bins=20).value_counts().sort_index()
                bins_data.index = bins_data.index.astype(str)
                st.bar_chart(bins_data, height=300)
    
    with col2:
        if 'AST' in df_players.columns:
            st.markdown("### Distribution des Passes Décisives")
            df_players_clean = df_players[~df_players['Player'].astype(str).str.contains('League Average', case=False, na=False)]
            ast_clean = df_players_clean['AST'].dropna()
            
            if PLOTLY_AVAILABLE and len(ast_clean) > 0:
                fig = px.histogram(
                    x=ast_clean,
                    nbins=30,
                    title="Distribution des Passes Décisives",
                    labels={'x': 'Passes Décisives', 'count': 'Nombre de Joueurs'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            elif len(ast_clean) > 0:
                # Convertir les intervalles en strings pour st.bar_chart
                bins_data = pd.cut(ast_clean, bins=20).value_counts().sort_index()
                bins_data.index = bins_data.index.astype(str)
                st.bar_chart(bins_data, height=300)
    
    # Graphique 2 : Évolution des moyennes par saison
    st.markdown("### Évolution des Statistiques par Saison")
    if 'Season' in df_players.columns and 'PTS' in df_players.columns:
        df_players_clean = df_players[~df_players['Player'].astype(str).str.contains('League Average', case=False, na=False)]
        season_stats = df_players_clean.groupby('Season').agg({
            'PTS': 'mean',
            'AST': 'mean',
            'TRB': 'mean'
        }).reset_index()
        
        if PLOTLY_AVAILABLE and len(season_stats) > 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=season_stats['Season'],
                y=season_stats['PTS'],
                mode='lines+markers',
                name='Points moyens',
                line=dict(color='#1f77b4', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=season_stats['Season'],
                y=season_stats['AST'],
                mode='lines+markers',
                name='Passes moyennes',
                line=dict(color='#ff7f0e', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=season_stats['Season'],
                y=season_stats['TRB'],
                mode='lines+markers',
                name='Rebonds moyens',
                line=dict(color='#2ca02c', width=2)
            ))
            fig.update_layout(
                title="Évolution des Moyennes par Saison",
                xaxis_title="Saison",
                yaxis_title="Moyenne",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        elif len(season_stats) > 0:
            st.line_chart(season_stats.set_index('Season'), height=400)
    

    # Graphique 4 : Boxplot des statistiques principales
    if 'PTS' in df_players.columns and 'AST' in df_players.columns and 'TRB' in df_players.columns:
        st.markdown("### Comparaison des Statistiques Principales")
        df_players_clean = df_players[~df_players['Player'].astype(str).str.contains('League Average', case=False, na=False)]
        
        if PLOTLY_AVAILABLE:
            # Créer un DataFrame pour le boxplot
            stats_data = pd.DataFrame({
                'Points': df_players_clean['PTS'].dropna().head(1000),  # Limiter pour performance
                'Passes': df_players_clean['AST'].dropna().head(1000),
                'Rebonds': df_players_clean['TRB'].dropna().head(1000)
            })
            
            fig = go.Figure()
            for col in stats_data.columns:
                fig.add_trace(go.Box(
                    y=stats_data[col],
                    name=col,
                    boxmean='sd'
                ))
            fig.update_layout(
                title="Distribution des Statistiques Principales",
                yaxis_title="Valeur",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # ANALYSES SUPPLÉMENTAIRES
    # ========================================================================
    # Section avec des analyses complémentaires (top 10 marqueurs, distribution des points)
    col1, col2 = st.columns(2)
    
    with col1:
        if 'PTS' in df_players.columns and 'Player' in df_players.columns:
            st.markdown("### 🏆 Top 10 Meilleurs Marqueurs (Tous Temps)")
            
            # Exclure "League Average"
            df_players_clean = df_players[~df_players['Player'].astype(str).str.contains('League Average', case=False, na=False)]
            top_scorers = df_players_clean.nlargest(10, 'PTS')
            
            if not top_scorers.empty:
                display_cols = ['Player', 'PTS']
                if 'Team' in top_scorers.columns:
                    display_cols.append('Team')
                if 'Season' in top_scorers.columns:
                    display_cols.append('Season')
                
                top_scorers_display = top_scorers[display_cols].copy()
                top_scorers_display['Rang'] = range(1, len(top_scorers_display) + 1)
                top_scorers_display = top_scorers_display[['Rang'] + display_cols]
                
                st.dataframe(
                    top_scorers_display.style.background_gradient(subset=['PTS'], cmap='YlOrRd'),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Afficher le meilleur marqueur en évidence
                best = top_scorers.iloc[0]
                st.success(f"🏆 **Meilleur marqueur :** {best['Player']} avec {best['PTS']:.0f} points ({best.get('Season', 'N/A')})")
    
    with col2:
        if 'HomePts' in df_boxscores.columns and 'AwayPts' in df_boxscores.columns:
            st.markdown("###Distribution des Points par Match")
            df_boxscores['TotalPts'] = df_boxscores['HomePts'] + df_boxscores['AwayPts']
            
            # Histogramme
            if PLOTLY_AVAILABLE:
                fig = px.histogram(
                    df_boxscores, 
                    x='TotalPts',
                    nbins=30,
                    title="Distribution des Points Totaux par Match",
                    labels={'TotalPts': 'Points Totaux', 'count': 'Nombre de Matchs'}
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback avec bar_chart de Streamlit - convertir les intervalles en strings
                hist_data = pd.cut(df_boxscores['TotalPts'], bins=20).value_counts().sort_index()
                hist_data.index = hist_data.index.astype(str)
                st.bar_chart(hist_data, height=300)
            
            # Statistiques
            avg_total = df_boxscores['TotalPts'].mean()
            median_total = df_boxscores['TotalPts'].median()
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Moyenne", f"{avg_total:.1f}")
            with col_b:
                st.metric("Médiane", f"{median_total:.1f}")
    
    st.markdown("---")


if __name__ == "__main__":
    main()