from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx

import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# NetworkX Multipartite Graph to Dash Cytoscape


def nx_to_cyto(G, pos):
    cyto_data = nx.cytoscape_data(G)["elements"]
    cyto_nodes = cyto_data["nodes"]
    cyto_edges = cyto_data["edges"]
    for index, node in enumerate(cyto_nodes):
        node_name = node["data"]["name"]
        cyto_nodes[index]["data"]["label"] = cyto_nodes[index]["data"].pop(
            "value")
        cyto_nodes[index]["data"]["size"] = 1
        cyto_nodes[index]["position"] = {
            "x": pos[node_name][0] * 25,
            "y": pos[node_name][1] * 1000000,
        }
    return cyto_nodes, cyto_edges

# Layout Components

# General Scaffolding


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="/"))
    ],
    brand="Concept",
    brand_href="/",
    color="dark",
    links_left=True,
    dark=True,
)

# Inputs
# Word Search
word_input = html.Div(
    [
        dbc.Input(id="word_input", placeholder="Search for Word", type="text"),
        html.Br(),
        html.P(id="output"),
    ],
    style={"margin": "2% 10% 2% 10%"}
)
# Depth Option
depth_slider = html.Div([
    dcc.Slider(0, 20, 5,
               value=10,
               id='my-slider'
               )],
    style={"margin": "2% 10% 2% 10%"}
)

# Cytoscape Graph
cyto_graph = html.Div(cyto.Cytoscape(
    id='cytoscape-two-nodes',
    layout={'name': 'preset'},
    style={'width': '100%', 'height': '600px'},
    elements=[
        {'data': {'id': 'one', 'label': 'Node 1'},
         'position': {'x': 75, 'y': 75}},
        {'data': {'id': 'two', 'label': 'Node 2'},
         'position': {'x': 200, 'y': 200}},
        {'data': {'source': 'one', 'target': 'two'}}
    ]
),
    # style={"margin-top": "100px"}
)


default_stylesheet = [
    {
        "selector": "node",
        "style": {
            "width": "data(size)",
            "height": "data(size)",
            "background-color": "mapData(layer, 0, 3, white, blue)",
            "content": "data(label)",
            "font-size": "12px",
            "text-valign": "center",
            "text-halign": "center",
        },
    }
]

app.layout = html.Div(
    style={"backgroundColor": "#4C4E52"},
    children=[
        navbar,
        word_input,
        depth_slider,
        cyto_graph
    ],
)


# Callbacks

# For Word Search and Depth Option

# On clicking of node

# On Panning

# Setting all the layout Component

if __name__ == "__main__":
    app.run_server(debug=True)
