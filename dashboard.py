import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import math

def calc_bowler_columns (df, plus_stats):
    
    # df['RUNS'] = df['RUNS'] \
    #                                             - df['EXTRA RUNS']
    df['OVERS'] = np.floor(df['DELIVERED'] / 6) + df['DELIVERED'] % 6 / 10
    df['TRUE_OVERS'] = df['DELIVERED'] / 6
    df['ECONOMY'] = round(df['RUNS'] / df['TRUE_OVERS'], 2)
    df['WICKET RATE'] = round(df['WICKET'] / df['TRUE_OVERS'], 2)
    df['DOT RATE'] = round(df['DOT'] / df['TRUE_OVERS'], 2)
    df['WIDE RATE'] = round(df['WIDE BALLS'] / df['TRUE_OVERS'], 2)
    df = df.merge(df.groupby('SEASON')[['ECONOMY', 'WICKET RATE', 'DOT RATE', 'WIDE RATE']]
                  .transform('mean')
                  .rename(columns={'ECONOMY' : 'season_mean_economy',
                                   'WICKET RATE' : 'season_mean_wicket',
                                   'DOT RATE' : 'season_mean_dot',
                                   'WIDE RATE' : 'season_mean_wide'}),
                              left_index = True,
                              right_index = True)
    
    if plus_stats == True:
        df['ECONOMY+'] = round(df['season_mean_economy'] \
                                            / df['ECONOMY'] * 100, 0)
        df['WICKET RATE+'] = round(df['WICKET RATE'] \
                                            / df['season_mean_wicket'] * 100, 0)
        df['DOT RATE+'] = round(df['DOT RATE'] \
                                            / df['season_mean_dot'] * 100, 0)
        df['WIDE RATE+'] = round(df['season_mean_wide'] \
                                            / df['WIDE RATE'] * 100, 0)
        
    df.drop(columns = ['TRUE_OVERS',
                                        'season_mean_economy',
                                        'season_mean_wicket',
                                        'season_mean_dot',
                                        'season_mean_wide'], inplace = True)
    overs = df.pop('OVERS') # move overs to second column
    df.insert = df.insert(1, overs.name, overs)
    df = df.reset_index()

    return df

def calc_batsman_columns (df, plus_stats):
    
    df.rename(columns = {'DELIVERED' : 'BALLS FACED',
                                           'GAME' : 'GAMES'}, inplace = True)
    df['RUNS'] = df['RUNS'] - df['EXTRA RUNS']
    df['STRIKE RATE'] = round(df['RUNS'] / df['BALLS FACED'] * 100, 1)
    df['AVG / INNINGS'] = round(df['RUNS'] / df['INNINGS BATTED'], 2)
    df = df.merge(df.groupby('SEASON')[['STRIKE RATE', 'AVG / INNINGS']]
                  .transform('mean')
                  .rename(columns={'STRIKE RATE' : 'season_mean_sr',
                                   'AVG / INNINGS' : 'season_mean_api'}),
                              left_index = True,
                              right_index = True)
    
    if plus_stats == True:
        df['STRIKE RATE+'] = round(df['STRIKE RATE'] \
                                                / df['season_mean_sr'] * 100, 0)
        df['AVG / INNINGS+'] = round(df['AVG / INNINGS'] \
                                                / df['season_mean_api'] * 100, 0)
        
    df.drop(columns = ['season_mean_sr', 'season_mean_api'], inplace = True)
    df = df.reset_index()

    return df



sheet_id = '1NfqXgq2l5vJw2M5ffCLv2zQsXy3iOqak6IAEe3U0AG4'
    
raw_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

full_data = raw_data.copy(deep=True)

full_data.loc[full_data['BATSMAN'] == 'Joez McFly', ['BATSMAN']] = 'Joez Mcfly'

full_data['DELIVERED'] = np.where(full_data['BALL'] != 'WIDE', 1, 0)
full_data['DOT'] = np.where((full_data['RUNS'] == 0) & 
                             (full_data['WICKET'].isna() == True), 1, 0)
full_data['WIDE BALLS'] = np.where(full_data['BALL'] == 'WIDE', 1, 0)
full_data['EXTRA RUNS'] = full_data['WIDE BALLS'] * full_data['RUNS']
full_data["4's"] = np.where(full_data['RUNS'] == 4, 1, 0)
full_data["6's"] = np.where(full_data['RUNS'] == 6, 1, 0)

full_data['INNINGS BATTED'] = full_data['GAME'].astype(str) + full_data['INNING'].astype(str)

grouped_bowler_data = full_data.groupby(['SEASON', 'BOWLER']).agg({'DELIVERED' : 'sum',
                                                                   'RUNS' : 'sum',
                                                                   'WICKET' : 'count',
                                                                   'DOT' : 'sum',
                                                                   'WIDE BALLS' : 'sum',
                                                                   'EXTRA RUNS' : 'sum',
                                                                   "4's" : 'sum',
                                                                   "6's" : 'sum'
                                                          })

grouped_bowler_data = calc_bowler_columns(grouped_bowler_data, plus_stats = True)

    
grouped_batsman_data = full_data.groupby(['SEASON', 'BATSMAN']).agg({'GAME' : 'nunique',
                                                                     'INNINGS BATTED' : 'nunique',
                                                                     'DELIVERED' : 'sum',
                                                                   'RUNS' : 'sum',
                                                                   'WICKET' : 'count',
                                                                   'DOT' : 'sum',
                                                                   'WIDE BALLS' : 'sum',
                                                                   'EXTRA RUNS' : 'sum',
                                                                   "4's" : 'sum',
                                                                   "6's" : 'sum'
                                                          })


grouped_batsman_data = calc_batsman_columns(grouped_batsman_data,  plus_stats = True)


grouped_bowling_team_data = full_data.groupby(['SEASON', 'BOWLING TEAM']).agg({'DELIVERED' : 'sum',
                                                                   'RUNS' : 'sum',
                                                                   'WICKET' : 'count',
                                                                   'DOT' : 'sum',
                                                                   'WIDE BALLS' : 'sum',
                                                                   'EXTRA RUNS' : 'sum',
                                                                   "4's" : 'sum',
                                                                   "6's" : 'sum'
                                                          })

grouped_bowling_team_data = calc_bowler_columns(grouped_bowling_team_data, plus_stats = False)

    
grouped_batting_team_data = full_data.groupby(['SEASON', 'BATTING TEAM']).agg({'GAME' : 'nunique',
                                                                     'INNINGS BATTED' : 'nunique',
                                                                     'DELIVERED' : 'sum',
                                                                   'RUNS' : 'sum',
                                                                   'WICKET' : 'count',
                                                                   'DOT' : 'sum',
                                                                   'WIDE BALLS' : 'sum',
                                                                   'EXTRA RUNS' : 'sum',
                                                                   "4's" : 'sum',
                                                                   "6's" : 'sum'
                                                          })


grouped_batting_team_data = calc_batsman_columns(grouped_batting_team_data,  plus_stats = False)

# Initialize the Dash app
#app = dash.Dash(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions = True)
server = app.server

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
#         html.H2("Menu", className="display-4"),
#         html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Player Stats", href="/", active="exact"),
                dbc.NavLink("Team Stats", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

player_page = html.Div([
            html.H1("Ball in Play Dashboard", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 20, 'font-family': 'Arial, sans-serif'}),
            html.H2("Players Stats", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 20, 'font-family': 'Arial, sans-serif'}),
    
            dcc.Tabs([
                # Tab for Bowler Data
                dcc.Tab(label='Bowler Stats',
                        style={'fontSize': 20, 'color': '#4CAF50'},
                        selected_style={'fontSize': 20, 'color': '#4CAF50', 'fontWeight': 'bold'},
                        children=[
                    html.Br(),
                    html.Label("Select Season:", style={'fontSize': 16, 'color': '#333'}),
                    html.Br(),
                    html.Br(),
                    dcc.Checklist(
                        id='season-toggle-bowler',
                        options=[
                            {'label': col, 'value': col} for col in grouped_bowler_data['SEASON'].unique()
                        ],
                        value=grouped_bowler_data['SEASON'].unique(),
                        style={'marginBottom': 20, 'color': '#333'}
                    ),
                    html.Br(),

                    html.Label("Select Bowler(s):", style={'fontSize': 16, 'color': '#333'}),
                    html.Button('Select All', id = 'select-all-bowlers', n_clicks = 0, style = {'fintSize': 16, 'marginBottom': 20}),
                    html.Button('Deselect All', id = 'deselect-all-bowlers', n_clicks = 0, style = {'fintSize': 16, 'marginBottom': 20}),        
                    dcc.Checklist(
                        id='bowler-dropdown',
                        options=[
                            {'label': category, 'value': category} for category in grouped_bowler_data['BOWLER'].unique()
                        ],
                        value=grouped_bowler_data['BOWLER'].unique().tolist(),
                        #multi=True,
                        #inline = True, 
                        style={'marginBottom': 20, 'columnCount': 4}
                    ),
                          
                    html.Label("Over Minimum:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Input(
                        id='bowler-minimum',
                        type = 'number',
                        value=0,
                    ),

                    html.H3("Bowler Data Table", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 10}),
                    dash_table.DataTable(
                        id='data-table-bowler',
                        columns=[
                            {"name": i, "id": i} for i in grouped_bowler_data.columns
                        ],
                        data=grouped_bowler_data.to_dict('records'),
                        style_table={'overflowX': 'auto',
                                     'border': '2px solid #4CAF50',
                                     'boxShadow': '0px 0px 10px #888888',
                                     'minWidth': '100%'},
                        style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                        style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                        sort_action='native',  # 'native' enables sorting on the client side
                        sort_mode='multi',  # 'multi' allows sorting by multiple columns
                        fixed_columns={'headers': True, 'data': 2}
                    ),
                    #style={'width': '100%'}

                    html.Div(style={'marginBottom': 40}),

                    # Dropdown for Y-axis selection
                    html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Dropdown(
                        id='y-axis-dropdown-bowler',
                        options=[
                            {'label': col, 'value': col} for col in grouped_bowler_data.columns if col not in ['SEASON', 'BOWLER']
                        ],
                        value='DELIVERED',
                        style={'marginBottom': 20}
                    ),

                    # Bar chart
                    dcc.Graph(
                        id='bar-chart-bowler',
                        style={'height': '400px'},
                    ),

                    html.Div(style={'marginBottom': 40}),

                    # Dropdown for X-axis selection
                    html.Label("Select X-axis:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Dropdown(
                        id='x-axis-scatter-dropdown-bowler',
                        options=[
                            {'label': col, 'value': col} for col in grouped_bowler_data.columns if col not in ['SEASON', 'BOWLER']
                        ],
                        value='DELIVERED',
                        style={'marginBottom': 20}
                    ),

                    # Dropdown for Y-axis selection
                    html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Dropdown(
                        id='y-axis-scatter-dropdown-bowler',
                        options=[
                            {'label': col, 'value': col} for col in grouped_bowler_data.columns if col not in ['SEASON', 'BOWLER']
                        ],
                        value='WICKET',
                        style={'marginBottom': 20}
                    ),

                    # Radio Button for Selecting Coloring Method      
                    html.Label("Select Coloring Method:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.RadioItems(['Season', 'Overs Bowled'],
                        value='Season',
                        style={'marginBottom': 20},
                        id='scatter-color-bowler'
                    ),

                    # Scatter Plot
                    dcc.Graph(
                        id='scatter-plot-bowler',
                        figure={
                            'data': [],
                            'layout': {
                                'xaxis': {'title': 'X-Axis'},
                                'yaxis': {'title': 'Y-Axis'},
                                'hovermode': 'closest',
                            }
                        }
                    )
                ]),

                # Tab for Batsman Data
                dcc.Tab(label='Batsman Stats',
                        style={'fontSize': 20, 'color': '#4CAF50'},
                        selected_style={'fontSize': 20, 'color': '#4CAF50', 'fontWeight': 'bold'},
                        children=[
                    html.Br(),
                    html.Label("Select Season:", style={'fontSize': 16, 'color': '#333'}),
                    html.Br(),
                    html.Br(),
                    dcc.Checklist(
                        id='season-toggle-batsman',
                        options=[
                            {'label': col, 'value': col} for col in grouped_batsman_data['SEASON'].unique()
                        ],
                        value=grouped_batsman_data['SEASON'].unique(),
                        style={'marginBottom': 20, 'color': '#333'}
                    ),
                    html.Br(),

                    html.Label("Select Batsman(s):", style={'fontSize': 16, 'color': '#333'}),
                    html.Button('Select All', id = 'select-all-batsman', n_clicks = 0, style = {'fintSize': 16, 'marginBottom': 20}),
                    html.Button('Deselect All', id = 'deselect-all-batsman', n_clicks = 0, style = {'fintSize': 16, 'marginBottom': 20}), 
                    dcc.Checklist(
                        id='batsman-dropdown',
                        options=[
                            {'label': category, 'value': category} for category in grouped_batsman_data['BATSMAN'].unique()
                        ],
                        value=grouped_batsman_data['BATSMAN'].unique().tolist(),
                        #multi=True,
                        #inline = True,
                        style={'marginBottom': 20, 'columnCount': 4}
                    ),
                    
                    html.Label("Innings Batted Minimum:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Input(
                        id='batsman-minimum',
                        type = 'number',
                        value=0,
                    ),
                            
                    html.H3("Batsman Data Table", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 10}),
                    dash_table.DataTable(
                        id='data-table-batsman',
                        columns=[
                            {"name": i, "id": i} for i in grouped_batsman_data.columns
                        ],
                        data=grouped_batsman_data.to_dict('records'),
                        style_table={'overflowX': 'auto',
                                     'border': '2px solid #4CAF50',
                                     'boxShadow': '0px 0px 10px #888888',
                                     'minWidth': '100%'},
                        style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                        style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                        sort_action='native',  # 'native' enables sorting on the client side
                        sort_mode='multi',  # 'multi' allows sorting by multiple columns
                        fixed_columns={'headers': True, 'data': 2}
                    ),

                    html.Div(style={'marginBottom': 40}),

                    # Dropdown for Y-axis selection
                    html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Dropdown(
                        id='y-axis-dropdown-batsman',
                        options=[
                            {'label': col, 'value': col} for col in grouped_batsman_data.columns if col not in ['SEASON', 'BATSMAN']
                        ],
                        value='BALLS FACED',
                        style={'marginBottom': 20}
                    ),

                    # Bar chart
                    dcc.Graph(
                        id='bar-chart-batsman',
                        style={'height': '400px'},
                    ),

                    html.Div(style={'marginBottom': 40}),

                    # Dropdown for X-axis selection
                    html.Label("Select X-axis:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Dropdown(
                        id='x-axis-scatter-dropdown-batsman',
                        options=[
                            #{'label': 'DELIVERED', 'value': 'DELIVERED'}
                            #{'label': col, 'value': col} for col in grouped_bowler_data.columns
                            {'label': col, 'value': col} for col in grouped_batsman_data.columns if col not in ['SEASON', 'BATSMAN']
                        ],
                        value='BALLS FACED',
                        style={'marginBottom': 20}
                    ),

                    # Dropdown for Y-axis selection
                    html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.Dropdown(
                        id='y-axis-scatter-dropdown-batsman',
                        options=[
                            #{'label': 'DELIVERED', 'value': 'DELIVERED'}
                            #{'label': col, 'value': col} for col in grouped_bowler_data.columns
                            {'label': col, 'value': col} for col in grouped_batsman_data.columns if col not in ['SEASON', 'BATSMAN']
                        ],
                        value='WICKET',
                        style={'marginBottom': 20}
                    ),

                    # Radio Button for Selecting Coloring Method      
                    html.Label("Select Coloring Method:", style={'fontSize': 16, 'color': '#333'}),
                    dcc.RadioItems(['Season', 'Innings Batted'],
                        value='Season',
                        style={'marginBottom': 20},
                        id='scatter-color-batsman'
                    ),

                    # Scatter Plot
                    dcc.Graph(
                        id='scatter-plot-batsman',
                        figure={
                            'data': [],
                            'layout': {
                                'xaxis': {'title': 'X-Axis'},
                                'yaxis': {'title': 'Y-Axis'},
                                'hovermode': 'closest',
                            }
                        }
                    )
                ])
            ])
        ], style={'font-family': 'Arial, sans-serif'}) #, 'width': '90%', 'margin': 'auto'})


team_page = html.Div([
        html.H1("Ball in Play Dashboard", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 20, 'font-family': 'Arial, sans-serif'}),
        html.H2("Team Stats", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 20, 'font-family': 'Arial, sans-serif'}),

        dcc.Tabs([
            # Tab for Bowler Data
            dcc.Tab(label='Bowling Team Stats',
                    style={'fontSize': 20, 'color': '#4CAF50'},
                    selected_style={'fontSize': 20, 'color': '#4CAF50', 'fontWeight': 'bold'},
                    children=[
                        html.Br(),
                        html.Label("Select Season:", style={'fontSize': 16, 'color': '#333'}),
                        html.Br(),
                        html.Br(),
                        dcc.Checklist(
                            id='season-toggle-bowler-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_bowling_team_data['SEASON'].unique()
                            ],
                            value=grouped_bowling_team_data['SEASON'].unique(),
                            style={'marginBottom': 20, 'color': '#333'}
                        ),
                        html.Br(),

                        html.Label("Select Team:", style={'fontSize': 16, 'color': '#333'}),
                        html.Button('Select All', id='select-all-bowlers-team', n_clicks=0,
                                    style={'fintSize': 16, 'marginBottom': 20}),
                        html.Button('Deselect All', id='deselect-all-bowlers-team', n_clicks=0,
                                    style={'fintSize': 16, 'marginBottom': 20}),
                        dcc.Checklist(
                            id='bowler-dropdown-team',
                            options=[
                                {'label': category, 'value': category} for category in
                                grouped_bowling_team_data['BOWLING TEAM'].unique()
                            ],
                            value=grouped_bowling_team_data['BOWLING TEAM'].unique().tolist(),
                            # multi=True,
                            # inline = True,
                            style={'marginBottom': 20, 'columnCount': 4}
                        ),

                        html.H3("Bowling Team Data Table", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 10}),
                        dash_table.DataTable(
                            id='data-table-bowler-team',
                            columns=[
                                {"name": i, "id": i} for i in grouped_bowling_team_data.columns
                            ],
                            data=grouped_bowling_team_data.to_dict('records'),
                            style_table={'overflowX': 'auto',
                                         'border': '2px solid #4CAF50',
                                         'boxShadow': '0px 0px 10px #888888',
                                         'minWidth': '100%'},
                            style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'textAlign': 'center',
                                          'font-family': 'Arial, sans-serif'},
                            style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                            sort_action='native',  # 'native' enables sorting on the client side
                            sort_mode='multi',  # 'multi' allows sorting by multiple columns
                            fixed_columns={'headers': True, 'data': 2}
                        ),

                        html.Div(style={'marginBottom': 40}),

                        # Dropdown for Y-axis selection
                        html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.Dropdown(
                            id='y-axis-dropdown-bowler-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_bowling_team_data.columns if
                                col not in ['SEASON', 'BOWLING TEAM']
                            ],
                            value='DELIVERED',
                            style={'marginBottom': 20}
                        ),

                        # Bar chart
                        dcc.Graph(
                            id='bar-chart-bowler-team',
                            style={'height': '400px'},
                        ),

                        html.Div(style={'marginBottom': 40}),

                        # Dropdown for X-axis selection
                        html.Label("Select X-axis:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.Dropdown(
                            id='x-axis-scatter-dropdown-bowler-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_bowling_team_data.columns if
                                col not in ['SEASON', 'BOWLING TEAM']
                            ],
                            value='DELIVERED',
                            style={'marginBottom': 20}
                        ),

                        # Dropdown for Y-axis selection
                        html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.Dropdown(
                            id='y-axis-scatter-dropdown-bowler-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_bowling_team_data.columns if
                                col not in ['SEASON', 'BOWLING TEAM']
                            ],
                            value='WICKET',
                            style={'marginBottom': 20}
                        ),

                        # Radio Button for Selecting Coloring Method
                        html.Label("Select Coloring Method:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.RadioItems(id='scatter-color-bowler-team',
                                       options=[{'label': 'Season', 'value': 'Season'}, {'label': 'Overs Bowled', 'value': 'Overs Bowled'}],
                                       value='Season',
                                       style={'marginBottom': 20}
                                       ),

                        # Scatter Plot
                        dcc.Graph(
                            id='scatter-plot-bowler-team',
                            figure={
                                'data': [],
                                'layout': {
                                    'xaxis': {'title': 'X-Axis'},
                                    'yaxis': {'title': 'Y-Axis'},
                                    'hovermode': 'closest',
                                }
                            }
                        )
                    ]),

            # Tab for Batsman Data
            dcc.Tab(label='Batting Team Stats',
                    style={'fontSize': 20, 'color': '#4CAF50'},
                    selected_style={'fontSize': 20, 'color': '#4CAF50', 'fontWeight': 'bold'},
                    children=[
                        html.Br(),
                        html.Label("Select Season:", style={'fontSize': 16, 'color': '#333'}),
                        html.Br(),
                        html.Br(),
                        dcc.Checklist(
                            id='season-toggle-batsman-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_batting_team_data['SEASON'].unique()
                            ],
                            value=grouped_batting_team_data['SEASON'].unique(),
                            style={'marginBottom': 20, 'color': '#333'}
                        ),
                        html.Br(),

                        html.Label("Select Batsman(s):", style={'fontSize': 16, 'color': '#333'}),
                        html.Button('Select All', id='select-all-batsman-team', n_clicks=0,
                                    style={'fintSize': 16, 'marginBottom': 20}),
                        html.Button('Deselect All', id='deselect-all-batsman-team', n_clicks=0,
                                    style={'fintSize': 16, 'marginBottom': 20}),
                        dcc.Checklist(
                            id='batsman-dropdown-team',
                            options=[
                                {'label': category, 'value': category} for category in
                                grouped_batting_team_data['BATTING TEAM'].unique()
                            ],
                            value=grouped_batting_team_data['BATTING TEAM'].unique().tolist(),
                            # multi=True,
                            # inline = True,
                            style={'marginBottom': 20, 'columnCount': 4}
                        ),

                        html.H3("Batsman Data Table", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 10}),
                        dash_table.DataTable(
                            id='data-table-batsman-team',
                            columns=[
                                {"name": i, "id": i} for i in grouped_batting_team_data.columns
                            ],
                            data=grouped_batting_team_data.to_dict('records'),
                            style_table={'overflowX': 'auto',
                                         'border': '2px solid #4CAF50',
                                         'boxShadow': '0px 0px 10px #888888',
                                         'minWidth': '100%'},
                            style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'textAlign': 'center',
                                          'font-family': 'Arial, sans-serif'},
                            style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                            sort_action='native',  # 'native' enables sorting on the client side
                            sort_mode='multi',  # 'multi' allows sorting by multiple columns
                            fixed_columns={'headers': True, 'data': 2}
                        ),

                        html.Div(style={'marginBottom': 40}),

                        # Dropdown for Y-axis selection
                        html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.Dropdown(
                            id='y-axis-dropdown-batsman-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_batting_team_data.columns if
                                col not in ['SEASON', 'BATTING TEAM']
                            ],
                            value='BALLS FACED',
                            style={'marginBottom': 20}
                        ),

                        # Bar chart
                        dcc.Graph(
                            id='bar-chart-batsman-team',
                            style={'height': '400px'},
                        ),

                        html.Div(style={'marginBottom': 40}),

                        # Dropdown for X-axis selection
                        html.Label("Select X-axis:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.Dropdown(
                            id='x-axis-scatter-dropdown-batsman-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_batting_team_data.columns if
                                col not in ['SEASON', 'BATTING TEAM']
                            ],
                            value='BALLS FACED',
                            style={'marginBottom': 20}
                        ),

                        # Dropdown for Y-axis selection
                        html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.Dropdown(
                            id='y-axis-scatter-dropdown-batsman-team',
                            options=[
                                {'label': col, 'value': col} for col in grouped_batting_team_data.columns if
                                col not in ['SEASON', 'BATTING TEAM']
                            ],
                            value='WICKET',
                            style={'marginBottom': 20}
                        ),

                        # Radio Button for Selecting Coloring Method
                        html.Label("Select Coloring Method:", style={'fontSize': 16, 'color': '#333'}),
                        dcc.RadioItems(id='scatter-color-batsman-team',
                                       options=[{'label': 'Season', 'value': 'Season'}, {'label': 'Innings Batted', 'value': 'Innings Batted'}],
                                       value='Season',
                                       style={'marginBottom': 20}
                                       ),

                        # Scatter Plot
                        dcc.Graph(
                            id='scatter-plot-batsman-team',
                            figure={
                                'data': [],
                                'layout': {
                                    'xaxis': {'title': 'X-Axis'},
                                    'yaxis': {'title': 'Y-Axis'},
                                    'hovermode': 'closest',
                                }
                            }
                        )
                    ])
        ])
    ], style={'font-family': 'Arial, sans-serif'})  # , 'width': '90%', 'margin': 'auto'})


content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])



######## Page Callback ########

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
#     if pathname == "/":
#         return html.P("This is the content of the home page!")
    if pathname == "/":
        # Define the layout of the app with tabs
        return player_page
    elif pathname == "/page-2":
        return team_page
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )







######## All Player Callbacks ########


## Bowlers ##

# Player Bowler Select
@app.callback(
    Output('bowler-dropdown', 'options'),
    [Input('season-toggle-bowler', 'value')]
)
def update_bowler_dropdown(selected_season):
    available_bowlers = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_season)]['BOWLER'].unique()
    options = [{'label': bowler, 'value': bowler} for bowler in available_bowlers]
    return options


# Player Bowler Select/Deselect All
@app.callback(
    Output('bowler-dropdown', 'value'),
    [Input('select-all-bowlers', 'n_clicks'),
     Input('deselect-all-bowlers', 'n_clicks')], 
    prevent_initial_call=True
)
def update_bowler_values(n_clicks_select_all, n_clicks_deselect_all):
    # Use dash.callback_context to distinguish triggers
    triggered_input = dash.callback_context.triggered_id
    
    if triggered_input == 'select-all-bowlers':
        # Return all bowlers when the button is clicked
        if n_clicks_select_all is not None and n_clicks_select_all > 0:
            return grouped_bowler_data['BOWLER'].unique().tolist()
        else:
            # Default value (no change)
            return dash.no_update

    elif triggered_input == 'deselect-all-bowlers':
        # Return all bowlers when the button is clicked
        if n_clicks_deselect_all is not None and n_clicks_deselect_all > 0:
            return [] #grouped_bowler_data['BOWLER'].unique().tolist()
        else:
            # Default value (no change)
            return dash.no_update

    else:
        # Default value (no change)
        #raise dash.exceptions.PreventUpdate
        return dash.no_update


# Player Bowler Data Table
@app.callback(
    Output('data-table-bowler', 'data'),
    [Input('season-toggle-bowler', 'value'),
     Input('bowler-dropdown', 'value'),
     Input('bowler-minimum', 'value')]
)
def update_data_table_bowler(selected_seasons, selected_bowlers, bowler_minimum):
    
#     grouped_bowler_data = full_data.groupby(['SEASON', 'BOWLER']).agg({'DELIVERED' : 'sum',
#                                                                    'RUNS' : 'sum',
#                                                                    'WICKET' : 'count',
#                                                                    'DOT' : 'sum',
#                                                                    'WIDE BALLS' : 'sum',
#                                                                    'EXTRA RUNS' : 'sum',
#                                                                    "4's" : 'sum',
#                                                                    "6's" : 'sum'
#                                                           })

#     grouped_bowler_data['OVERS'] = np.floor(grouped_bowler_data['DELIVERED'] / 6) \
#                                     + grouped_bowler_data['DELIVERED'] % 6 / 10

#     grouped_bowler_data['ECONOMY'] = round(grouped_bowler_data['RUNS'] \
#                                     / grouped_bowler_data['OVERS'], 2)
#     overs = grouped_bowler_data.pop('OVERS')
#     grouped_bowler_data.insert = grouped_bowler_data.insert(1, overs.name, overs)
#     grouped_bowler_data = grouped_bowler_data.reset_index()
    #grouped_bowler_data.reset_index(inplace = True)


    filtered_df = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_seasons) \
                                      & grouped_bowler_data['BOWLER'].isin(selected_bowlers) \
                                      & (grouped_bowler_data['OVERS'] > bowler_minimum)]
    table_data = filtered_df.to_dict('records')
    return table_data


# Player Bowler Bar Chart
@app.callback(
    Output('bar-chart-bowler', 'figure'),
    [Input('season-toggle-bowler', 'value'),
     Input('bowler-dropdown', 'value'),
     Input('y-axis-dropdown-bowler', 'value')]
)
def update_barchart_bowler(selected_seasons, selected_bowlers, y_axis_column):
    filtered_df = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_seasons) & grouped_bowler_data['BOWLER'].isin(selected_bowlers)]
    fig = px.bar(filtered_df,
                 x='BOWLER',
                 y=y_axis_column,
                 title=f'Bowler Data - {y_axis_column}',
                 color = 'SEASON')
    return fig


# Player Bowler Scatter Plot
@app.callback(
    Output('scatter-plot-bowler', 'figure'),
    [Input('season-toggle-bowler', 'value'),
     Input('bowler-dropdown', 'value'),
     Input('scatter-color-bowler', 'value'),
     Input('x-axis-scatter-dropdown-bowler', 'value'),
     Input('y-axis-scatter-dropdown-bowler', 'value')]
)
def update_scatter_plot_bowler(selected_seasons, selected_bowlers, scatter_color, x_axis, y_axis):
    filtered_df = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_seasons) & grouped_bowler_data['BOWLER'].isin(selected_bowlers)]
    
    if scatter_color == 'Season':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='SEASON',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BOWLER', 'OVERS']
        )
    elif scatter_color == 'Overs Bowled':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='OVERS',
            color_continuous_scale='gray_r',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BOWLER', 'SEASON']
        )

    return fig




## Batsmen ##

    
# Player Batsman Select
@app.callback(
    Output('batsman-dropdown', 'options'),
    [Input('season-toggle-batsman', 'value')]
)
def update_batsman_dropdown(selected_season):
    available_batsmen = grouped_batsman_data[grouped_batsman_data['SEASON'].isin(selected_season)]['BATSMAN'].unique()
    options = [{'label': batsman, 'value': batsman} for batsman in available_batsmen]
    return options



# Player Batsman Select/Deselect All
@app.callback(
    Output('batsman-dropdown', 'value'),
    [Input('select-all-batsman', 'n_clicks'),
     Input('deselect-all-batsman', 'n_clicks')], 
    prevent_initial_call=True
)
def update_batsman_values(n_clicks_select_all, n_clicks_deselect_all):
    # Use dash.callback_context to distinguish triggers
    triggered_input = dash.callback_context.triggered_id
    
    if triggered_input == 'select-all-batsman':
        # Return all batsman when the button is clicked
        if n_clicks_select_all is not None and n_clicks_select_all > 0:
            return grouped_batsman_data['BATSMAN'].unique().tolist()
        else:
            # Default value (no change)
            return dash.no_update

    elif triggered_input == 'deselect-all-batsman':
        # Return all bowlers when the button is clicked
        if n_clicks_deselect_all is not None and n_clicks_deselect_all > 0:
            return []
        else:
            # Default value (no change)
            return dash.no_update

    else:
        # Default value (no change)
        #raise dash.exceptions.PreventUpdate
        return dash.no_update
    
    
# Player Batsman Data Table
@app.callback(
    Output('data-table-batsman', 'data'),
    [Input('season-toggle-batsman', 'value'),
     Input('batsman-dropdown', 'value'),
     Input('batsman-minimum', 'value')]
)
def update_data_table_batsman(selected_seasons, selected_batsmen, batsman_minimum):
    
#     grouped_batsman_data = full_data.groupby(['SEASON', 'BATSMAN']).agg({'GAME' : 'nunique',
#                                                                      'INNINGS BATTED' : 'nunique',
#                                                                      'DELIVERED' : 'sum',
#                                                                    'RUNS' : 'sum',
#                                                                    'WICKET' : 'count',
#                                                                    'DOT' : 'sum',
#                                                                    'WIDE BALLS' : 'sum',
#                                                                    'EXTRA RUNS' : 'sum',
#                                                                    "4's" : 'sum',
#                                                                    "6's" : 'sum'
#                                                           })

#     grouped_batsman_data.rename(columns = {'DELIVERED' : 'BALLS FACED',
#                                            'GAME' : 'GAMES'}, inplace = True)
#     grouped_batsman_data['RUNS'] = grouped_batsman_data['RUNS'] - grouped_batsman_data['EXTRA RUNS']
#     grouped_batsman_data['STRIKE RATE'] = round(grouped_batsman_data['RUNS'] \
#                                             / grouped_batsman_data['BALLS FACED'] * 100, 1)
#     grouped_batsman_data['AVG / INNINGS'] = round(grouped_batsman_data['RUNS'] \
#                                             / grouped_batsman_data['INNINGS BATTED'], 2)
#     grouped_batsman_data = grouped_batsman_data.reset_index()

    
    filtered_df = grouped_batsman_data[grouped_batsman_data['SEASON'].isin(selected_seasons) \
                                       & grouped_batsman_data['BATSMAN'].isin(selected_batsmen) \
                                       & (grouped_batsman_data['INNINGS BATTED'] > batsman_minimum)]
    table_data = filtered_df.to_dict('records')
    return table_data


# Player Batsman Bar Chart
@app.callback(
    Output('bar-chart-batsman', 'figure'),
    [Input('season-toggle-batsman', 'value'),
     Input('batsman-dropdown', 'value'),
     Input('y-axis-dropdown-batsman', 'value')]
)
def update_barchart_batsman(selected_seasons, selected_batsman, y_axis_column):
    filtered_df = grouped_batsman_data[grouped_batsman_data['SEASON'].isin(selected_seasons) & grouped_batsman_data['BATSMAN'].isin(selected_batsman)]
    fig = px.bar(filtered_df,
                 x='BATSMAN',
                 y=y_axis_column,
                 title=f'Batsman Data - {y_axis_column}',
                 color = 'SEASON')
    return fig


# Player Batsman Scatter Plot
@app.callback(
    Output('scatter-plot-batsman', 'figure'),
    [Input('season-toggle-batsman', 'value'),
     Input('batsman-dropdown', 'value'),
     Input('scatter-color-batsman', 'value'),
     Input('x-axis-scatter-dropdown-batsman', 'value'),
     Input('y-axis-scatter-dropdown-batsman', 'value')]
)
def update_scatter_plot_batsman(selected_seasons, selected_batsmen, scatter_color, x_axis, y_axis):
    filtered_df = grouped_batsman_data[grouped_batsman_data['SEASON'].isin(selected_seasons) & grouped_batsman_data['BATSMAN'].isin(selected_batsmen)]
    
    if scatter_color == 'Season':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='SEASON',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BATSMAN', 'INNINGS BATTED']
        )
    elif scatter_color == 'Innings Batted':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='INNINGS BATTED',
            color_continuous_scale='gray_r',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BATSMAN', 'SEASON']
        )

    return fig












######## All Team Callbacks ########


## Bowling Team ##

# Team Bowler Select
@app.callback(
    Output('bowler-dropdown-team', 'options'),
    [Input('season-toggle-bowler-team', 'value')]
)
def update_bowler_dropdown(selected_season):
    available_bowlers = grouped_bowling_team_data[grouped_bowling_team_data['SEASON'].isin(selected_season)]['BOWLING TEAM'].unique()
    options = [{'label': bowler, 'value': bowler} for bowler in available_bowlers]
    return options


# Team Bowler Select/Deselect All
@app.callback(
    Output('bowler-dropdown-team', 'value'),
    [Input('select-all-bowlers-team', 'n_clicks'),
     Input('deselect-all-bowlers-team', 'n_clicks')], 
    prevent_initial_call=True
)
def update_bowler_values(n_clicks_select_all, n_clicks_deselect_all):
    # Use dash.callback_context to distinguish triggers
    triggered_input = dash.callback_context.triggered_id
    
    if triggered_input == 'select-all-bowlers-team':
        # Return all bowlers when the button is clicked
        if n_clicks_select_all is not None and n_clicks_select_all > 0:
            return grouped_bowling_team_data['BOWLING TEAM'].unique().tolist()
        else:
            # Default value (no change)
            return dash.no_update

    elif triggered_input == 'deselect-all-bowlers-team':
        # Return all bowlers when the button is clicked
        if n_clicks_deselect_all is not None and n_clicks_deselect_all > 0:
            return []
        else:
            # Default value (no change)
            return dash.no_update

    else:
        # Default value (no change)
        return dash.no_update

    
# Team Bowler Data Table
@app.callback(
    Output('data-table-bowler-team', 'data'),
    [Input('season-toggle-bowler-team', 'value'),
     Input('bowler-dropdown-team', 'value')]
)
def update_data_table_bowler(selected_seasons, selected_bowlers):
    filtered_df = grouped_bowling_team_data[grouped_bowling_team_data['SEASON'].isin(selected_seasons) \
                                            & grouped_bowling_team_data['BOWLING TEAM'].isin(selected_bowlers)]
    table_data = filtered_df.to_dict('records')
    return table_data


# Team Bowler Bar Chart
@app.callback(
    Output('bar-chart-bowler-team', 'figure'),
    [Input('season-toggle-bowler-team', 'value'),
     Input('bowler-dropdown-team', 'value'),
     Input('y-axis-dropdown-bowler-team', 'value')]
)
def update_barchart_bowler(selected_seasons, selected_bowlers, y_axis_column):
    filtered_df = grouped_bowling_team_data[grouped_bowling_team_data['SEASON'].isin(selected_seasons) & grouped_bowling_team_data['BOWLING TEAM'].isin(selected_bowlers)]
    fig = px.bar(filtered_df,
                 x='BOWLING TEAM',
                 y=y_axis_column,
                 title=f'Bowler Data - {y_axis_column}',
                 color='SEASON')
    return fig


# Team Bowler Scatter Plot
@app.callback(
    Output('scatter-plot-bowler-team', 'figure'),
    [Input('season-toggle-bowler-team', 'value'),
     Input('bowler-dropdown-team', 'value'),
     Input('scatter-color-bowler-team', 'value'),
     Input('x-axis-scatter-dropdown-bowler-team', 'value'),
     Input('y-axis-scatter-dropdown-bowler-team', 'value')]
)
def update_scatter_plot_bowler(selected_seasons, selected_bowlers, scatter_color, x_axis, y_axis):
    filtered_df = grouped_bowling_team_data[grouped_bowling_team_data['SEASON'].isin(selected_seasons) & grouped_bowling_team_data['BOWLING TEAM'].isin(selected_bowlers)]
    
    if scatter_color == 'Season':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='SEASON',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BOWLING TEAM', 'OVERS']
        )
    elif scatter_color == 'Overs Bowled':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='OVERS',
            color_continuous_scale='gray_r',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BOWLING TEAM', 'SEASON']
        )

    return fig






## Batting Team ##
    
# Team Batsman Select
@app.callback(
    Output('batsman-dropdown-team', 'options'),
    [Input('season-toggle-batsman-team', 'value')]
)
def update_batsman_dropdown(selected_season):
    available_batsmen = grouped_batting_team_data[grouped_batting_team_data['SEASON'].isin(selected_season)]['BATTING TEAM'].unique()
    options = [{'label': batsman, 'value': batsman} for batsman in available_batsmen]
    return options


# Team Batsman Select/Deselect All
@app.callback(
    Output('batsman-dropdown-team', 'value'),
    [Input('select-all-batsman-team', 'n_clicks'),
     Input('deselect-all-batsman-team', 'n_clicks')], 
    prevent_initial_call=True
)
def update_batsman_values(n_clicks_select_all, n_clicks_deselect_all):
    # Use dash.callback_context to distinguish triggers
    triggered_input = dash.callback_context.triggered_id
    
    if triggered_input == 'select-all-batsman-team':
        # Return all batsman when the button is clicked
        if n_clicks_select_all is not None and n_clicks_select_all > 0:
            return grouped_batting_team_data['BATTING TEAM'].unique().tolist()
        else:
            # Default value (no change)
            return dash.no_update

    elif triggered_input == 'deselect-all-batsman-team':
        # Return all bowlers when the button is clicked
        if n_clicks_deselect_all is not None and n_clicks_deselect_all > 0:
            return []
        else:
            # Default value (no change)
            return dash.no_update

    else:
        # Default value (no change)
        return dash.no_update

    
# Team Batsman Data Table
@app.callback(
    Output('data-table-batsman-team', 'data'),
    [Input('season-toggle-batsman-team', 'value'),
     Input('batsman-dropdown-team', 'value')]
)
def update_data_table_batsman(selected_seasons, selected_batsmen):
    filtered_df = grouped_batting_team_data[grouped_batting_team_data['SEASON'].isin(selected_seasons) & grouped_batting_team_data['BATTING TEAM'].isin(selected_batsmen)]
    table_data = filtered_df.to_dict('records')
    return table_data


# Team Batsman Bar Chart
@app.callback(
 Output('bar-chart-batsman-team', 'figure'),
    [Input('season-toggle-batsman-team', 'value'),
     Input('batsman-dropdown-team', 'value'),
     Input('y-axis-dropdown-batsman-team', 'value')]
)
def update_barchart_batsman(selected_seasons, selected_batsman, y_axis_column):
    filtered_df = grouped_batting_team_data[grouped_batting_team_data['SEASON'].isin(selected_seasons) & grouped_batting_team_data['BATTING TEAM'].isin(selected_batsman)]
    fig = px.bar(filtered_df,
                 x='BATTING TEAM',
                 y=y_axis_column,
                 title=f'Batsman Data - {y_axis_column}',
                 color='SEASON')
    return fig


# Team Batsman Scatter Plot
@app.callback(
    Output('scatter-plot-batsman-team', 'figure'),
    [Input('season-toggle-batsman-team', 'value'),
     Input('batsman-dropdown-team', 'value'),
     Input('scatter-color-batsman-team', 'value'),
     Input('x-axis-scatter-dropdown-batsman-team', 'value'),
     Input('y-axis-scatter-dropdown-batsman-team', 'value')]
)
def update_scatter_plot_batsman(selected_seasons, selected_batsmen, scatter_color, x_axis, y_axis):
    filtered_df = grouped_batting_team_data[grouped_batting_team_data['SEASON'].isin(selected_seasons) & grouped_batting_team_data['BATTING TEAM'].isin(selected_batsmen)]
    
    if scatter_color == 'Season':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='SEASON',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BATTING TEAM', 'INNINGS BATTED']
        )
    elif scatter_color == 'Innings Batted':
        fig = px.scatter(
            filtered_df,
            x=x_axis,
            y=y_axis,
            color='INNINGS BATTED',
            color_continuous_scale='gray_r',
            size_max=10,
            title=f'{x_axis} vs. {y_axis}',
            hover_data=['BATTING TEAM', 'SEASON']
        )

    return fig

    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
