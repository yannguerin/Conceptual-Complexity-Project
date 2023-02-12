from pandas import read_csv

import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dcc

from components import complexity_calculations
from utils import complexity_index

dash.register_page(__name__, path='/Complexity-Index')


@dash.callback(Output("complexity-index-output", 'children'),
               Input("submit-text-complexity", 'n_clicks'),
               Input('complexity-text-input', 'value'))
def complexity_index_calculator(n_clicks: int, text: str):
    df = read_csv("./data/word_complexity_index.csv")
    if n_clicks > 0:
        complexity_index_value = complexity_index(df, text)
        return "Complexity Index: " + str(complexity_index_value)
    else:
        return "Complexity Index"


layout = complexity_calculations
