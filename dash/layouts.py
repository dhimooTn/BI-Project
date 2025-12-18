from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from gestionnaire import db_manager

# Chargement des données
df = db_manager.get_all_data()

# Extraction des valeurs uniques
if not df.empty:
    liste_entreprises = sorted(df['entreprise'].dropna().unique().tolist()[:500])
    unique_clusters = sorted(df['cluster'].dropna().unique().tolist())
    unique_cities = sorted(df['region'].dropna().unique().tolist()[:100]) if 'region' in df.columns else []
    unique_depts = sorted([int(d) for d in df['departement'].dropna().unique()
                           if str(d).replace('.', '').isdigit() or isinstance(d, (int, float))])
    columns_list = [{"name": i, "id": i} for i in df.columns]
else:
    liste_entreprises = []
    unique_clusters = []
    unique_cities = []
    unique_depts = list(range(1, 96))
    columns_list = []

# Options pour dropdowns
options_cities = [{'label': city, 'value': city} for city in unique_cities]
options_depts = [{'label': f"Département {d:02d}", 'value': d} for d in unique_depts]

# Régions officielles françaises
REGIONS_OFFICIELLES = [
    'Auvergne-Rhône-Alpes', 'Bourgogne-Franche-Comté', 'Bretagne',
    'Centre-Val de Loire', 'Corse', 'Grand Est', 'Guadeloupe',
    'Guyane', 'Hauts-de-France', 'Île-de-France', 'La Réunion',
    'Martinique', 'Mayotte', 'Normandie', 'Nouvelle-Aquitaine',
    'Occitanie', 'Pays de la Loire', "Provence-Alpes-Côte d'Azur"
]
options_regions = [{'label': r, 'value': r} for r in REGIONS_OFFICIELLES]

# Styles
SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "18rem",
    "padding": "2rem 1rem", "backgroundColor": "#2c3e50", "color": "#ecf0f1",
    "overflow": "auto", "boxShadow": "2px 0 5px rgba(0,0,0,0.1)"
}

CONTENT_STYLE = {
    "marginLeft": "20rem", "marginRight": "2rem", "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa", "minHeight": "100vh"
}

CARD_STYLE = {
    "border": "none", "borderRadius": "8px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.05)", "marginBottom": "20px"
}

# SIDEBAR
sidebar = html.Div([
    html.H4("Analytics HW", className="fw-bold mb-4", style={'color': '#fff'}),

    dbc.Nav([
        dbc.NavLink([html.I(className="fa-solid fa-chart-pie me-2"), "Dashboard"],
                    href="/", active="exact", className="text-light"),
        dbc.NavLink([html.I(className="fa-solid fa-table me-2"), "Données"],
                    href="/dataset", active="exact", className="text-light"),
        dbc.NavLink([html.I(className="fa-solid fa-circle-plus me-2"), "Ajouter"],
                    href="/add", active="exact", className="text-light"),
    ], vertical=True, pills=True, className="mb-4"),

    html.Hr(style={'borderColor': 'rgba(255,255,255,0.2)'}),

    html.Div(id='sidebar-filters', children=[
        html.Small("FILTRES", className="text-uppercase fw-bold text-muted mb-2 d-block"),

        html.Label("Villes", className="small text-light mt-2"),
        dcc.Dropdown(id='filter-city', options=options_cities, multi=True,
                     placeholder="Toutes", className="text-dark mb-2"),

        html.Label("Départements", className="small text-light mt-2"),
        dcc.Dropdown(id='filter-dept', options=options_depts, multi=True,
                     placeholder="Tous", className="text-dark mb-2"),

        html.Label("Clusters", className="small text-light mt-2"),
        dcc.Dropdown(id='filter-cluster',
                     options=[{'label': f'Cluster {i}', 'value': i} for i in unique_clusters],
                     multi=True, placeholder="Tous", className="text-dark mb-2"),

        html.Label("Entreprises", className="small text-light mt-2"),
        dcc.Dropdown(id='filter-company',
                     options=[{'label': e, 'value': e} for e in liste_entreprises],
                     multi=True, placeholder="Toutes", className="text-dark mb-4"),

        dbc.Button([html.I(className="fa-solid fa-rotate-left me-2"), "Réinitialiser"],
                   id="btn-reset-map", color="light", size="sm", outline=True, className="w-100"),
    ])
], style=SIDEBAR_STYLE)

# DASHBOARD LAYOUT
dashboard_layout = html.Div([
    dbc.Row([
        dbc.Col(html.H2("Vue d'ensemble", className="fw-bold"), width=8),
        dbc.Col(html.Div(id="selection-feedback", className="text-end text-muted mt-2"), width=4)
    ], className="mb-4"),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.I(className="fa-solid fa-briefcase fa-2x text-primary mb-2"),
                html.H3(id="kpi-count", className="fw-bold"),
                html.Small("Offres actives", className="text-muted text-uppercase fw-bold")
            ])
        ], className="text-center border-0 shadow-sm"), width=4, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.I(className="fa-solid fa-euro-sign fa-2x text-success mb-2"),
                html.H3(id="kpi-salary", className="fw-bold"),
                html.Small("Salaire moyen", className="text-muted text-uppercase fw-bold")
            ])
        ], className="text-center border-0 shadow-sm"), width=4, className="mb-4"),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.I(className="fa-solid fa-map-location-dot fa-2x text-warning mb-2"),
                html.H3(id="kpi-dept", className="fw-bold"),
                html.Small("Départements", className="text-muted text-uppercase fw-bold")
            ])
        ], className="text-center border-0 shadow-sm"), width=4, className="mb-4"),
    ]),

    # Carte + Camemberts
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("🗺️ Répartition géographique", className="bg-white fw-bold"),
            dbc.CardBody(dcc.Graph(id='graph-map', style={'height': '500px'}), className="p-0")
        ], style=CARD_STYLE), lg=8),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader("⏳ Contrats", className="bg-white fw-bold"),
                dbc.CardBody(dcc.Graph(id='graph-time', style={'height': '200px'}))
            ], style=CARD_STYLE),

            dbc.Card([
                dbc.CardHeader("💰 Salaires", className="bg-white fw-bold"),
                dbc.CardBody(dcc.Graph(id='graph-cat-salary', style={'height': '200px'}))
            ], style=CARD_STYLE)
        ], lg=4)
    ]),

    # Top Jobs + Box Plot
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("🏆 Top 10 métiers", className="bg-white fw-bold"),
            dbc.CardBody(dcc.Graph(id='graph-jobs'))
        ], style=CARD_STYLE), lg=6),

        dbc.Col(dbc.Card([
            dbc.CardHeader("📊 Salaires par Cluster", className="bg-white fw-bold"),
            dbc.CardBody(dcc.Graph(id='graph-box'))
        ], style=CARD_STYLE), lg=6)
    ])
])

# DATASET LAYOUT
dataset_layout = html.Div([
    html.H2("📂 Base de données", className="fw-bold mb-4"),
    dbc.Card([
        dbc.CardHeader("Données brutes", className="bg-white fw-bold"),
        dbc.CardBody(
            dash_table.DataTable(
                id='dataset-table',
                data=df.to_dict('records'),
                columns=columns_list,
                page_size=15,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'padding': '12px'},
                style_header={'backgroundColor': '#f1f2f6', 'fontWeight': 'bold'},
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f8f8'}
                ],
                filter_action="native",
                sort_action="native"
            )
        )
    ], style=CARD_STYLE)
])

# ADD LAYOUT
add_layout = html.Div([
    html.H2("➕ Ajouter une offre", className="fw-bold mb-4"),
    dbc.Card([
        dbc.CardHeader("Formulaire", className="bg-white fw-bold"),
        dbc.CardBody([
            html.Div(id="add-feedback", className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Intitulé du poste", className="fw-bold"),
                    dbc.Input(id="add-title", placeholder="ex: Data Scientist")
                ], width=6),
                dbc.Col([
                    dbc.Label("Entreprise", className="fw-bold"),
                    dbc.Input(id="add-company", placeholder="ex: HelloWork")
                ], width=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Région", className="fw-bold"),
                    dcc.Dropdown(id="add-region", options=options_regions,
                                 placeholder="Sélectionnez")
                ], width=6),
                dbc.Col([
                    dbc.Label("Département", className="fw-bold"),
                    dcc.Dropdown(id="add-dept", options=options_depts,
                                 placeholder="Sélectionnez")
                ], width=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Ville", className="fw-bold"),
                    dbc.Input(id="add-city", placeholder="ex: Paris")
                ], width=12),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Salaire Annuel Brut (€)", className="fw-bold"),
                    dbc.Input(id="add-salary", type="number", placeholder="35000")
                ], width=6),
                dbc.Col([
                    dbc.Label("Temps de travail", className="fw-bold"),
                    dbc.Select(id="add-worktime", options=[
                        {"label": "Temps plein", "value": "1"},
                        {"label": "Temps partiel", "value": "0"}
                    ], value="1")
                ], width=6),
            ], className="mb-4"),

            dbc.Button([html.I(className="fa-solid fa-floppy-disk me-2"), "Enregistrer"],
                       id="btn-save-add", color="primary", size="lg")
        ])
    ], style=CARD_STYLE)
])