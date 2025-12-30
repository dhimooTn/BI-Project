import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ⭐ CRITIQUE: Importer FrequencyEncoder AVANT model_predictor
from frequency_encoder import FrequencyEncoder

import layouts
from gestionnaire import db_manager
from model_predictor import predictor

# Configuration App
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.FONT_AWESOME],
                suppress_callback_exceptions=True)
server = app.server


def load_data_complete():
    """Charge et prépare les données"""
    df = db_manager.get_all_data()

    if not df.empty:
        if 'departement' in df.columns:
            df['departement'] = df['departement'].astype(str).apply(
                lambda x: x.split('.')[0].zfill(2))

        if 'categorie_salaire' in df.columns:
            df['categorie_salaire_label'] = df['categorie_salaire'].apply(
                lambda x: "Haut salaire" if x == 1 else "Bas salaire")

        if 'temps_travail' in df.columns:
            df['temps_travail_label'] = df['temps_travail'].apply(
                lambda x: "Temps plein" if x == 1 else "Temps partiel")

    return df


df = load_data_complete()

# Layout principal
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id='selection-store', data={'cities': [], 'depts': []}),
    layouts.sidebar,
    html.Div(id="page-content", style=layouts.CONTENT_STYLE, children=[
        html.Div(id="view-dashboard", children=layouts.dashboard_layout),
        html.Div(id="view-dataset", children=layouts.dataset_layout, style={'display': 'none'}),
        html.Div(id="view-add", children=layouts.add_layout, style={'display': 'none'}),
    ])
])


# CALLBACK 1: ROUTAGE
@app.callback(
    [Output("view-dashboard", "style"),
     Output("view-dataset", "style"),
     Output("view-add", "style"),
     Output("sidebar-filters", "style"),
     Output("dataset-table", "data")],
    [Input("url", "pathname")]
)
def render_page(pathname):
    """Gère la navigation entre les pages"""
    dash_style = {'display': 'block'}
    data_style = {'display': 'none'}
    add_style = {'display': 'none'}
    filter_style = {'display': 'block'}
    table_data = dash.no_update

    if pathname == "/dataset":
        dash_style = {'display': 'none'}
        data_style = {'display': 'block'}
        filter_style = {'display': 'none'}
        table_data = db_manager.get_all_data().to_dict('records')

    elif pathname == "/add":
        dash_style = {'display': 'none'}
        add_style = {'display': 'block'}
        filter_style = {'display': 'none'}

    return dash_style, data_style, add_style, filter_style, table_data


# CALLBACK 1.5: FILTRE BIDIRECTIONNEL VILLE ↔ DÉPARTEMENT
@app.callback(
    [Output('filter-dept', 'options'),
     Output('filter-city', 'options')],
    [Input('filter-city', 'value'),
     Input('filter-dept', 'value')]
)
def update_filters_bidirectional(selected_cities, selected_depts):
    """Met à jour les options de département et ville de manière bidirectionnelle"""
    # Options par défaut (toutes les données)
    all_unique_depts = sorted([int(d) for d in df['departement'].dropna().unique()
                               if str(d).replace('.', '').isdigit() or isinstance(d, (int, float))])
    all_dept_options = [{'label': f"Département {d:02d}", 'value': d} for d in all_unique_depts]

    all_unique_cities = sorted(df['region'].dropna().unique().tolist()[:100]) if 'region' in df.columns else []
    all_city_options = [{'label': city, 'value': city} for city in all_unique_cities]

    # Si rien n'est sélectionné, retourner toutes les options
    if (not selected_cities or len(selected_cities) == 0) and (not selected_depts or len(selected_depts) == 0):
        return all_dept_options, all_city_options

    # Cas 1: Villes sélectionnées → filtrer départements
    if selected_cities and len(selected_cities) > 0:
        dff_city = df[df['region'].isin(selected_cities)]
        if not dff_city.empty:
            filtered_depts = sorted([int(d) for d in dff_city['departement'].dropna().unique()
                                     if str(d).replace('.', '').isdigit() or isinstance(d, (int, float))])
            dept_options = [{'label': f"Département {d:02d}", 'value': d} for d in filtered_depts]
        else:
            dept_options = []
    else:
        dept_options = all_dept_options

    # Cas 2: Départements sélectionnés → filtrer villes
    if selected_depts and len(selected_depts) > 0:
        depts_str = [str(d).zfill(2) for d in selected_depts]
        dff_dept = df[df['departement'].isin(depts_str)]
        if not dff_dept.empty:
            filtered_cities = sorted(dff_dept['region'].dropna().unique().tolist())
            city_options = [{'label': city, 'value': city} for city in filtered_cities]
        else:
            city_options = []
    else:
        city_options = all_city_options

    return dept_options, city_options


# CALLBACK 2: AJOUT OFFRE
@app.callback(
    Output("add-feedback", "children"),
    Input("btn-save-add", "n_clicks"),
    [State("add-title", "value"),
     State("add-company", "value"),
     State("add-region", "value"),
     State("add-dept", "value"),
     State("add-city", "value"),
     State("add-salary", "value"),
     State("add-worktime", "value")]
)
def save_offer(n_clicks, title, company, region, dept, city, salary, worktime):
    """Enregistre une nouvelle offre avec prédiction du cluster"""
    global df

    if not n_clicks:
        raise PreventUpdate

    if not all([title, company, dept, salary]):
        return dbc.Alert("Merci de remplir tous les champs obligatoires.",
                         color="danger")

    try:
        sal_val = float(salary)
        dept_val = int(dept)
        cat = 1 if sal_val > 35000 else 0  # Médiane
        temps_val = 1 if worktime == "1" else 0
        location_value = city if city else region

        # Prédiction du cluster
        if predictor and predictor.model:
            cluster_predit = predictor.predict_cluster(
                emploi=title, entreprise=company, ville=location_value,
                departement=dept_val, salaire=sal_val,
                categorie_salaire=cat, temps_travail=temps_val
            )
        else:
            cluster_predit = 0
            print("⚠️ Modèle non disponible, cluster par défaut: 0")

        # Ajout en base
        ok = db_manager.ajouter(title, company, location_value, dept_val,
                                sal_val, cat, temps_val, cluster_predit)

        if ok:
            df = load_data_complete()
            return dbc.Alert([
                html.H5("✅ Offre ajoutée avec succès!", className="alert-heading"),
                html.P(f"Classée dans le Cluster {cluster_predit}"),
                html.Hr(),
                html.P("Retournez au dashboard pour voir les changements.", className="mb-0")
            ], color="success")
        else:
            return dbc.Alert("Erreur lors de l'enregistrement.", color="danger")

    except ValueError:
        return dbc.Alert("Le salaire et le département doivent être des nombres.",
                         color="danger")
    except Exception as e:
        return dbc.Alert(f"Erreur: {e}", color="danger")


# CALLBACK 3: RESET FILTRES
@app.callback(
    [Output('filter-city', 'value'),
     Output('filter-dept', 'value'),
     Output('filter-cluster', 'value'),
     Output('filter-company', 'value')],
    Input('btn-reset-map', 'n_clicks')
)
def reset_filters(n_clicks):
    """Réinitialise tous les filtres"""
    if not n_clicks:
        raise PreventUpdate
    return None, None, None, None


# CALLBACK 3.5: SÉLECTION RÉGION DEPUIS TREEMAP
@app.callback(
    Output('filter-city', 'value', allow_duplicate=True),
    Input('graph-map', 'clickData'),
    prevent_initial_call=True
)
def update_from_treemap(click_data):
    """Met à jour le filtre ville selon la région cliquée dans le treemap"""
    if not click_data:
        raise PreventUpdate

    try:
        # Extraire la région cliquée
        region_clicked = click_data['points'][0]['label']

        # Trouver toutes les villes de cette région
        dff = df[df['departement'].apply(dept_to_region) == region_clicked]
        cities_in_region = dff['region'].dropna().unique().tolist()

        return cities_in_region
    except:
        raise PreventUpdate


def dept_to_region(dept):
    """Convertit un département en région"""
    try:
        dept_num = int(str(dept).split('.')[0])
    except:
        return "Autre"

    mapping = {
        range(75, 96): "Île-de-France",
        (14, 27, 50, 61, 76): "Normandie",
        (22, 29, 35, 56): "Bretagne",
        (44, 49, 53, 72, 85): "Pays de la Loire",
        (18, 28, 36, 37, 41, 45): "Centre-Val de Loire",
        (21, 25, 39, 58, 70, 71, 89, 90): "Bourgogne-Franche-Comté",
        (2, 59, 60, 62, 80): "Hauts-de-France",
        (8, 10, 51, 52, 54, 55, 57, 67, 68, 88): "Grand Est",
        (16, 17, 19, 23, 24, 33, 40, 47, 64, 79, 86, 87): "Nouvelle-Aquitaine",
        (9, 11, 12, 30, 31, 32, 34, 46, 48, 65, 66, 81, 82): "Occitanie",
        (1, 3, 7, 15, 26, 38, 42, 43, 63, 69, 73, 74): "Auvergne-Rhône-Alpes",
        (4, 5, 6, 13, 83, 84): "Provence-Alpes-Côte d'Azur",
        (20, 201, 202): "Corse"
    }

    for depts, region in mapping.items():
        if dept_num in depts if isinstance(depts, tuple) else dept_num in depts:
            return region

    return "Autre"


# CALLBACK 4: UPDATE DASHBOARD
@app.callback(
    [Output('kpi-count', 'children'),
     Output('kpi-salary', 'children'),
     Output('kpi-dept', 'children'),
     Output('graph-map', 'figure'),
     Output('graph-time', 'figure'),
     Output('graph-cat-salary', 'figure'),
     Output('graph-jobs', 'figure'),
     Output('graph-box', 'figure'),
     Output('selection-feedback', 'children')],
    [Input('filter-city', 'value'),
     Input('filter-dept', 'value'),
     Input('filter-cluster', 'value'),
     Input('filter-company', 'value')]
)
def update_dashboard(cities, depts, clusters, companies):
    """Met à jour tous les graphiques selon les filtres"""
    dff = df.copy()

    # Application des filtres
    if cities:
        dff = dff[dff['region'].isin(cities)]
    if depts:
        depts_str = [str(d).zfill(2) for d in depts]
        dff = dff[dff['departement'].isin(depts_str)]
    if clusters:
        dff = dff[dff['cluster'].isin(clusters)]
    if companies:
        dff = dff[dff['entreprise'].isin(companies)]

    # KPIs
    count = len(dff)
    avg = f"{dff['salaire_annuel'].mean():,.0f} €" if count > 0 else "-"
    nb_dept = dff['departement'].nunique() if count > 0 else 0

    # Figure vide par défaut
    empty = go.Figure().update_layout(
        xaxis={'visible': False}, yaxis={'visible': False},
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(text="Pas de données", xref="paper", yref="paper",
                          showarrow=False, font=dict(size=20))]
    )

    if count == 0:
        return 0, "-", 0, empty, empty, empty, empty, empty, "Aucune donnée"

    # 1. TREEMAP (remplace la carte)
    dff['region_mapped'] = dff['departement'].apply(dept_to_region)

    # Grouper par région et calculer les statistiques
    df_region = dff.groupby('region_mapped').agg({
        'salaire_annuel': ['count', 'mean']
    }).reset_index()
    df_region.columns = ['region', 'count', 'avg_salary']
    df_region = df_region[df_region['region'] != 'Autre']

    # Créer le treemap
    fig_map = px.treemap(
        df_region,
        path=['region'],
        values='count',
        color='avg_salary',
        color_continuous_scale='RdYlGn',
        labels={'count': 'Nombre d\'offres', 'avg_salary': 'Salaire moyen', 'region': 'Région'},
        title='Distribution des offres par région'
    )

    fig_map.update_traces(
        textinfo='label+value',
        textfont_size=12,
        marker=dict(line=dict(width=2, color='white'))
    )

    fig_map.update_layout(
        margin=dict(t=40, l=0, r=0, b=0),
        font=dict(size=11)
    )

    # 2. CAMEMBERT TEMPS
    fig_time = px.pie(dff, names='temps_travail_label', hole=0.6,
                      color_discrete_sequence=px.colors.qualitative.Prism)
    fig_time.update_layout(
        margin={"r": 10, "t": 10, "l": 10, "b": 10}, showlegend=False,
        annotations=[dict(text=f"{count}", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    # 3. BARRES SALAIRES
    cat_counts = dff['categorie_salaire_label'].value_counts().reset_index()
    cat_counts.columns = ['categorie', 'count']
    fig_cat = px.bar(cat_counts, x='count', y='categorie', orientation='h',
                     text='count', color='categorie',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_cat.update_layout(margin={"r": 10, "t": 0, "l": 0, "b": 0},
                          xaxis={'visible': False}, yaxis={'title': ''},
                          showlegend=False, plot_bgcolor='rgba(0,0,0,0)')

    # 4. TOP JOBS
    top_jobs = dff['emploi'].value_counts().head(10).reset_index()
    top_jobs.columns = ['emploi', 'count']
    fig_jobs = px.bar(top_jobs, x='count', y='emploi', orientation='h', text='count')
    fig_jobs.update_layout(margin={"r": 10, "t": 0, "l": 0, "b": 0},
                           yaxis={'autorange': "reversed", 'title': ''},
                           xaxis={'title': "Nombre d'offres"},
                           plot_bgcolor='rgba(0,0,0,0)')

    # 5. BOX PLOT
    fig_box = px.box(dff, x='cluster', y='salaire_annuel', color='cluster', points=False)
    fig_box.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 30},
                          showlegend=False, xaxis={'title': 'Cluster'},
                          yaxis={'title': 'Salaire'}, plot_bgcolor='white')

    # Feedback
    filters = []
    if cities: filters.append(f"{len(cities)} ville(s)")
    if depts: filters.append(f"{len(depts)} dép.")
    if clusters: filters.append(f"{len(clusters)} cluster(s)")
    if companies: filters.append(f"{len(companies)} entreprise(s)")

    feedback = f"{count} offres" + (f" filtrées par: {', '.join(filters)}" if filters else "")

    return count, avg, nb_dept, fig_map, fig_time, fig_cat, fig_jobs, fig_box, feedback


if __name__ == '__main__':
    app.run(debug=True)