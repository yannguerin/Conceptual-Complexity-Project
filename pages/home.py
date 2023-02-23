from json import dumps
from collections import Counter
import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dcc, ctx

from components import *
from neo4j_manager import Neo4jHTTPManager

from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))

dash.register_page(__name__, path='/')

# Callbacks

# For Word Search and Depth Option

# Displaying the chosen Depth


@dash.callback(Output('chosen-depth-display', 'children'),
               Input('depth-slider', 'value'))
def displayDepthOption(depth_value: int) -> str:
    return f"Chosen Depth of {depth_value}"

# On clicking of node


@dash.callback(Output('cytoscape-graph', 'stylesheet'),
               Input('cytoscape-graph', 'tapNode'),
               Input("word-input", "value"))
def displayTapNodeData(data: dict, word_value: str) -> dict:
    """Highlights nodes and edges when a node is clicked

    Args:
        data (dict): The tapped node data
        word_value (str): The word input value

    Returns:
        dict: The updated stylesheet to highlight nodes and edges
    """
    current_style = default_style.copy()
    highlight_starting_words = [{
        'selector': f'#{word_value}',
        'style': {
            'color': ' green',
            'background-color': 'green',
            'width': 50,
            'height': 50
        }
    }]
    current_style.extend(highlight_starting_words)
    if data:
        new_edge_style = [{
            'selector': f'#{edge["id"]}',
            'style': {
                'line-color': ' red',
            }
        } for edge in data["edgesData"]]
        new_node_style = [{
            'selector': f'#{edge["target"]}',
            'style': {
                'color': ' red',
                'background-color': 'red',
            }
        } for edge in data["edgesData"]]
        current_style.extend(new_edge_style)
        current_style.extend(new_node_style)
        return current_style
    else:
        return current_style

# On Generate


@dash.callback(Output("cytoscape-graph", 'elements'),
               Output("generate", 'n_clicks'),
               Input("generate", 'n_clicks'),
               Input("word-input", "value"),
               Input("depth-slider", 'value'),
               Input('include-stopwords', 'value'))
def generateGraph(n_clicks: int, word_value: str, depth_value: int, include_stopwords: bool) -> tuple[list, int]:
    """Generates the Cytoscape graph when the Generate button is clicked

    Args:
        n_clicks (int): The number of clicks on the generate button
        word_value (str): The word input value, to start the graph from
        depth_value (int): The max depth/path length to search for
        include_stopwords (bool): Whether of not to include paths containing stopwords

    Returns:
        tuple[list, int]: The list of nodes and edges for Cytoscape graph, 0 for resetting the n_clicks value of the Generate button
    """
    # Cytoscape Element Generation
    if n_clicks > 0 and word_value and depth_value:
        database = Neo4jHTTPManager()
        initial_value = word_value.strip()
        word_data = database.get_word_data(
            initial_value, depth_value, include_stopwords)

        # Nodes
        count_nodes = {initial_value: 1}
        count_nodes.update(
            dict(Counter([source for source, _ in word_data.keys()])))
        count_nodes.update(
            dict(Counter([target for _, target in word_data.keys()])))

        cyto_nodes = [
            {
                'data': {'id': word, 'label': word, 'size': 25 + (size * 10)}
            }
            for word, size in count_nodes.items()
        ]

        # Edges
        cyto_edges = [
            {'data': {'source': source, 'target': target, 'weight': count / 2}}
            for (source, target), count in word_data.items()
        ]

        elements = cyto_nodes + cyto_edges
        return elements, 0
    else:
        return [], 0


# @app.callback(Input("cytoscape-graph", 'elements'),
#               Input("graph-layout-options", 'value'))
# def shiftPositions(elements, layout_option):
#     if layout_option == "breadthfirst" and elements != []:
#         pass


# Graph Layout Picker


@dash.callback(Output("cytoscape-graph", 'layout'),
               Input("graph-layout-options", 'value'),
               Input('word-input', 'value'),
               Input('cytoscape-graph', 'layout'),
               Input('depth-slider', 'value'))
def graph_layout_pick(layout_option: str, word_value: str, layout: dict, depth: int) -> dict:
    """A callback for the dropdown allowing the user to pick the graph layout algorithm

    Args:
        layout_option (str): The layout option chosen from the dropdown
        word_value (str): The word input value
        layout (dict): The current layout dict for Cytoscape
        depth (int): The max depth searched, used to scale the graph

    Returns:
        dict: THe updated layout dict for Cytoscape
    """
    if layout_option and word_value:
        new_layout = layout
        new_layout['name'] = layout_option
        new_layout['spacingFactor'] = depth * 3
        new_layout['avoidOverlap'] = True
        new_layout['nodeDimensionsIncludeLabels'] = True
        if layout_option == "breadthfirst":
            new_layout['roots'] = f"[id = '{word_value}']"
            new_layout['circle'] = True
            new_layout['padding'] = 50
            # Add position shifting
            # nodes.positions(shiftPositions)
        return new_layout
    else:
        return layout


@dash.callback(Output("cytoscape-graph", "generateImage"),
               Input("download", "n_clicks"),
               Input('word-input', 'value'),
               Input('depth-slider', 'value'),
               prevent_initial_call=True)
def download_graph_image(n_clicks: int, word: str, depth_value: int) -> dict:
    """Downloads a jpg image of the graph, following the click of the download button
        Sets the filename to the word and depth values

    Args:
        n_clicks (int): Number of clicks to the download button
        word (str): Word input value, for filename
        depth_value (int): Depth value, for filename and scaling 

    Returns:
        dict: A dictionary of settings for the downloading, specifying the type and filename
    """
    action = "store"
    ftype = "jpg"
    download_dict = {
        "type": ftype,
        "action": action
    }
    if ctx.triggered and ctx.triggered_id == "download" and word:
        download_dict["action"] = "download"
        download_dict["ftype"] = "jpg"
        filename = f"{word}_{depth_value}"
        download_dict["filename"] = filename
        download_dict["options"] = {
            "scale": depth_value * 2
        }

    return download_dict


layout = html.Div(
    children=[
        html.H1("One Word: Graphed"),
        html.H3("Exploring the words connected to a word via dictionary definitions"),
        word_input,
        depth_slider,
        stopword_div,
        html.H5(
            "Layout Option Dropdown: The algorithm used to determine the positions of the nodes in the graph"),
        graph_layout_options,
        button_generate,
        download_button,
        cyto_component
    ]
)
