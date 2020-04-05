import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


import pandas as pd

import numpy as np
from datetime import datetime

from utils import get_df, datetimeify, process_df
# from utils import total_vs_time, new_vs_time, new_vs_total
from my_dash_functions import total_vs_time, new_vs_time, new_vs_total

# path do data folder
path = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

# file names
file_confirmed = 'time_series_covid19_confirmed_global.csv'
file_deaths = 'time_series_covid19_deaths_global.csv'
file_recovered = 'time_series_covid19_recovered_global.csv'

# load DataFrames
df_conf = get_df(file_path=path + file_confirmed)
df_deaths = get_df(file_path=path + file_deaths)

date_list = datetimeify(df_conf.index)

# Pick countries to plot
countries = ['China',
             'Sweden',
             'Denmark',
             'Norway',
             'France',
             'Spain',
             'Germany',
             'Switzerland',
             'Finland',
             'US',
             'Korea, South',
             'Singapore',
             'Italy',
             ]
countries.sort()

# Filter DataFrames
df_conf = df_conf[countries]
df_deaths = df_deaths[countries]

# style sheets for dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# dash app starts here
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([

    dcc.Markdown('''
    # Covid-19 data visualization

    *by Eric Wulff*

    The visualizations presented here are based on data from the Johns Hopkins
    University's GitHub [repository](https://github.com/CSSEGISandData/COVID-19).

    The source code of this app is published on GitHub
    [here](https://github.com/erwulff/covid-19_data_exploration).

    ## Number of total confirmed cases/deaths over time
    '''),

    html.Div([
        dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': 'Deaths', 'value': 'deaths'},
                {'label': 'Confirmed cases', 'value': 'confirmed cases'},
            ],
            value='confirmed cases',
        ),
    ],
        className='three columns',
    ),
    html.Div(
        dcc.Dropdown(
            id='axis_dropdown',
            options=[
                {'label': 'Linear', 'value': 'linear'},
                {'label': 'Logarithmic', 'value': 'log'},
            ],
            value='log',
        ),
        className='three columns',
    ),
    html.Div(
        dcc.Graph(id='graph1', style={'height': '600px', 'width': '85vw'}, responsive=True),
        className='twelve columns'
    ),

    dcc.Markdown('''
    ## Number of new confirmed cases/deaths over time
    '''),

    html.Div([
        dcc.Dropdown(
            id='dropdown2',
            options=[
                {'label': 'Deaths', 'value': 'deaths'},
                {'label': 'Confirmed cases', 'value': 'confirmed cases'},
            ],
            value='confirmed cases',
        ),
    ],
        className='three columns',
    ),
    html.Div(
        dcc.Dropdown(
            id='axis_dropdown2',
            options=[
                {'label': 'Linear', 'value': 'linear'},
                {'label': 'Logarithmic', 'value': 'log'},
            ],
            value='linear',
        ),
        className='three columns',
    ),
    html.Div(
        dcc.Dropdown(
            id='window_selector',
            options=[{'label': 'Rolling mean: {}'.format(
                ii + 1), 'value': ii + 1} for ii in range(14)],
            value=7,
        ),
        className='three columns'
    ),
    html.Div(
        dcc.Graph(id='graph2', style={'height': '600px', 'width': '85vw'}, responsive=True),
        className='twelve columns'
    ),
])


@app.callback(
    Output('graph1', 'figure'),
    [Input('dropdown', 'value'), Input('axis_dropdown', 'value')])
def update_figure(selected_cases, selected_axis_type):
    if selected_cases == 'confirmed cases':
        df = df_conf
    elif selected_cases == 'deaths':
        df = df_deaths

    traces, layout = total_vs_time(df, descr=selected_cases)

    layout.update(dict(
        xaxis={'title': 'Date'},
        yaxis={'title': 'Covid-19 {}'.format(selected_cases), 'type': selected_axis_type},
    ))

    return {
        'data': traces,
        'layout': layout,
    }


@app.callback(
    Output('graph2', 'figure'),
    [Input('dropdown2', 'value'),
     Input('axis_dropdown2', 'value'),
     Input('window_selector', 'value')])
def update_figure2(selected_cases, selected_axis_type, selected_window):
    if selected_cases == 'confirmed cases':
        df = df_conf
    elif selected_cases == 'deaths':
        df = df_deaths

    traces, layout = new_vs_time(df, descr=selected_cases, window=selected_window)

    layout.update(dict(
        xaxis={'title': 'Date'},
        yaxis={'title': 'Covid-19 new {}'.format(selected_cases), 'type': selected_axis_type},
    ))

    return {
        'data': traces,
        'layout': layout,
    }


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
