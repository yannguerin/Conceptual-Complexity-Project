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
def complexity_index_calculator(n_clicks: int, text: str) -> str:
    """The main callback for calculating the complexity of the input text.
    Uses the Complexity_Index function from utils to calculate the index based on
    the text input from the text box

    Args:
        n_clicks (int): Number of clicks on the Submit button
        text (str): The text inside the text box

    Returns:
        str: The complexity index of the submitted text
    """
    # Reading the csv file containing the values used in calculating the index
    df = read_csv("./data/word_complexity_index.csv")
    if n_clicks > 0:
        complexity_index_value = complexity_index(df, text)
        return "Complexity Index: " + complexity_index_value
    else:
        return "Complexity Index:"


layout = html.Div([
    html.H1("Text Complexity Calculator", id='center'),
    complexity_calculations
])
