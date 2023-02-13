from json import dumps

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


@dash.callback(Output('clicked-num-connected-two-word', 'children'),
               Output('cytoscape-graph-two-word', 'stylesheet'),
               Input('cytoscape-graph-two-word', 'tapNode'),
               Input("word-input-two-word-left", "value"),
               Input("word-input-two-word-right", "value"))
def displayTapNodeData(data: dict, first_word: str, second_word: str) -> tuple[str, dict]:
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
                'width': 3
            }
        } for edge in data["edgesData"]]
        new_node_style = [{
            'selector': f'#{edge["target"]}',
            'style': {
                'color': 'red',
                'background-color': 'red',
                'width': 50,
                'height': 50
            }
        } for edge in data["edgesData"]]
        current_style.extend(new_edge_style)
        current_style.extend(new_node_style)
        return dumps(len(data), indent=2), current_style
    else:
        return "", current_style

# On Panning


@dash.callback(Output("cytoscape-graph-two-word", 'pan'),
               Input("depth-slider-two-word", 'value'))
def displayPanPosition(value: int) -> dict:
    return {"x": value*10, "y": value*10}

# On Generate


@dash.callback(Output("cytoscape-graph-two-word", 'elements'),
               Input("generate-two-word", 'n_clicks'),
               Input("word-input-two-word-left", "value"),
               Input("word-input-two-word-right", "value"),
               Input("depth-slider-two-word", 'value'),
               Input('include-stopwords-two-word', 'value'))
def generateGraph(n_clicks: int, first_word: str, second_word: str, depth_value: int, include_stopwords: bool) -> list:
    # Cytoscape Element Generation
    if n_clicks > 0 and first_word and second_word and depth_value:
        database = Neo4jHTTPManager()
        initial_value = first_word.strip()
        if not include_stopwords:
            word_data = database.get_two_word_data(
                initial_value, second_word.strip(), depth_value)[::-1]
            word_data = [(source, target) for source,
                         target in word_data if source not in eng_stopwords and target not in eng_stopwords]
        else:
            word_data = database.get_two_word_data(
                initial_value, second_word.strip(), depth_value)

        # Nodes
        nodes = [initial_value, second_word.strip()]
        for word_tuple in word_data:
            nodes.append(word_tuple[0])

        cyto_nodes = [
            {
                'data': {'id': word, 'label': word}
            }
            for word in nodes
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


# Graph Layout Picker


@dash.callback(Output("cytoscape-graph-two-word", 'layout'),
               Input("graph-layout-options-two-word", 'value'),
               Input('word-input-two-word-left', 'value'),
               Input('word-input-two-word-right', 'value'),
               Input('cytoscape-graph-two-word', 'layout'),
               Input('depth-slider-two-word', 'value'))
def graph_layout_pick(layout_option: str, first_word: str, second_word: str, layout: dict, depth: int) -> dict:
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
            # Add position shifting
            # nodes.positions(shiftPositions)
        return new_layout
    else:
        return layout


layout = html.Div(
    children=[
        html.H1("Two Words: Graphed"),
        html.H3("Exploring how two words connect together via dictionary definitions"),
        two_word_input,
        two_word_depth_slider,
        two_word_include_stopwords,
        two_word_graph_layout_options,
        two_word_button_generate,
        two_word_cyto_component,
        html.P("Database Connection", id='database-loading-two-word'),
        html.P("Positions", id="pan-pos-two-word"),
        two_word_clicked_num_connected
    ]
)
