##borrowed from https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-clinical-analytics
#key imports
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction
import dash_bootstrap_components as dbc
import base64
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
#importing the data file 

diff_df_sc = pd.read_csv('../models/diff_df_sc.csv', index_col = 0)
diff_df_exp_sc = pd.read_csv('../models/diff_df_exp_sc.csv', index_col = 0)
offer_info = pd.read_csv('../data/offer_info.csv', index_col = 0)

offer_types = list(float(i) for i in diff_df_sc.columns)
user_types = list(diff_df_sc.index)
offer_descrip = list(offer_info.columns)


diff_shared = diff_df_sc - diff_df_exp_sc
diff_shared = pd.DataFrame(StandardScaler().fit_transform(diff_shared))
diff_shared_clean = diff_shared.applymap(lambda x: 1 if (x < 0) else 0)
diff_shared.columns, diff_shared.index = offer_types, user_types
diff_shared_clean.columns, diff_shared_clean.index = offer_types, user_types

diff_agg = diff_df_sc + diff_df_exp_sc

# external CSS stylesheets
external_stylesheets = [
   dbc.themes.YETI
]


#config settings
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

server = app.server
app.config.suppress_callback_exceptions = True



# Path

# Read data
#setting the selection items to topics and diaries of interest


navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Madeline Kehl", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://www.github.com/madkehl/Starbucks",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    
)

def description_card():
    """
    OUTPUT: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5(""),
            html.Br(),
            html.H3("Recommendations based on collaborative filtering techniques, Starbucks Data"),
            html.Br(),
            html.A('This web app is designed to be a clean and simple way of visualizing the results of a rather complex analysis. The goal of this was to understand what offers would be most impactful for which demographics.  Information such as age, income, gender and years member was available for analysis as well as offers and their various characteristics.  More behind-the-scenes data cleaning and analysis, as well as other intermediary discussion is available in the Github for the project and the Jupyter notebook rendering.'),
            html.A("If you love this, please visit the full project either by clicking my name above (my Github) or viewing the full notebook here.", href = 'https://nbviewer.jupyter.org/github/madkehl/Starbucks/blob/main/web_app/models/Starbucks_full_documentation.ipynb'),
            html.Div(
                id="intro",
                children=[
                    html.Br(),
                    html.A("This interactive graph allows you to examine recommendations by demographic.  Double click labels in the legend to view demographics of interest, and use the offer selection bar to filter by offer types."),
                    html.Br(),
                    html.A('If no offers exist that meet all the criteria selected, then you will simply see all results.'),
                ],
            ),
        ],
    )


def generate_control_card():
    """
    OUTPUT: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Br(),
            html.Br(),
            html.P("Select Offer"),
            dcc.Dropdown(
                id="offer-select",
                options=[{"label": i, "value": i} for i in offer_descrip],
                value= offer_descrip[:],
                multi=True
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )

def generate_message(offer_des, reset):
    '''
    INPUT: offer descriptors, reset click

    OUTPUT: message of status of graph
    '''
    offer_t = offer_info[offer_des]
    offer_t = offer_t[offer_t.eq(1).all(axis = 1)].reset_index()
    if offer_t.shape[0] == 0:
        message = "No combinations of the current column selections exist. Showing full data."
    else:
        message = "Current selection valid. Corresponding subset of data shown."
    return(message)

def generate_bar_chart_all(offer_des, reset):
    """
    INPUT: offer descriptions reset click

    OUTPUT: interactive fig with custom results
    """
    offer_t = offer_info[offer_des]
    offer_t = offer_t[offer_t.eq(1).all(axis = 1)].reset_index()
    indexer = [float(i) for i in offer_t['offer_id']]
    bool_type = 1
    
    if offer_t.shape[0] == 0:
        offer_t = offer_info
        indexer = [float(i) for i in offer_t.index.values]
        bool_type = 0
        
    diff_shared_clean_filt = diff_shared_clean[indexer]
    
    hovertemplate = "<b> %{y}  %{x} <br><br> %{z} Recommended Offers <br><br> %{text} <b>"

    fig = go.Figure()

    for i in diff_shared_clean.index:
        bool_type = 0
        row = diff_shared_clean.loc[i]
        row_sig = row[row.values == 1]

        row_sig_filt = row_sig[row_sig.index.isin(indexer)]
   
        if(row_sig_filt.shape[0]) == 0:
            row_sig_filt = row_sig
    
        offer_types = row_sig_filt.index.values
        
    
        offer_vals = diff_agg.loc[i]
        if bool_type == 0:
            offer_vals = offer_vals[[str(i) for i in offer_types]]
        else:
            offer_vals = offer_vals[[str(i) for i in offer_types]]
            
    
        types = offer_info.loc[[float(i) for i in offer_vals.index.values]]
        types = types.mul(offer_vals.values, axis = 0)
        types_sums = types.sum(axis = 0)
        types_most_successful = types_sums[abs(types_sums).values > 0.5]
        
 
        fig.add_trace(go.Bar(x=types_most_successful.index.values, y = types_most_successful.values, name = i[2:], marker=dict(color =  types_most_successful.values, colorscale='bluered')))
                  
                      
    fig.update_layout(width = 1200, height = 600)
    fig.update_traces(marker_showscale=False)
    
    
    return(fig)

def control_card_accessory(offered_values):
    """
    OUTPUT: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.Br(),
            html.Br(),
            html.P("Select Offer"),
            dcc.Dropdown(
                id="offer-select",
                options=[{"label": i, "value": i} for i in offer_descrip],
                value= offered_values[:],
                multi=True
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer",
                children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            ),
        ],
    )
#get starting values

message = generate_message(offer_descrip, True)
starter = generate_bar_chart_all(offer_descrip, True)
control = generate_control_card()
#import images for below app

image_filename = os.getcwd() + '/diff_df_styler.png' # replace with your own image
encoded_image1 = base64.b64encode(open(image_filename, 'rb').read()).decode('ascii')

image_filename2 = os.getcwd() + '/diff_df_exp_styler.png' # replace with your own image
encoded_image2 = base64.b64encode(open(image_filename2, 'rb').read()).decode('ascii')

image_filename3 = os.getcwd() + '/df_combo_format.png' # replace with your own image
encoded_image3 = base64.b64encode(open(image_filename3, 'rb').read()).decode('ascii')

#app structure

app.layout = html.Div(
    id="app-container",
    children=[
        # Left column
        html.Div(id="nav", children = [navbar]),
        html.Div(id="left-column", className="four columns", children=[description_card()]),
        html.Div(id="control-card-div", children = [control]+
                 [html.Div(["initial child"], id="output-clientside", style={"display": "none"})],),
        html.I(id="graph-statement", children = [html.A(message)]),
        html.Div(id="right-column", className="eight columns", children = [dcc.Graph(id="offer_user_recs", figure = starter)],),
        html.Br(),
        html.A('Below is an illustration of the process used to arrive at whether or not an offer was "impactful" for a demographic.'),
        html.Br(),
        html.A('The first two tables show impact-weighted output from two FunkSVD configurations, or two different iterations of a collaborative filtering algorithm.'),
        html.A('The black and white table shows places where there was greater than mean overlap between the two experiments.  Results in white here are those you see reflected in the graph above, with the exception that they are sums between the two dataframes, instead of the differences seen here.'),
        html.Br(),
        html.Br(),
        html.Div([
            html.A(
            # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                    dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image1),  style={'height':'80%', 'width':'80%'})),
                    dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image2),  style={'height':'80%', 'width':'80%'})),
                    dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image3),  style={'height':'80%', 'width':'80%'})),
                    ],
                    align="center",
                    no_gutters=True,
                ),
             ),   
        ]),
        html.Br(),
        html.Br(),
        ],
    style={'marginBottom': 50, 'marginLeft': 25,'marginRight':25, 'marginTop': 25},
)

#this connects user interactions with backend code
@app.callback([
     Output("control-card-div", "children"),
     Output("graph-statement", "children"),
     Output("offer_user_recs", "figure")],
    [Input("offer-select", "value"),
    Input("reset-btn", "n_clicks")],
)

#this runs when user makes selections

def update_barplot(offer_d, reset_click):
    '''
    takes in offer description list from user and their reset motive
    '''
    reset = False
    # Find which one has been triggered
    ctx = dash.callback_context
    
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "reset-btn":
            offer_d = offer_descrip
            
                
    return (control_card_accessory(offer_d), generate_message(offer_d, reset), generate_bar_chart_all(offer_d, reset))




def main():
    '''
    as the main function this runs whenever the file is called
    
    it sets the port and then runs the app through the desired port
    '''
    
    if len(sys.argv) == 2: 
        from waitress import serve
        serve(server, host="0.0.0.0", port=8080)
    else:
        port = int(os.environ.get('PORT', 5000))
        app.run_server(host='0.0.0.0', port=port)
  



# Run the server
if __name__ == "__main__":
    main()
  

    
