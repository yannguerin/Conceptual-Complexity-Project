import dash
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dcc

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

# StopWords Toggle

include_stopwords = dcc.Checklist(
    ['Include StopWords'], id='include-stopwords')

# Graph Layout Options
layout_options = ['concentric', 'breadthfirst', 'circle', 'random']
graph_layout_options = dcc.Dropdown(
    layout_options, 'breadthfirst', id='graph-layout-options')

# Cytoscape Graph

default_style = [
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
    stylesheet=default_style
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


# ### TEXT COMPLEXITY INDEX COMPONENTS

text_area_input = dcc.Textarea(id='complexity-text-input', value='Input Text to calculate the complexity of',
                               style={'width': '80%', 'height': 300, 'margin': '2% 10% 2% 10%'})

complexity_index_output = html.H4(
    "Complexity Index", id='complexity-index-output', style={'margin-left': '10%'})

complexity_calculations = html.Div([
    text_area_input,
    html.Button('Submit', id='submit-text-complexity',
                n_clicks=0, style={'margin-left': '10%'}),
    complexity_index_output
])
