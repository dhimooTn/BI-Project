from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from gestionnaire import db_manager

# --- 1. CHARGEMENT INITIAL (Pour les listes déroulantes) ---
df = db_manager.get_all_data()

if df.empty:
    liste_entreprises = []
    unique_clusters = []
    columns_list = [{"name": i, "id": i} for i in ["emploi", "entreprise", "salaire_annuel"]]
else:
    liste_entreprises = sorted(df['entreprise'].dropna().unique().tolist()) if 'entreprise' in df.columns else []
    unique_clusters = sorted(df['cluster'].dropna().unique().tolist()) if 'cluster' in df.columns else []
    columns_list = [{"name": i, "id": i} for i in df.columns]

# --- 2. MAPPING COMPLET (Départements -> Régions) ---
# Indispensable pour que la carte fonctionne sur toute la France
DEPT_TO_REGION = {
    # Auvergne-Rhône-Alpes
    '01': 'Auvergne-Rhône-Alpes', '03': 'Auvergne-Rhône-Alpes', '07': 'Auvergne-Rhône-Alpes',
    '15': 'Auvergne-Rhône-Alpes', '26': 'Auvergne-Rhône-Alpes', '38': 'Auvergne-Rhône-Alpes',
    '42': 'Auvergne-Rhône-Alpes', '43': 'Auvergne-Rhône-Alpes', '63': 'Auvergne-Rhône-Alpes',
    '69': 'Auvergne-Rhône-Alpes', '73': 'Auvergne-Rhône-Alpes', '74': 'Auvergne-Rhône-Alpes',
    # Bourgogne-Franche-Comté
    '21': 'Bourgogne-Franche-Comté', '25': 'Bourgogne-Franche-Comté', '39': 'Bourgogne-Franche-Comté',
    '58': 'Bourgogne-Franche-Comté', '70': 'Bourgogne-Franche-Comté', '71': 'Bourgogne-Franche-Comté',
    '89': 'Bourgogne-Franche-Comté', '90': 'Bourgogne-Franche-Comté',
    # Bretagne
    '22': 'Bretagne', '29': 'Bretagne', '35': 'Bretagne', '56': 'Bretagne',
    # Centre-Val de Loire
    '18': 'Centre-Val de Loire', '28': 'Centre-Val de Loire', '36': 'Centre-Val de Loire',
    '37': 'Centre-Val de Loire', '41': 'Centre-Val de Loire', '45': 'Centre-Val de Loire',
    # Corse
    '2A': 'Corse', '2B': 'Corse',
    # Grand Est
    '08': 'Grand Est', '10': 'Grand Est', '51': 'Grand Est', '52': 'Grand Est',
    '54': 'Grand Est', '55': 'Grand Est', '57': 'Grand Est', '67': 'Grand Est',
    '68': 'Grand Est', '88': 'Grand Est',
    # Hauts-de-France
    '02': 'Hauts-de-France', '59': 'Hauts-de-France', '60': 'Hauts-de-France',
    '62': 'Hauts-de-France', '80': 'Hauts-de-France',
    # Île-de-France
    '75': 'Île-de-France', '77': 'Île-de-France', '78': 'Île-de-France', '91': 'Île-de-France',
    '92': 'Île-de-France', '93': 'Île-de-France', '94': 'Île-de-France', '95': 'Île-de-France',
    # Normandie
    '14': 'Normandie', '27': 'Normandie', '50': 'Normandie', '61': 'Normandie', '76': 'Normandie',
    # Nouvelle-Aquitaine
    '16': 'Nouvelle-Aquitaine', '17': 'Nouvelle-Aquitaine', '19': 'Nouvelle-Aquitaine',
    '23': 'Nouvelle-Aquitaine', '24': 'Nouvelle-Aquitaine', '33': 'Nouvelle-Aquitaine',
    '40': 'Nouvelle-Aquitaine', '47': 'Nouvelle-Aquitaine', '64': 'Nouvelle-Aquitaine',
    '79': 'Nouvelle-Aquitaine', '86': 'Nouvelle-Aquitaine', '87': 'Nouvelle-Aquitaine',
    # Occitanie
    '09': 'Occitanie', '11': 'Occitanie', '12': 'Occitanie', '30': 'Occitanie',
    '31': 'Occitanie', '32': 'Occitanie', '34': 'Occitanie', '46': 'Occitanie',
    '48': 'Occitanie', '65': 'Occitanie', '66': 'Occitanie', '81': 'Occitanie', '82': 'Occitanie',
    # Pays de la Loire
    '44': 'Pays de la Loire', '49': 'Pays de la Loire', '53': 'Pays de la Loire',
    '72': 'Pays de la Loire', '85': 'Pays de la Loire',
    # Provence-Alpes-Côte d'Azur
    '04': "Provence-Alpes-Côte d'Azur", '05': "Provence-Alpes-Côte d'Azur",
    '06': "Provence-Alpes-Côte d'Azur", '13': "Provence-Alpes-Côte d'Azur",
    '83': "Provence-Alpes-Côte d'Azur", '84': "Provence-Alpes-Côte d'Azur"
}

# --- 3. OPTIONS ---
unique_regions = sorted(list(set(DEPT_TO_REGION.values())))
options_regions = [{'label': r, 'value': r} for r in unique_regions]
options_depts = [{'label': d, 'value': d} for d in sorted(DEPT_TO_REGION.keys())]

# --- 4. STYLES ---
SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "18rem",
    "padding": "2rem 1rem", "backgroundColor": "#2c3e50", "color": "#ecf0f1", "overflow": "auto",
    "boxShadow": "2px 0 5px rgba(0,0,0,0.1)"
}
CONTENT_STYLE = {
    "marginLeft": "20rem", "marginRight": "2rem", "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa", "minHeight": "100vh"
}
CARD_STYLE = {
    "border": "none", "borderRadius": "8px", "boxShadow": "0 2px 4px rgba(0,0,0,0.05)", "marginBottom": "20px"
}

# --- 5. SIDEBAR ---
sidebar = html.Div([
    html.H4("Analytics HW", className="fw-bold mb-4", style={'color': '#fff'}),

    dbc.Nav([
        dbc.NavLink([html.I(className="fa-solid fa-chart-pie me-2"), "Tableau de bord"], href="/", active="exact",
                    className="text-light"),
        dbc.NavLink([html.I(className="fa-solid fa-table me-2"), "Données brutes"], href="/dataset", active="exact",
                    className="text-light"),
        dbc.NavLink([html.I(className="fa-solid fa-circle-plus me-2"), "Ajouter Offre"], href="/add", active="exact",
                    className="text-light"),
    ], vertical=True, pills=True, className="mb-4"),

    html.Hr(style={'borderColor': 'rgba(255,255,255,0.2)'}),

    html.Div(id='sidebar-filters', children=[
        html.Small("FILTRES ACTIFS", className="text-uppercase fw-bold text-muted mb-2 d-block"),
        html.Div([
            html.Label("Régions sélectionnées :", className="small text-info mb-1"),
            html.Div(id='selected-regions-list', className="mb-3 d-flex flex-wrap gap-1", style={'minHeight': '20px'})
        ]),

        html.Label("Clusters", className="small text-light mt-2"),
        dcc.Dropdown(id='filter-cluster',
                     options=[{'label': f'Cluster {i}', 'value': i} for i in unique_clusters],
                     multi=True, placeholder="Tous", className="text-dark mb-2", style={'fontSize': '0.9rem'}),

        html.Label("Entreprises", className="small text-light mt-2"),
        dcc.Dropdown(id='filter-company',
                     options=[{'label': i, 'value': i} for i in liste_entreprises[:500]],
                     multi=True, placeholder="Toutes", className="text-dark mb-4", style={'fontSize': '0.9rem'}),

        dbc.Button([html.I(className="fa-solid fa-rotate-left me-2"), "Réinitialiser"],
                   id="btn-reset-map", color="light", size="sm", outline=True, className="w-100 mt-2"),
    ])
], style=SIDEBAR_STYLE)

# --- 6. PAGE LAYOUTS ---

# --- DASHBOARD (REDESIGN) ---
dashboard_layout = html.Div([
    # Titre et header
    dbc.Row([
        dbc.Col(html.H2("Vue d'ensemble", className="fw-bold text-dark"), width=8),
        dbc.Col(html.Div(id="selection-feedback", className="text-end text-muted mt-2"), width=4)
    ], className="mb-4"),

    # Section KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([html.I(className="fa-solid fa-briefcase fa-2x text-primary mb-2")]),
                html.H3(id="kpi-count", className="fw-bold text-dark"),
                html.Small("Offres actives", className="text-muted text-uppercase fw-bold")
            ])
        ], className="text-center h-100 border-0 shadow-sm"), width=12, md=4, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([html.I(className="fa-solid fa-euro-sign fa-2x text-success mb-2")]),
                html.H3(id="kpi-salary", className="fw-bold text-dark"),
                html.Small("Salaire moyen", className="text-muted text-uppercase fw-bold")
            ])
        ], className="text-center h-100 border-0 shadow-sm"), width=12, md=4, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Div([html.I(className="fa-solid fa-map-location-dot fa-2x text-warning mb-2")]),
                html.H3(id="kpi-dept", className="fw-bold text-dark"),
                html.Small("Départements couverts", className="text-muted text-uppercase fw-bold")
            ])
        ], className="text-center h-100 border-0 shadow-sm"), width=12, md=4, className="mb-4"),
    ]),

    # Ligne : Carte (Grande) + Camemberts (Colonne droite)
    dbc.Row([
        # Carte
        dbc.Col(dbc.Card([
            dbc.CardHeader("🗺️ Répartition géographique des offres", className="bg-white fw-bold"),
            dbc.CardBody(dcc.Graph(id='graph-map', style={'height': '500px'}), className="p-0")
        ], style=CARD_STYLE), lg=8),

        # Colonne droite (Temps de travail + Catégorie salaire)
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("⏳ Type de contrat", className="bg-white fw-bold"),
                dbc.CardBody(dcc.Graph(id='graph-time', style={'height': '200px'}), className="p-2")
            ], style=CARD_STYLE),

            dbc.Card([
                dbc.CardHeader("💰 Niveaux de salaire", className="bg-white fw-bold"),
                dbc.CardBody(dcc.Graph(id='graph-cat-salary', style={'height': '200px'}), className="p-2")
            ], style=CARD_STYLE)
        ], lg=4)
    ]),

    # Ligne du bas : Top Jobs + Distribution
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("🏆 Top 10 des métiers", className="bg-white fw-bold"),
            dbc.CardBody(dcc.Graph(id='graph-jobs'), className="p-2")
        ], style=CARD_STYLE), lg=6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("📊 Distribution des salaires par Cluster", className="bg-white fw-bold"),
            dbc.CardBody(dcc.Graph(id='graph-box'), className="p-2")
        ], style=CARD_STYLE), lg=6)
    ])
])

# --- DATASET ---
dataset_layout = html.Div([
    html.H2("📂 Base de données", className="fw-bold mb-4"),
    dbc.Card([
        dbc.CardHeader("Données brutes (filtrables)", className="bg-white fw-bold"),
        dbc.CardBody(
            dash_table.DataTable(
                id='dataset-table',
                data=df.to_dict('records'),
                columns=columns_list,
                page_size=15,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'sans-serif'},
                style_header={'backgroundColor': '#f1f2f6', 'fontWeight': 'bold', 'color': '#2c3e50'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                ],
                filter_action="native",
                sort_action="native"
            )
        )
    ], style=CARD_STYLE)
])

# --- ADD FORM ---
add_layout = html.Div([
    html.H2("➕ Ajouter une offre", className="fw-bold mb-4"),
    dbc.Card([
        dbc.CardHeader("Formulaire de saisie", className="bg-white fw-bold"),
        dbc.CardBody([
            html.Div(id="add-feedback", className="mb-4"),
            dbc.Row([
                dbc.Col([dbc.Label("Intitulé du poste", className="fw-bold"),
                         dbc.Input(id="add-title", placeholder="ex: Data Scientist")], width=6),
                dbc.Col([dbc.Label("Entreprise", className="fw-bold"),
                         dbc.Input(id="add-company", placeholder="ex: HelloWork")], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Région (Indicatif)", className="fw-bold"),
                         dcc.Dropdown(id="add-region", options=options_regions)], width=6),
                dbc.Col([dbc.Label("Département (Code)", className="fw-bold"),
                         dcc.Dropdown(id="add-dept", options=options_depts)], width=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([dbc.Label("Salaire Annuel Brut (€)", className="fw-bold"),
                         dbc.Input(id="add-salary", type="number", placeholder="35000")], width=6),
                dbc.Col([dbc.Label("Temps de travail", className="fw-bold"), dbc.Select(id="add-worktime", options=[
                    {"label": "Temps plein", "value": "1"}, {"label": "Temps partiel", "value": "0"}
                ])], width=6),
            ], className="mb-4"),
            dbc.Button([html.I(className="fa-solid fa-floppy-disk me-2"), "Enregistrer l'offre"], id="btn-save-add",
                       color="primary", size="lg")
        ])
    ], style=CARD_STYLE)
])