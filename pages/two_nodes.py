from json import dumps
from collections import Counter
import time

import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dcc

from components import *
from neo4j_manager import Neo4jHTTPManager

from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))

dash.register_page(__name__, path='/Two-Word-Graph')
# Callbacks

# For Word Search and Depth Option

# Displaying the chosen Depth


@dash.callback(Output('chosen-depth-display-two-word', 'children'),
               Input('depth-slider-two-word', 'value'))
def displayDepthOption(depth_value: int) -> str:
    return f"Chosen Depth of {depth_value}"

# On clicking of node


@dash.callback(Output('cytoscape-graph-two-word', 'stylesheet'),
               Input('cytoscape-graph-two-word', 'tapNode'),
               Input("word-input-two-word-left", "value"),
               Input("word-input-two-word-right", "value"))
def displayTapNodeData(data: dict, first_word: str, second_word: str) -> dict:
    """Highlights the Nodes and Edges connected to the Tapped Node

    Args:
        data (dict): tapNode Data, containing the nodes and edges connected to the tapped node
        first_word (str): the left word input, used to highlight it green
        second_word (str): the right word input, used to highlight it green

    Returns:
        dict: Containing the updated stylesheet for the cytoscape graph
    """
    current_style = two_word_default_style.copy()
    highlight_starting_words = [{
        'selector': f'#{first_word}',
        'style': {
            'color': ' green',
            'background-color': 'green',
            'width': 50,
            'height': 50
        }
    },
        {
        'selector': f'#{second_word}',
        'style': {
            'color': 'green',
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
                'line-color': 'red',
            }
        } for edge in data["edgesData"]]
        new_node_style = [{
            'selector': f'#{edge["target"]}',
            'style': {
                'color': 'red',
                'background-color': 'red',
            }
        } for edge in data["edgesData"]]
        current_style.extend(new_edge_style)
        current_style.extend(new_node_style)
        return current_style
    else:
        return current_style

# On Generate


@dash.callback(Output("cytoscape-graph-two-word", 'elements'),
               Output("generate-two-word", 'n_clicks'),
               Input("generate-two-word", 'n_clicks'),
               Input("word-input-two-word-left", "value"),
               Input("word-input-two-word-right", "value"),
               Input("depth-slider-two-word", 'value'),
               Input('include-stopwords-two-word', 'value'))
def generateGraph(n_clicks: int, first_word: str, second_word: str, depth_value: int, include_stopwords: bool) -> list:
    """Generates the Network Graph connecting Two Words via their dictionary definitions

    Args:
        n_clicks (int): Number of clicks on the button to generate the graph
        first_word (str): The left word input value
        second_word (str): The right word input value
        depth_value (int): The depth at which to search to attempt to connect both words
        include_stopwords (bool): A boolean value to choose whether or not to include stopwords in the graph

    Returns:
        list: A list of dictionaries containing all the node and edge data for Cytoscape
        int: Returning 0 to reset the n_clicks value
    """
    # Cytoscape Element Generation
    if n_clicks > 0 and first_word and second_word and depth_value:
        database = Neo4jHTTPManager()  # Create an instance of the Neo4j Database Manager
        initial_value = first_word.strip()
        word_data = database.get_two_word_data(
            initial_value, second_word.strip(), depth_value, include_stopwords)

        # Nodes

        count_nodes = {initial_value: 1, second_word.strip(): 1}
        # for word_tuple in word_data:
        #     nodes.append(word_tuple[0])

        count_nodes.update(
            dict(Counter([source for source, _ in word_data.keys()])))

        cyto_nodes = [
            {
                'data': {'id': word, 'label': word, 'size': 25 + (size * 10)}
            }
            for word, size in count_nodes.items()
        ]

        # Edges
        cyto_edges = [
            {'data': {'source': source, 'target': target, 'weight': count}}
            for (source, target), count in word_data.items()
        ]

        elements = cyto_nodes + cyto_edges
        return elements, 0
    else:
        return [], 0

# Swap Two Words


@dash.callback(Output('word-input-two-word-right', 'value'),
               Output('word-input-two-word-left', 'value'),
               Output('two-word-swapper', 'n_clicks'),
               Input('two-word-swapper', 'n_clicks'),
               Input('word-input-two-word-right', 'value'),
               Input('word-input-two-word-left', 'value'))
def swap_two_words(n_clicks: int, right_word: str, left_word: str) -> tuple[str, str, int]:
    """Swaps the two word input values when a button is clicked

    Args:
        n_clicks (int): Number of clicks on the button
        right_word (str): The right word input value
        left_word (str): The left word input value

    Returns:
        tuple[str, str, int]: The left word, right word, and 0 clicks when button is clicked, otherwise it keeps things the same
    """
    if n_clicks and left_word and right_word:
        return str(left_word), str(right_word), 0
    else:
        return right_word, left_word, 0


# Graph Layout Picker


@dash.callback(Output("cytoscape-graph-two-word", 'layout'),
               Input("graph-layout-options-two-word", 'value'),
               Input('word-input-two-word-left', 'value'),
               Input('word-input-two-word-right', 'value'),
               Input('cytoscape-graph-two-word', 'layout'),
               Input('depth-slider-two-word', 'value'))
def graph_layout_pick(layout_option: str, first_word: str, second_word: str, layout: dict, depth: int) -> dict:
    """Callback for the dropdown menu allowing the user to choose the layout for the Cytoscape graph,
    and adding extra parameters for the layout based on the chosen layout

    Args:
        layout_option (str): The chosen layout from the dropdown
        first_word (str): The left word input value
        second_word (str): The right word input value
        layout (dict): Layout dictionary to be passed to Cytoscape
        depth (int): The chosen depth value

    Returns:
        dict: Updated layout dictionary for Cytoscape graph
    """
    if layout_option and first_word and second_word:
        new_layout = layout
        new_layout['name'] = layout_option
        # new_layout['spacingFactor'] = depth
        new_layout['avoidOverlap'] = True
        new_layout['nodeDimensionsIncludeLabels'] = 'true'
        if layout_option == "breadthfirst":
            new_layout['roots'] = f"#{first_word}"
            # new_layout['circle'] = True
            new_layout['padding'] = 50
        return new_layout
    else:
        return layout


layout = html.Div(
    children=[
        html.H1("Two Words: Graphed"),
        html.H3("Exploring how two words connect together via dictionary definitions"),
        two_word_input,
        two_word_depth_slider,
        two_word_stopword_div,
        html.H5(
            "Layout Option Dropdown: The algorithm used to determine the positions of the nodes in the graph"),
        two_word_graph_layout_options,
        two_word_button_generate,
        two_word_swapper,
        two_word_cyto_component,
        html.P("Database Connection", id='database-loading-two-word'),
        html.P("Positions", id="pan-pos-two-word"),
        two_word_clicked_num_connected
    ]
)
