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

# Graph Layout Options
layout_options = ['concentric', 'breadthfirst', 'circle', 'random']
graph_layout_options = dcc.Dropdown(
    layout_options, 'breadthfirst', id='graph-layout-options')

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
        "roots": "[id = 'defenestration']",
        # "circle": "false"
    },
    stylesheet=[
        {
            'selector': 'edge',
            'style': {
                'width': 0.1,
                'mid-target-arrow-shape': 'triangle',
                'arrow-scale': 1
            }
        },
        {
            'selector': 'node',
            'style': {
                'label': 'data(label)'
            }
        }
    ]
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
def generateGraph(n_clicks, word_value, depth_value):
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


@app.callback(Input("cytoscape-graph", 'elements'),
              Input("graph-layout-options", 'value'))
def shiftPositions(elements, layout_option):
    if layout_option == "breadthfirst" and elements != []:
        pass


# Graph Layout Picker


@app.callback(Output("cytoscape-graph", 'layout'),
              Input("graph-layout-options", 'value'),
              Input('word-input', 'value'),
              Input('cytoscape-graph', 'layout'))
def graph_layout_pick(layout_option, word_value, layout):
    if layout_option and word_value:
        new_layout = layout
        new_layout['name'] = layout_option
        if layout_option == "breadthfirst":
            new_layout['roots'] = f"[id = '{word_value}']"
            new_layout['avoidOverlap'] = 'true'
        elif layout_option == "concentric":
            new_layout['nodeDimensionsIncludeLabels'] = 'true'
        return new_layout
    else:
        return layout


# Layout
app.layout = html.Div(
    style={"backgroundColor": "#FFFFFF"},
    children=[
        navbar,
        word_input,
        depth_slider,
        graph_layout_options,
        button_generate,
        cyto_component,
        html.P("Database Connection", id='database-loading'),
        html.P("Positions", id="pan-pos"),
        clicked_num_connected
    ],
)

if __name__ == "__main__":
    app.run_server(debug=True)
