import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from flask import Flask

# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '¡Hola, mundo!'

# Cargar los datos a trabajar
df = pd.read_csv("datos.csv", delimiter=";")
df = df.drop_duplicates()

# Rango de horas de estudio para el slider
min_horas = int(df["HORAS_DE_ESTUDIO"].min())
max_horas = int(df["HORAS_DE_ESTUDIO"].max())

# Opciones de gráficos para el checklist
graf_options = [
    {"label": "Histograma de la distribución de Lugares", "value": "graf1"},
    {"label": "Boxplot de Horas de Estudio", "value": "graf2"},
    {"label": "Promedio de Horas por Lugar", "value": "graf3"},
    {"label": "Pastel de la distribución de Puntuación", "value": "graf4"},
    {"label": "Mapa de calor de Mejoras vs Lugar", "value": "graf5"}
]

# Opciones para el dropdown de carreras (incluye "General")
carreras_options = [{"label": "General", "value": "General"}] + [
    {"label": c, "value": c} for c in sorted(df["CARRERA"].unique())
]

# Inicializar la aplicación Dash (esto sobrescribe la variable app, pero se asume que se utiliza Dash para el dashboard)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Análisis de Unisinu"

# Layout de la vista inicial
home_layout = html.Div(
    id="Inicio_info",
    style={"display": "block"},
    children=[
        dbc.Row([
            dbc.Col(
                html.H2("Bienvenido a este Análisis de Lugares de Estudio en la Unisinu", 
                        className="text-center",
                        style={"color": "white"}),
                width=12,
                style={"backgroundColor": "#f30e07", "padding": "20px"}
            )
        ]),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H4("Autores: Jhon Martinez y Erick Valenzuela", className="mt-4", style={"color": "#f30e07"}),
                    html.P(
                        ("En este dashboard presentamos un análisis integral acerca de los lugares de estudio "
                         "más frecuentados por los estudiantes dentro de la Universidad del Sinu Elías Bechara Zainum "
                         "Seccional Cartagena, con el objetivo de obtener datos nuevos y presentar propuestas de mejoras "
                         "a estos lugares analizados"),
                        style={"color": "#333"}
                    ),
                    dbc.Button("Descargar Data", id="download-button", color="warning", className="me-2"),
                    dcc.Download(id="download-dataframe-csv"),
                    dbc.Button("Acceder al dashboard", id="go-dashboard-button", color="primary", className="ms-2")
                ], width=12)
            ], className="my-3")
        ], fluid=True)
    ]
)

# Layout del dashboard
dashboard_layout = html.Div(
    id="dashboard-container",
    style={"display": "none"},
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.H2("Dashboard de Lugares de estudio en la Unisinu", className="text-center", 
                            style={"color": "white"}),
                    width=12,
                    style={"backgroundColor": "#f30e07", "padding": "20px"}
                )
            ]),
            dbc.Row([
                # Panel izquierdo con filtros
                dbc.Col([
                    html.Div([
                        html.Label("Seleccione la carrera a filtrar:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="carrera-dropdown",
                            options=carreras_options,
                            value="General",
                            placeholder="General"
                        ),
                    ], className="mb-3"),
                    html.Div([
                        html.Label("Seleccione el lugar de estudio que desea filtrar:", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="lugar-dropdown",
                            options=[{"label": l, "value": l} for l in sorted(df["LUGAR_DE_ESTUDIO"].unique())],
                            value=[],
                            multi=True,
                            placeholder="General"
                        ),
                    ], className="mb-3"),
                    html.Div([
                        html.Label("Escoga el rango de horas de estudio que desea visualizar:", style={"fontWeight": "bold"}),
                        dcc.RangeSlider(
                            id="horas-slider",
                            min=min_horas,
                            max=max_horas,
                            step=1,
                            value=[min_horas, max_horas],
                            marks={i: str(i) for i in range(min_horas, max_horas+1, max(1, (max_horas-min_horas)//5))}
                        ),
                    ], className="mb-3"),
                    html.Div([
                        html.Label("Seleccione la gráfica que desea ampliar:", style={"fontWeight": "bold"}),
                        dcc.Checklist(
                            id="graf-checklist",
                            options=graf_options,
                            value=["graf1", "graf2", "graf3", "graf4", "graf5"],
                            labelStyle={'display': 'block'}
                        )
                    ], className="mb-3")
                ], width=3, className="bg-light p-3", style={"border": "2px solid #FFD700"}),
                
                # Columna para los gráficos
                dbc.Col([
                    dcc.Loading(
                        id="loading-graphs",
                        type="default",
                        children=html.Div(id="graphs-container")
                    )
                ], id="content-col", width=9)
            ], className="mt-3"),
            dbc.Row([
                dbc.Col(
                    html.H4("Tabla de datos filtrados", className="mt-4", style={"color": "#f30e07"}),
                    width=12
                )
            ]),
            dbc.Row([
                dbc.Col(
                    dash_table.DataTable(
                        id="filtered-table",
                        columns=[{"name": col, "id": col} for col in df.columns],
                        data=df.to_dict("records"),
                        page_size=10,
                        filter_action="native",
                        sort_action="native",
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                    ),
                    width=12
                )
            ], className="mb-4")
        ], fluid=True)
    ]
)

# Layout principal: se incluyen los dos layouts creados
app.layout = html.Div([
    home_layout,
    dashboard_layout
])

# Callback para cambiar de pantalla (de inicio a dashboard)
@app.callback(
    [Output("Inicio_info", "style"),
     Output("dashboard-container", "style")],
    [Input("go-dashboard-button", "n_clicks")],
    [State("Inicio_info", "style"),
     State("dashboard-container", "style")]
)
def show_dashboard(n_clicks, home_style, dash_style):
    if n_clicks:
        return {"display": "none"}, {"display": "block"}
    else:
        return {"display": "block"}, {"display": "none"}

# Callback para descargar los datos
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def download_data(n_clicks):
    return dcc.send_data_frame(df.to_csv, "data_lugares_de_estudio.csv", index=False)

# Callback para actualizar los gráficos según los filtros seleccionados
@app.callback(
    Output("graphs-container", "children"),
    [Input("carrera-dropdown", "value"),
     Input("lugar-dropdown", "value"),
     Input("horas-slider", "value"),
     Input("graf-checklist", "value")]
)
def update_graphs(selected_carrera, selected_lugares, horas_range, selected_grafs):
    dff = df.copy()
    if selected_carrera and selected_carrera != "General":
        dff = dff[dff["CARRERA"] == selected_carrera]
    if selected_lugares:
        dff = dff[dff["LUGAR_DE_ESTUDIO"].isin(selected_lugares)]
    dff = dff[(dff["HORAS_DE_ESTUDIO"] >= horas_range[0]) & (dff["HORAS_DE_ESTUDIO"] <= horas_range[1])]

    graphs = []
    if "graf1" in selected_grafs:
        fig1 = px.histogram(dff, x="LUGAR_DE_ESTUDIO", title="Distribución de Lugares de Estudio",
                            color="LUGAR_DE_ESTUDIO", template="plotly_white")
        graphs.append(dcc.Graph(figure=fig1, id="graph1"))
    if "graf2" in selected_grafs:
        fig2 = px.box(dff, x="HORAS_DE_ESTUDIO", title="Boxplot de Horas de Estudio", template="plotly_white")
        fig2.update_traces(marker=dict(color="#FFD700"), line=dict(color="#FFD700"))
        graphs.append(dcc.Graph(figure=fig2, id="graph2"))
    if "graf3" in selected_grafs:
        prom_horas = dff.groupby("LUGAR_DE_ESTUDIO")["HORAS_DE_ESTUDIO"].mean().reset_index()
        prom_horas.columns = ['LUGAR_DE_ESTUDIO', 'HORAS_PROMEDIO']
        fig3 = px.bar(prom_horas, x="LUGAR_DE_ESTUDIO", y="HORAS_PROMEDIO",
                      title="Promedio de Horas de Estudio por Lugar", color="LUGAR_DE_ESTUDIO", template="plotly_white")
        graphs.append(dcc.Graph(figure=fig3, id="graph3"))
    if "graf4" in selected_grafs:
        puntuacion = dff['PUNTUACION'].value_counts().reset_index()
        puntuacion.columns = ['PUNTUACION', 'FRECUENCIA']
        fig4 = px.pie(puntuacion, names='PUNTUACION', values='FRECUENCIA',
                      title="Distribución de Puntuación", hole=0.3, template="plotly_white")
        graphs.append(dcc.Graph(figure=fig4, id="graph4"))
    if "graf5" in selected_grafs:
        color_scale = [(0.0, "#ffffff"), (0.5, "#FFD700"), (1.0, "#f30e07")]
        tabla = pd.crosstab(dff['MEJORAS_SUGERIDAS'], dff['LUGAR_DE_ESTUDIO'])
        fig5 = px.imshow(tabla, text_auto=True, aspect="auto",
                         title="Mapa de calor de Mejoras Sugeridas vs Lugar de Estudio",
                         template="plotly_white", color_continuous_scale=color_scale)
        graphs.append(dcc.Graph(figure=fig5, id="graph5"))

    rows = []
    if len(graphs) == 1:
        rows = [dbc.Row(dbc.Col(graphs[0], md=12), className="mb-4")]
    else:
        for i in range(0, len(graphs), 2):
            row_graphs = graphs[i:i+2]
            col_width = 12 if len(row_graphs) == 1 else 6
            row = dbc.Row([dbc.Col(graph, md=col_width) for graph in row_graphs], className="mb-4")
            rows.append(row)
    if not rows:
        rows = [html.Div("Por favor, selecciona algún gráfico para visualizar", className="text-center")]
    return rows

# Callback para actualizar la tabla de datos filtrados según los filtros
@app.callback(
    Output("filtered-table", "data"),
    [Input("carrera-dropdown", "value"),
     Input("lugar-dropdown", "value"),
     Input("horas-slider", "value")]
)
def update_table(selected_carrera, selected_lugares, horas_range):
    dff = df.copy()
    if selected_carrera and selected_carrera != "General":
        dff = dff[dff["CARRERA"] == selected_carrera]
    if selected_lugares:
        dff = dff[dff["LUGAR_DE_ESTUDIO"].isin(selected_lugares)]
    dff = dff[(dff["HORAS_DE_ESTUDIO"] >= horas_range[0]) & (dff["HORAS_DE_ESTUDIO"] <= horas_range[1])]
    return dff.to_dict("records")

# Ejecutar la aplicación en el puerto 8050
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)

