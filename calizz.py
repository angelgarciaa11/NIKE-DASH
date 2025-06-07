import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
from sqlalchemy import create_engine

# Conexión a la base de datos
USER = "root"
PASSWORD = "12345678"
HOST = "localhost"
PORT = "3306"
DATABASE = "nike_db"
cadena_con = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(cadena_con)

# Cargar datos base
query = """
SELECT p.nombre, p.precio, g.nombre_genero AS genero, c.nombre_categoria AS categoria
FROM productos p
JOIN generos g ON p.id_genero = g.id_genero
JOIN categorias c ON p.id_categoria = c.id_categoria
"""
df = pd.read_sql(query, engine)

# Cargar vistas
vista1 = pd.read_sql("SELECT * FROM vista_resumen_general", engine)
vista2 = pd.read_sql("SELECT * FROM vista_precio_categoria_genero", engine)
vista3 = pd.read_sql("SELECT * FROM vista_detalle_productos", engine)

# Datos para gráficas
conteo_categoria = df["categoria"].value_counts().reset_index()
conteo_categoria.columns = ["categoria", "count"]
conteo_genero = df["genero"].value_counts().reset_index()
conteo_genero.columns = ["genero", "count"]
precio_promedio = df.groupby("categoria")["precio"].mean().reset_index()
conteo_cross = df.groupby(["categoria", "genero"]).size().reset_index(name="count")
precio_cross = df.groupby(["categoria", "genero"])["precio"].mean().reset_index()
heatmap_data = precio_cross.pivot(index="categoria", columns="genero", values="precio")

# Estilos
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "17rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "Nike Dashboard"

# Sidebar
sidebar = html.Div([
    html.H2("Nike Dash", className="display-6"),
    html.Img(src="https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg", style={"height": "50px", "marginTop": "10px"}),
    html.Hr(),
    html.P("Navegación", className="lead"),
    dbc.Nav([
        dbc.NavLink("Bienvenida", href="/", active="exact"),
        dbc.NavLink("Datos Generales", href="/datos", active="exact"),
        dbc.NavLink("Comparativa por Género", href="/comparativa", active="exact"),
        dbc.NavLink("Vista General", href="/vista1", active="exact"),
        dbc.NavLink("Precios por Categoría y Género", href="/vista2", active="exact"),
        dbc.NavLink("Detalle de Productos", href="/vista3", active="exact"),
    ], vertical=True, pills=True),
], style=SIDEBAR_STYLE)

# Contenido dinámico
content = html.Div(id="page-content", style=CONTENT_STYLE)

# Layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content
])

# Callback principal
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([
            html.H1("Bienvenido a Nike Dash", style={"textAlign": "center"}),
            html.Img(src="https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg", style={"height": "80px", "float": "right", "margin": "-40px 0 20px 20px"}),
            html.P("Este dashboard analiza los productos scrapeados de Nike México, comparando precios, géneros y categorías."),
            html.P("Desarrollado con fines educativos y de análisis de datos."),
        ])

    elif pathname == "/datos":
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=px.pie(df, names="genero", title="Distribución de productos por género")), md=6),
                dbc.Col(dcc.Graph(figure=px.bar(conteo_categoria, x="categoria", y="count", title="Cantidad por categoría")), md=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=px.bar(conteo_genero, x="genero", y="count", title="Total de productos por género")), md=6),
                dbc.Col(dcc.Graph(figure=px.bar(precio_promedio, x="categoria", y="precio", title="Precio promedio por categoría")), md=6),
            ]),
        ])

    elif pathname == "/comparativa":
        return html.Div([
            dbc.Row([dbc.Col(dcc.Graph(figure=px.bar(conteo_cross, x="categoria", y="count", color="genero", barmode="group", title="Productos por género en cada categoría")), md=12)]),
            dbc.Row([dbc.Col(dcc.Graph(figure=px.box(df, x="categoria", y="precio", color="genero", title="Rango de precios por categoría y género")), md=12)]),
            dbc.Row([dbc.Col(dcc.Graph(figure=go.Figure(data=go.Heatmap(z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index, colorscale="Viridis", colorbar=dict(title="Precio Promedio"))).update_layout(title="Heatmap: Precio promedio por categoría y género")), md=12)]),
        ])

    elif pathname == "/vista1":
        return html.Div([
            html.H3("Vista General de Resumen"),
            dbc.Table.from_dataframe(vista1, striped=True, bordered=True, hover=True)
        ])

    elif pathname == "/vista2":
        return html.Div([
            html.H3("Precios Promedio por Categoría y Género"),
            dbc.Table.from_dataframe(vista2, striped=True, bordered=True, hover=True)
        ])

    elif pathname == "/vista3":
        return html.Div([
            html.H3("Detalle de Productos: Nombre, Género, Categoría y Precio"),
            dbc.Table.from_dataframe(vista3.head(50), striped=True, bordered=True, hover=True),
            html.P("Mostrando los primeros 50 productos."),
        ])

    return html.Div([
        html.H1("404 - Página no encontrada", className="text-danger"),
        html.P(f"La ruta {pathname} no existe."),
    ])

if __name__ == "__main__":
    app.run(debug=True)
