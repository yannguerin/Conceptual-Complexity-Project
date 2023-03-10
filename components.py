import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import html, dcc

# Layout Components

# General Scaffolding

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Home',
                    href='/')),
        dbc.NavItem(dbc.NavLink('Complexity Index',
                    href='/Complexity-Index')),
        dbc.NavItem(dbc.NavLink('Two Word Graph',
                    href='/Two-Word-Graph'))
    ],
    brand="Concept Complexity",
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

button_generate = dbc.Button(
    'Generate Graph', color="primary", id='generate', n_clicks=0)

# StopWords Toggle

include_stopwords = dcc.Checklist(
    ['Include StopWords'], id='include-stopwords')

stopword_tooltip = dbc.Tooltip(
    "Stopwords are words that are (often) insignificant to the definition of a word. Stopwords include: the, at, a, an, but...",
    target='include-stopwords',
    placement='top-start')

stopword_div = html.Div(children=[
    include_stopwords,
    stopword_tooltip
])


# Graph Layout Options
layout_options = ['concentric', 'breadthfirst', 'circle', 'random']
graph_layout_options = dcc.Dropdown(
    layout_options, 'breadthfirst', id='graph-layout-options')

# Cytoscape Graph

default_style = [
    {
        'selector': 'edge',
        'style': {
            'width': 'data(weight)',
            'mid-target-arrow-shape': 'triangle',
            'arrow-scale': 1
        }
    },
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'width': 'data(size)',
            'height': 'data(size)'
        }
    }
]

cyto_graph = cyto.Cytoscape(
    id='cytoscape-graph',
    style={'width': '80%', 'height': '1000px'},
    minZoom=0.01,
    maxZoom=10,
    zoom=1,
    zoomingEnabled=True,
    pan={"x": 0, "y": 0},
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

download_button = dbc.Button(
    "Download Graph Image", color='primary', id='download', style={"margin-right": "10%", "float": "right"})

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
    "Complexity Index:", id='complexity-index-output')

unknown_word_list = html.P(
    children="Unknown Words/Terms: ", id='unknown-word-list', style={'margin-left': '10%'})

use_wikipedia_summaries_checkbox = dcc.Checklist(
    ['Replace Unknown Words/Terms with Wikipedia Summaries (if available)'], id='use-wikipedia-summaries', style={"float": "right", "margin-right": "10%", "margin-top": "5px"})

complexity_calculations = html.Div([
    text_area_input,
    html.Div(children=[dbc.Button('Submit', color="primary", id='submit-text-complexity',
                                  n_clicks=0, style={'margin-left': '10%'}),
                       use_wikipedia_summaries_checkbox]
             ),
    complexity_index_output,
    unknown_word_list
])

#
# ### TWO WORD GRAPH COMPONENTS
#

# Inputs
# Word Search
two_word_input = html.Div(
    [
        dbc.Input(id="word-input-two-word-left",
                  placeholder="Search for First Word", type="text"),
        dbc.Input(id="word-input-two-word-right",
                  placeholder="Search for Second Word", type="text"),
        html.Br()
    ],
    id="two-word-input-div"
)
# Depth Option
two_word_depth_slider = html.Div([
    html.H6("Pick the Recursive Depth of the Concept Graph",
            style={"margin-left": "2%"}),
    dcc.Slider(1, 5, 1,
               value=3,
               id='depth-slider-two-word'
               ),
    dbc.Badge("Chosen Depth of 2", color="info",
              id='chosen-depth-display-two-word')
],
    style={"margin": "2% 10% 2% 10%"}
)

# Generate Button

two_word_button_generate = dbc.Button(
    'Generate Graph', color="primary", id='generate-two-word', n_clicks=0)

two_word_swapper = dbc.Button(
    "Swap the Word Inputs", color='primary', id='two-word-swapper')

two_word_download_button = dbc.Button(
    "Download Graph Image", color='primary', id='two-word-download')

two_word_button_div = html.Div(children=[
    two_word_button_generate,
    two_word_swapper,
    two_word_download_button
],
    style={'margin-top': "5%", 'margin-right': "10%", "text-align": "center"}
)

# StopWords Toggle

two_word_include_stopwords = dcc.Checklist(
    ['Include StopWords'], id='include-stopwords-two-word')

two_word_stopword_tooltip = dbc.Tooltip(
    "Stopwords are words that are (often) insignificant to the definition of a word. Stopwords include: the, at, a, an, but...",
    target='include-stopwords-two-word',
    placement='top-start')

two_word_stopword_div = html.Div(children=[
    two_word_include_stopwords,
    two_word_stopword_tooltip
])

# Graph Layout Options
two_word_layout_options = ['concentric', 'breadthfirst', 'circle', 'random']
two_word_graph_layout_options = dcc.Dropdown(
    two_word_layout_options, 'breadthfirst', id='graph-layout-options-two-word')

# Cytoscape Graph

two_word_default_style = [
    {
        'selector': 'edge',
        'style': {
            'width': 'data(weight)',
            'mid-target-arrow-shape': 'triangle',
            'arrow-scale': 1
        }
    },
    {
        'selector': 'node',
        'style': {
            'label': 'data(label)',
            'width': 'data(size)',
            'height': 'data(size)'
        }
    }
]

two_word_cyto_graph = cyto.Cytoscape(
    id='cytoscape-graph-two-word',
    style={'width': '100%', 'height': '1000px'},
    minZoom=0.05,
    maxZoom=10,
    zoom=1,
    zoomingEnabled=True,
    pan={"x": 0, "y": 0},
    elements=[],
    layout={
        "name": "breadthfirst",
        "roots": "[id = 'defenestration']",
        # "circle": "false"
    },
    stylesheet=two_word_default_style
)

two_word_cyto_component = html.Div(two_word_cyto_graph,
                                   className="bg-dark rounded-3",
                                   style={"margin": "5% 5% 5% 5%"}
                                   )


# Graph Info Components
two_word_clicked_num_connected = html.Pre(
    id='clicked-num-connected-two-word',
    style={
        'border': 'thin lightgrey solid',
    })
