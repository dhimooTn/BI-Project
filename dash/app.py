import dash
from dash import dcc, html, ctx, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

import layouts
from gestionnaire import db_manager

# --- CONSTANTES ---
GEOJSON_URL = "https://france-geojson.wladimir.me/regions.geojson"

# --- CONFIG APP ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.FONT_AWESOME],
                suppress_callback_exceptions=True)
server = app.server


# --- CHARGEMENT DONNÉES ---
def load_data_complete():
    df = db_manager.get_all_data()

    if not df.empty and 'departement' in df.columns:
        # 1. Nettoyage du département : on force le string et le format 2 chiffres (ex: 1 -> "01")
        # .astype(str) gère les nombres, .split('.')[0] gère les floats (1.0 -> 1), .zfill(2) met le 0 devant
        df['departement'] = df['departement'].astype(str).apply(lambda x: x.split('.')[0].zfill(2))

        # 2. Mapping région
        df['region'] = df['departement'].apply(lambda x: layouts.DEPT_TO_REGION.get(x[:2], "Autre"))

    return df


# Variable globale initiale
df = load_data_complete()

# --- LAYOUT GLOBAL ---
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id='region-store', data=[]),
    layouts.sidebar,
    html.Div(id="page-content", style=layouts.CONTENT_STYLE, children=[
        html.Div(id="view-dashboard", children=layouts.dashboard_layout),
        html.Div(id="view-dataset", children=layouts.dataset_layout, style={'display': 'none'}),
        html.Div(id="view-add", children=layouts.add_layout, style={'display': 'none'}),
    ])
])


# --- CALLBACK 1 : ROUTAGE ---
@app.callback(
    [Output("view-dashboard", "style"),
     Output("view-dataset", "style"),
     Output("view-add", "style"),
     Output("sidebar-filters", "style"),
     Output("dataset-table", "data")],
    [Input("url", "pathname")]
)
def render_page(pathname):
    dash_style = {'display': 'block'}
    data_style = {'display': 'none'}
    add_style = {'display': 'none'}
    filter_style = {'display': 'block'}
    table_data = dash.no_update

    if pathname == "/dataset":
        dash_style, data_style = {'display': 'none'}, {'display': 'block'}
        filter_style = {'display': 'none'}
        current_df = db_manager.get_all_data()
        table_data = current_df.to_dict('records')

    elif pathname == "/add":
        dash_style, add_style = {'display': 'none'}, {'display': 'block'}
        filter_style = {'display': 'none'}

    return dash_style, data_style, add_style, filter_style, table_data


# --- CALLBACK 2 : AJOUT OFFRE ---
@app.callback(
    Output("add-feedback", "children"),
    Input("btn-save-add", "n_clicks"),
    [State("add-title", "value"),
     State("add-company", "value"),
     State("add-dept", "value"),
     State("add-salary", "value"),
     State("add-worktime", "value")]
)
def save_offer(n_clicks, title, company, dept, salary, worktime):
    global df
    if not n_clicks: raise PreventUpdate

    if not all([title, company, dept, salary]):
        return dbc.Alert("Merci de remplir tous les champs obligatoires.", color="danger")

    try:
        sal_val = float(salary)
        dept_str = str(dept).zfill(2)

        # Calcul automatique de la région
        nom_region = layouts.DEPT_TO_REGION.get(dept_str[:2], "Autre")

        mediane = 35000
        cat = "Haut" if sal_val > mediane else "Bas"
        temps_str = "Temps plein" if worktime == "1" else "Temps partiel"

        # Ajout DB avec les bons arguments
        ok = db_manager.ajouter(title, company, nom_region, dept_str, sal_val, cat, temps_str)

        if ok:
            df = load_data_complete()
            return dbc.Alert("Offre ajoutée avec succès ! Retournez au tableau de bord pour voir les changements.",
                             color="success")
        else:
            return dbc.Alert("Erreur lors de l'enregistrement en base de données.", color="danger")

    except ValueError:
        return dbc.Alert("Le salaire doit être un nombre valide.", color="danger")


# --- CALLBACK 3 : SELECTION CARTE ---
@app.callback(
    [Output('selected-regions-list', 'children'), Output('region-store', 'data')],
    [Input('graph-map', 'clickData'), Input('btn-reset-map', 'n_clicks')],
    [State('region-store', 'data')]
)
def update_selection(clickData, n_reset, current):
    if not current: current = []
    trigger = ctx.triggered_id

    if trigger == 'btn-reset-map':
        return [], []

    if trigger == 'graph-map' and clickData:
        loc = clickData['points'][0]['location']
        if loc in current:
            current.remove(loc)
        else:
            current.append(loc)

    badges = [dbc.Badge(r, color="info", className="me-1") for r in current]
    return badges, current


# --- CALLBACK 4 : UPDATE DASHBOARD ---
@app.callback(
    [Output('kpi-count', 'children'), Output('kpi-salary', 'children'), Output('kpi-dept', 'children'),
     Output('graph-map', 'figure'), Output('graph-time', 'figure'), Output('graph-cat-salary', 'figure'),
     Output('graph-jobs', 'figure'), Output('graph-box', 'figure'), Output('selection-feedback', 'children')],
    [Input('region-store', 'data'), Input('filter-cluster', 'value'), Input('filter-company', 'value')]
)
def update_dashboard(regions, clusters, companies):
    dff = df.copy()

    # Filtres
    if regions: dff = dff[dff['region'].isin(regions)]
    if clusters: dff = dff[dff['cluster'].isin(clusters)]
    if companies: dff = dff[dff['entreprise'].isin(companies)]

    # KPIs
    count = len(dff)
    avg = f"{dff['salaire_annuel'].mean():,.0f} €" if count > 0 and pd.notnull(dff['salaire_annuel'].mean()) else "-"

    # Correction nom colonne KPI
    nb_dept = dff['departement'].nunique() if 'departement' in dff.columns else 0

    # Graph vide par défaut
    empty = go.Figure().update_layout(
        xaxis={'visible': False}, yaxis={'visible': False},
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    empty.add_annotation(text="Pas de données", xref="paper", yref="paper", showarrow=False, font=dict(size=20))

    if count == 0:
        return 0, "-", 0, empty, empty, empty, empty, empty, "Aucune donnée trouvée"

    # --- 1. CARTE (Mapbox) ---
    # Groupement par région
    if 'region' in dff.columns:
        df_map = dff.groupby('region').size().reset_index(name='c')
    else:
        df_map = pd.DataFrame(columns=['region', 'c'])

    fig_map = px.choropleth_mapbox(
        df_map,
        geojson=GEOJSON_URL,
        locations='region',
        featureidkey="properties.nom",
        color='c',
        color_continuous_scale="Teal",
        mapbox_style="carto-positron",
        zoom=4.8,
        center={"lat": 46.5, "lon": 2.2},
        opacity=0.7,
        labels={'c': 'Offres'}
    )
    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode='event+select'
    )

    # --- 2. CAMEMBERT TEMPS ---
    fig_time = px.pie(dff, names='temps_travail', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
    fig_time.update_layout(
        margin={"r": 10, "t": 10, "l": 10, "b": 10},
        showlegend=False,
        annotations=[dict(text=f"{count}", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    # --- 3. BARRES SALAIRES ---
    cat_counts = dff['categorie_salaire'].value_counts().reset_index()
    cat_counts.columns = ['categorie_salaire', 'count']

    fig_cat = px.bar(cat_counts, x='count', y='categorie_salaire', orientation='h',
                     text='count', color='categorie_salaire', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_cat.update_layout(
        margin={"r": 10, "t": 0, "l": 0, "b": 0},
        xaxis={'visible': False},
        yaxis={'title': ''},
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # --- 4. TOP JOBS ---
    top_jobs = dff['emploi'].value_counts().head(10).reset_index()
    top_jobs.columns = ['emploi', 'count']

    fig_jobs = px.bar(top_jobs, x='count', y='emploi', orientation='h', text='count')
    fig_jobs.update_layout(
        margin={"r": 10, "t": 0, "l": 0, "b": 0},
        yaxis={'autorange': "reversed", 'title': ''},
        xaxis={'title': 'Nombre d\'offres'},
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # --- 5. BOX PLOT CLUSTERS ---
    fig_box = px.box(dff, x='cluster', y='salaire_annuel', color='cluster', points=False)
    fig_box.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 30},
        showlegend=False,
        xaxis={'title': 'Cluster'},
        yaxis={'title': 'Salaire Annuel'},
        plot_bgcolor='white'
    )

    return count, avg, nb_dept, fig_map, fig_time, fig_cat, fig_jobs, fig_box, f"{count} offres filtrées"


if __name__ == '__main__':
    app.run(debug=True)