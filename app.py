from collections import Counter
import json
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import networkx as nx

import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dcc

from neo4j_manager import Neo4jHTTPManager
from components import *

from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Callbacks

# For Word Search and Depth Option

# Displaying the chosen Depth


@app.callback(Output('chosen-depth-display', 'children'),
              Input('depth-slider', 'value'))
def displayDepthOption(depth_value: int):
    return f"Chosen Depth of {depth_value}"

# On clicking of node


@app.callback(Output('clicked-num-connected', 'children'),
              Output('cytoscape-graph', 'stylesheet'),
              Input('cytoscape-graph', 'tapNode'))
def displayTapNodeData(data: dict):
    current_style = default_style
    if data:
        new_edge_style = [{
            'selector': f'#{edge["id"]}',
            'style': {
                'line-color': ' red',
                'width': 3
            }
        } for edge in data["edgesData"]]
        new_node_style = [{
            'selector': f'#{edge["target"]}',
            'style': {
                'color': ' red',
                'background-color': 'red',
                'width': 100,
                'height': 100
            }
        } for edge in data["edgesData"]]
        current_style.extend(new_edge_style)
        current_style.extend(new_node_style)
        return json.dumps(data, indent=2), current_style
    else:
        return "", default_style

# On Panning


@app.callback(Output("cytoscape-graph", 'pan'),
              Input("depth-slider", 'value'))
def displayPanPosition(value):
    return {"x": value*10, "y": value*10}

# On Generate


@app.callback(Output("cytoscape-graph", 'elements'),
              Input("generate", 'n_clicks'),
              Input("word-input", "value"),
              Input("depth-slider", 'value'),
              Input('include-stopwords', 'value'))
def generateGraph(n_clicks, word_value, depth_value, include_stopwords):
    # Cytoscape Element Generation
    if n_clicks > 0 and word_value and depth_value:
        database = Neo4jHTTPManager()
        initial_value = word_value.strip()
        if not include_stopwords:
            word_data = database.get_word_data(
                initial_value, depth_value)[::-1]
            word_data = set([(source, target) for source,
                            target in word_data if source not in eng_stopwords and target not in eng_stopwords])
        else:
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


# @app.callback(Input("cytoscape-graph", 'elements'),
#               Input("graph-layout-options", 'value'))
# def shiftPositions(elements, layout_option):
#     if layout_option == "breadthfirst" and elements != []:
#         pass


# Graph Layout Picker


@app.callback(Output("cytoscape-graph", 'layout'),
              Input("graph-layout-options", 'value'),
              Input('word-input', 'value'),
              Input('cytoscape-graph', 'layout'),
              Input('depth-slider', 'value'))
def graph_layout_pick(layout_option, word_value, layout, depth):
    if layout_option and word_value:
        new_layout = layout
        new_layout['name'] = layout_option
        new_layout['spacingFactor'] = depth * 5
        new_layout['avoidOverlap'] = True
        new_layout['nodeDimensionsIncludeLabels'] = 'true'
        if layout_option == "breadthfirst":
            new_layout['roots'] = f"[id = '{word_value}']"
            new_layout['circle'] = True
            new_layout['padding'] = 50
            # Add position shifting
            # nodes.positions(shiftPositions)
        return new_layout
    else:
        return layout


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
# Layout
app.layout = html.Div(
    style={"backgroundColor": "#FFFFFF"},
    children=[
        navbar,
        word_input,
        depth_slider,
        include_stopwords,
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
