from collections import Counter
import json
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx

import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, Input, Output

from neo4j_manager import Neo4jHTTPManager

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Database Loading Callback
# Using the Initial Call


# @app.callback(Output("database-loading", 'children'),
#               Input("depth-slider", "value"))
# def database_init(value):
#     if value:
#         global database
#         database = Neo4jHTTPManager()
#         return ""


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
        dbc.Input(id="word-input", placeholder="Search for Word", type="text"),
        html.Br(),
        html.P(id="output"),
    ],
    style={"margin": "2% 10% 2% 10%"}
)
# Depth Option
depth_slider = html.Div([
    html.H6("Pick the Recursive Depth of the Concept Graph",
            style={"margin-left": "2%"}),
    dcc.Slider(1, 3, 1,
               value=2,
               id='depth-slider'
               ),
    dbc.Badge("Chosen Depth of 2", color="info", id='chosen-depth-display')
],
    style={"margin": "2% 10% 2% 10%"}
)

# Generate Button

button_generate = html.Button('Generate Graph', id='generate', n_clicks=0)

# Cytoscape Graph
cyto_graph = cyto.Cytoscape(
    id='cytoscape-graph',
    style={'width': '80%', 'height': '600px'},
    minZoom=0.05,
    maxZoom=10,
    zoom=1,
    zoomingEnabled=True,
    pan={"x": 100, "y": 0},
    elements=[],
    layout={
        "name": "breadthfirst",
        "roots": "[id = 'defenestration']"
    },
    # stylesheet=[
    #     {
    #         'selector': 'node',
    #         'style': {
    #             'width': 10,
    #             'height': 10
    #         }
    #     }
    # ]
)

cyto_component = html.Div(cyto_graph,
                          className="bg-dark rounded-3",
                          style={"margin": "5% 5% 5% 5%"}
                          )


# Graph Info Components
clicked_num_connected = html.Pre(
    id='clicked-num-connected',
    style={
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    })


# default_stylesheet = [
#     {
#         "selector": "node",
#         "style": {
#             "width": "data(size)",
#             "height": "data(size)",
#             "background-color": "mapData(layer, 0, 3, white, blue)",
#             "content": "data(label)",
#             "font-size": "12px",
#             "text-valign": "center",
#             "text-halign": "center",
#         },
#     }
# ]


# Callbacks

# For Word Search and Depth Option

# Displaying the chosen Depth


@app.callback(Output('chosen-depth-display', 'children'),
              Input('depth-slider', 'value'))
def displayDepthOption(depth_value: int):
    return f"Chosen Depth of {depth_value}"

# On clicking of node


@app.callback(Output('clicked-num-connected', 'children'),
              Input('cytoscape-graph', 'tapNode'))
def displayTapNodeData(data: dict):
    if data:
        return json.dumps(data, indent=2)

# On Panning


@app.callback(Output("cytoscape-graph", 'pan'),
              Input("depth-slider", 'value'))
def displayPanPosition(value):
    return {"x": value*10, "y": value*10}

# On Generate


@app.callback(Output("cytoscape-graph", 'elements'),
              Input("generate", 'n_clicks'),
              Input("word-input", "value"),
              Input("depth-slider", 'value'))
def displayPanPosition(n_clicks, word_value, depth_value):
    # Cytoscape Element Generation
    if n_clicks > 0 and word_value and depth_value:
        database = Neo4jHTTPManager()
        initial_value = word_value.strip()
        word_data = set(database.get_word_data(
            initial_value, depth_value)[::-1])

        # Nodes
        nodes = [initial_value]
        for word_tuple in word_data:
            nodes.append(word_tuple[1])

        cyto_nodes = [
            {
                'data': {'id': word, 'label': word}
            }
            for word in set(nodes)
        ]

        # Edges
        cyto_edges = [
            {'data': {'source': source, 'target': target}}
            for source, target in word_data
        ]

        elements = cyto_nodes + cyto_edges
        return elements
    else:
        return []


# Layout
app.layout = html.Div(
    style={"backgroundColor": "#FFFFFF"},
    children=[
        navbar,
        word_input,
        depth_slider,
        button_generate,
        cyto_component,
        html.P("Database Connection", id='database-loading'),
        html.P("Positions", id="pan-pos"),
        clicked_num_connected
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
