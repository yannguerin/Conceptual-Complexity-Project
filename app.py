import dash
import dash_bootstrap_components as dbc
from dash import html


from components import navbar

app = dash.Dash(__name__, use_pages=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])


# Layout
app.layout = html.Div(
    style={"backgroundColor": "#FFFFFF"},
    children=[
        navbar,
        dash.page_container
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
