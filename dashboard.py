import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import math


sheet_id = '1NfqXgq2l5vJw2M5ffCLv2zQsXy3iOqak6IAEe3U0AG4'
    
raw_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

full_data = raw_data.copy(deep=True)

#full_data.loc[full_data['BATSMAN'] == 'Joez McFly', ['BATSMAN']] = 'Joez Mcfly'

full_data['DELIVERED'] = np.where(full_data['BALL'] != 'WIDE', 1, 0)
full_data['DOT'] = np.where((full_data['RUNS'] == 0) & 
                             (full_data['WICKET'].isna() == True), 1, 0)
full_data['WIDE BALLS'] = np.where(full_data['BALL'] == 'WIDE', 1, 0)
full_data['EXTRA RUNS'] = full_data['WIDE BALLS'] * full_data['RUNS']
full_data["4's"] = np.where(full_data['RUNS'] == 4, 1, 0)
full_data["6's"] = np.where(full_data['RUNS'] == 6, 1, 0)

full_data['INNINGS BATTED'] = full_data['GAME'] + full_data['INNING'].astype(str)

grouped_bowler_data = full_data.groupby(['SEASON', 'BOWLER']).agg({'DELIVERED' : 'sum',
                                                                   'RUNS' : 'sum',
                                                                   'WICKET' : 'count',
                                                                   'DOT' : 'sum',
                                                                   'WIDE BALLS' : 'sum',
                                                                   'EXTRA RUNS' : 'sum',
                                                                   "4's" : 'sum',
                                                                   "6's" : 'sum'
                                                          })

grouped_bowler_data['OVERS'] = np.floor(grouped_bowler_data['DELIVERED'] / 6) \
                                    + grouped_bowler_data['DELIVERED'] % 6 / 10

grouped_bowler_data['ECONOMY'] = round(grouped_bowler_data['RUNS'] \
                                    / grouped_bowler_data['OVERS'], 2)
overs = grouped_bowler_data.pop('OVERS')
grouped_bowler_data.insert = grouped_bowler_data.insert(1, overs.name, overs)
grouped_bowler_data = grouped_bowler_data.reset_index()
#grouped_bowler_data.reset_index(inplace = True)
    
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

grouped_batsman_data.rename(columns = {'DELIVERED' : 'BALLS FACED',
                                           'GAME' : 'GAMES'}, inplace = True)
grouped_batsman_data['RUNS'] = grouped_batsman_data['RUNS'] \
                                            - grouped_batsman_data['EXTRA RUNS']
grouped_batsman_data['STRIKE RATE'] = round(grouped_batsman_data['RUNS'] \
                                            / grouped_batsman_data['BALLS FACED'] * 100, 1)
grouped_batsman_data['AVG / INNINGS'] = round(grouped_batsman_data['RUNS'] \
                                            / grouped_batsman_data['INNINGS BATTED'], 2)
grouped_batsman_data = grouped_batsman_data.reset_index()


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout of the app with tabs
app.layout = html.Div([
    html.H1("Ball in Play Dashboard", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 20, 'font-family': 'Arial, sans-serif'}),
    
    dcc.Tabs([
        # Tab for Bowler Data
        dcc.Tab(label='Bowler Data',
                style={'fontSize': 20, 'color': '#4CAF50'},
                selected_style={'fontSize': 20, 'color': '#4CAF50', 'fontWeight': 'bold'},
                children=[
            html.Label("Select Season:", style={'fontSize': 16, 'color': '#333'}),
            dcc.Checklist(
                id='season-toggle-bowler',
                options=[
                    {'label': col, 'value': col} for col in grouped_bowler_data['SEASON'].unique()
                ],
                value=grouped_bowler_data['SEASON'].unique(),
                style={'marginBottom': 20, 'color': '#333'}
            ),
            
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
            
            html.H3("Bowler Data Table", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 10}),
            dash_table.DataTable(
                id='data-table-bowler',
                columns=[
                    {"name": i, "id": i} for i in grouped_bowler_data.columns
                ],
                data=grouped_bowler_data.to_dict('records'),
                style_table={'overflowX': 'auto', 'border': '2px solid #4CAF50', 'boxShadow': '0px 0px 10px #888888'},
                style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                sort_action='native',  # 'native' enables sorting on the client side
                sort_mode='multi',  # 'multi' allows sorting by multiple columns
            ),
            
            html.Div(style={'marginBottom': 40}),
                    
            # Dropdown for Y-axis selection
            html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
            dcc.Dropdown(
                id='y-axis-dropdown-bowler',
                options=[
                    #{'label': 'DELIVERED', 'value': 'DELIVERED'}
                    #{'label': col, 'value': col} for col in grouped_bowler_data.columns
                    {'label': col, 'value': col} for col in grouped_bowler_data.columns if col not in ['SEASON', 'BOWLER']
                ],
                value='DELIVERED',
                style={'marginBottom': 20}
            ),
                    
            # Bar chart
            dcc.Graph(
                id='bar-chart-bowler',
                style={'height': '400px'},
            )
        ]),
        
        # Tab for Batsman Data
        dcc.Tab(label='Batsman Data',
                style={'fontSize': 20, 'color': '#4CAF50'},
                selected_style={'fontSize': 20, 'color': '#4CAF50', 'fontWeight': 'bold'},
                children=[
            html.Label("Select Season:", style={'fontSize': 16, 'color': '#333'}),
            dcc.Checklist(
                id='season-toggle-batsman',
                options=[
                    {'label': col, 'value': col} for col in grouped_batsman_data['SEASON'].unique()
                ],
                value=grouped_batsman_data['SEASON'].unique(),
                style={'marginBottom': 20, 'color': '#333'}
            ),
            
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
            
            html.H3("Batsman Data Table", style={'textAlign': 'center', 'color': '#4CAF50', 'marginBottom': 10}),
            dash_table.DataTable(
                id='data-table-batsman',
                columns=[
                    {"name": i, "id": i} for i in grouped_batsman_data.columns
                ],
                data=grouped_batsman_data.to_dict('records'),
                style_table={'overflowX': 'auto', 'border': '2px solid #4CAF50', 'boxShadow': '0px 0px 10px #888888'},
                style_header={'backgroundColor': '#4CAF50', 'color': 'white', 'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                style_cell={'textAlign': 'center', 'font-family': 'Arial, sans-serif'},
                sort_action='native',  # 'native' enables sorting on the client side
                sort_mode='multi',  # 'multi' allows sorting by multiple columns
            ),
                    
            html.Div(style={'marginBottom': 40}),
                    
            # Dropdown for Y-axis selection
            html.Label("Select Y-axis:", style={'fontSize': 16, 'color': '#333'}),
            dcc.Dropdown(
                id='y-axis-dropdown-batsman',
                options=[
                    #{'label': col, 'value': col} for col in grouped_batsman_data.columns
                    {'label': col, 'value': col} for col in grouped_batsman_data.columns if col not in ['SEASON', 'BATSMAN']
                ],
                value='INNINGS BATTED',
                style={'marginBottom': 20}
            ),
                    
            # Bar chart
            dcc.Graph(
                id='bar-chart-batsman',
                style={'height': '400px'},
            )
        ])
    ])
], style={'font-family': 'Arial, sans-serif'})


# Callback for updating player selection list based on selected season for Bowler Data
@app.callback(
    Output('bowler-dropdown', 'options'),
    [Input('season-toggle-bowler', 'value')]
)
def update_bowler_dropdown(selected_season):
    available_bowlers = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_season)]['BOWLER'].unique()
    options = [{'label': bowler, 'value': bowler} for bowler in available_bowlers]
    return options

# Callback to update bowler dropdown options when "Select All" or "Deselect All" button is clicked
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



    
    
    
# Callback for updating player selection list based on selected season for Batsman Data
@app.callback(
    Output('batsman-dropdown', 'options'),
    [Input('season-toggle-batsman', 'value')]
)
def update_batsman_dropdown(selected_season):
    available_batsmen = grouped_batsman_data[grouped_batsman_data['SEASON'].isin(selected_season)]['BATSMAN'].unique()
    options = [{'label': batsman, 'value': batsman} for batsman in available_batsmen]
    return options


# Callback to update batsman dropdown options when "Select All" or "Deselect All" button is clicked
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




# Callback for updating bar chart based on selected options for Bowler Data
@app.callback(
    Output('bar-chart-bowler', 'figure'),
    [Input('season-toggle-bowler', 'value'),
     Input('bowler-dropdown', 'value'),
     Input('y-axis-dropdown-bowler', 'value')]
)
def update_barchart_bowler(selected_seasons, selected_bowlers, y_axis_column):
    #filtered_df = grouped_bowler_data[grouped_bowler_data['BOWLER'].isin(selected_bowlers)]
    filtered_df = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_seasons) & grouped_bowler_data['BOWLER'].isin(selected_bowlers)]
    fig = px.bar(filtered_df,
                 x='BOWLER',
                 y=y_axis_column,
                 title=f'Bowler Data - {y_axis_column}',
                 color = 'SEASON')
    return fig


# Callback for updating bar chart based on selected options for Batsman Data
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


# Callback for updating Bowler Data Table
@app.callback(
    Output('data-table-bowler', 'data'),
    [Input('season-toggle-bowler', 'value'),
     Input('bowler-dropdown', 'value')]
)
def update_data_table_bowler(selected_seasons, selected_bowlers):
    
    grouped_bowler_data = full_data.groupby(['SEASON', 'BOWLER']).agg({'DELIVERED' : 'sum',
                                                                   'RUNS' : 'sum',
                                                                   'WICKET' : 'count',
                                                                   'DOT' : 'sum',
                                                                   'WIDE BALLS' : 'sum',
                                                                   'EXTRA RUNS' : 'sum',
                                                                   "4's" : 'sum',
                                                                   "6's" : 'sum'
                                                          })

    grouped_bowler_data['OVERS'] = np.floor(grouped_bowler_data['DELIVERED'] / 6) \
                                    + grouped_bowler_data['DELIVERED'] % 6 / 10

    grouped_bowler_data['ECONOMY'] = round(grouped_bowler_data['RUNS'] \
                                    / grouped_bowler_data['OVERS'], 2)
    overs = grouped_bowler_data.pop('OVERS')
    grouped_bowler_data.insert = grouped_bowler_data.insert(1, overs.name, overs)
    grouped_bowler_data = grouped_bowler_data.reset_index()
    #grouped_bowler_data.reset_index(inplace = True)


    filtered_df = grouped_bowler_data[grouped_bowler_data['SEASON'].isin(selected_seasons) & grouped_bowler_data['BOWLER'].isin(selected_bowlers)]
    table_data = filtered_df.to_dict('records')
    return table_data


# Callback for updating Batsman Data Table
@app.callback(
    Output('data-table-batsman', 'data'),
    [Input('season-toggle-batsman', 'value'),
     Input('batsman-dropdown', 'value')]
)
def update_data_table_batsman(selected_seasons, selected_batsmen):
    
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

    grouped_batsman_data.rename(columns = {'DELIVERED' : 'BALLS FACED',
                                           'GAME' : 'GAMES'}, inplace = True)
    grouped_batsman_data['RUNS'] = grouped_batsman_data['RUNS'] - grouped_batsman_data['EXTRA RUNS']
    grouped_batsman_data['STRIKE RATE'] = round(grouped_batsman_data['RUNS'] \
                                            / grouped_batsman_data['BALLS FACED'] * 100, 1)
    grouped_batsman_data['AVG / INNINGS'] = round(grouped_batsman_data['RUNS'] \
                                            / grouped_batsman_data['INNINGS BATTED'], 2)
    grouped_batsman_data = grouped_batsman_data.reset_index()

    
    filtered_df = grouped_batsman_data[grouped_batsman_data['SEASON'].isin(selected_seasons) & grouped_batsman_data['BATSMAN'].isin(selected_batsmen)]
    table_data = filtered_df.to_dict('records')
    return table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)