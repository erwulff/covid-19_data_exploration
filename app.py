import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


import pandas as pd

import numpy as np
from datetime import datetime

from utils import get_df, datetimeify, process_df, get_frame
# from utils import total_vs_time, new_vs_time, new_vs_total
from my_dash_functions import total_vs_time, new_vs_time, new_vs_total

# path do data folder
# path = 'COVID-19/csse_covid_19_data/csse_covid_19_time_series/'

# file names
# file_confirmed = 'time_series_covid19_confirmed_global.csv'
# file_deaths = 'time_series_covid19_deaths_global.csv'
# file_recovered = 'time_series_covid19_recovered_global.csv'


# load DataFrames
# df_conf_all = get_df(file_path=path + file_confirmed)
# df_deaths_all = get_df(file_path=path + file_deaths)

df_conf_all = process_df(get_frame('confirmed'))
df_deaths_all = process_df(get_frame('deaths'))
all_countries = list(df_conf_all.keys())


date_list = datetimeify(df_conf_all.index)

# Pick countries to plot
start_countries = [
    'Sweden',
    'Norway',
    'France',
    'Spain',
    'Germany',
    'Switzerland',
    'US',
    'Korea, South',
    'Singapore',
    'Italy',
    'United Kingdom'
]
start_countries.sort()

# Filter DataFrames
df_conf = df_conf_all[start_countries]
df_deaths = df_deaths_all[start_countries]

# style sheets for dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# dash app starts here
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([

    dcc.Markdown('''
    # Covid-19 data visualization

    > *by Eric Wulff*

    The visualizations presented here are based on data from the Johns Hopkins
    University's GitHub [repository](https://github.com/CSSEGISandData/COVID-19).

    The source code of this app is published on GitHub
    [here](https://github.com/erwulff/covid-19_data_exploration).

    Use the search box below to add countries to the plots.
    '''),
    html.Div([
        dcc.Dropdown(
            placeholder='Select countries...',
            id='country_dropdown',
            multi=True,
            value=start_countries,
        ),
        html.Button('Nordic countries', id='button1', n_clicks=0),
        html.Button('Reset', id='reset_button', n_clicks=0),
    ],
        className='twelve columns',
    ),
    html.Div([
        dcc.Markdown('''
                     ## Total confirmed cases/deaths
                     '''),
    ],
        className='twelve columns'

    ),

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
    html.Div([
        dcc.Markdown('''
        ## New confirmed cases/deaths per day
        '''),
    ],
        className='twelve columns'),

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
            value='log',
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



    html.Div([
        dcc.Markdown('''
        ## New vs. total confirmed cases/deaths

        If the growth of something is proportional to its prevalence the growth
        is exponential. This results in that the growth
        is accelerating with time.

        In terms of a pandemic this translates to that the number of newly
        infected people per day is proportional to the total number of infected
        people. Therefore exponential growth appears as a straight line if you
        plot the new cases against the total cases. The steepness of this line
        corresponds to the growth rate.

        This plot makes it easy to see which countries have managed to
        break the exponential trend, thus plummeting towards fewer new cases per
        day.
        '''),
    ],
        className='twelve columns'),

    html.Div([
        dcc.Dropdown(
            id='dropdown3',
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
            id='window_selector2',
            options=[{'label': 'Rolling mean: {}'.format(
                ii + 1), 'value': ii + 1} for ii in range(14)],
            value=7,
        ),
        className='three columns'
    ),
    html.Div(
        dcc.Graph(id='graph3', style={'height': '600px', 'width': '85vw'}, responsive=True),
        className='twelve columns'
    ),
])


country_options = [{'label': country, 'value': country} for country in all_countries]


@app.callback(
    Output("country_dropdown", "options"),
    [Input("country_dropdown", "search_value")],
    [State("country_dropdown", "value")],
)
def update_multi_options(search_value, value):
    if not search_value:
        raise PreventUpdate
    # Make sure that the set values are in the option list, else they will disappear
    # from the shown select list, but still part of the `value`.
    return [
        o for o in country_options if search_value in o["label"] or o["value"] in (value or [])
    ]


@app.callback(
    Output('graph1', 'figure'),
    [Input('dropdown', 'value'),
     Input('axis_dropdown', 'value'),
     Input('country_dropdown', 'value'),
     Input("button1", "n_clicks"),
     Input("reset_button", "n_clicks"),
     ])
def update_figure(selected_cases,
                  selected_axis_type,
                  selected_countries,
                  button,
                  reset):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'button1' in changed_id:
        selected_countries = ['Sweden', 'Denmark', 'Finland', 'Norway']
        selected_countries.sort()
    elif 'reset_button' in changed_id:
        selected_countries = start_countries
        selected_countries.sort()

    if selected_cases == 'confirmed cases':
        df = df_conf_all[selected_countries]
    elif selected_cases == 'deaths':
        df = df_deaths_all[selected_countries]

    traces, layout = total_vs_time(df, descr=selected_cases)

    layout.update(dict(
        xaxis={'title': 'Date'},
        yaxis={'title': 'Total {}'.format(selected_cases), 'type': selected_axis_type},
    ))
    return {
        'data': traces,
        'layout': layout,
    }


@app.callback(
    Output('graph2', 'figure'),
    [Input('dropdown2', 'value'),
     Input('axis_dropdown2', 'value'),
     Input('window_selector', 'value'),
     Input('country_dropdown', 'value'),
     Input("button1", "n_clicks"),
     Input("reset_button", "n_clicks")])
def update_figure2(selected_cases,
                   selected_axis_type,
                   selected_window,
                   selected_countries,
                   button,
                   reset,
                   ):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'button1' in changed_id:
        selected_countries = ['Sweden', 'Denmark', 'Finland', 'Norway']
        selected_countries.sort()
    elif 'reset_button' in changed_id:
        selected_countries = start_countries
        selected_countries.sort()

    if selected_cases == 'confirmed cases':
        df = df_conf_all[selected_countries]
    elif selected_cases == 'deaths':
        df = df_deaths_all[selected_countries]

    traces, layout = new_vs_time(df, descr=selected_cases, window=selected_window)

    layout.update(dict(
        xaxis={'title': 'Date'},
        yaxis={'title': 'New {}'.format(selected_cases), 'type': selected_axis_type},
    ))

    return {
        'data': traces,
        'layout': layout,
    }


@app.callback(
    Output('graph3', 'figure'),
    [Input('dropdown3', 'value'),
     Input('window_selector2', 'value'),
     Input('country_dropdown', 'value'),
     Input("button1", "n_clicks"),
     Input("reset_button", "n_clicks")])
def update_figure3(selected_cases,
                   selected_window,
                   selected_countries,
                   button,
                   reset,
                   ):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'button1' in changed_id:
        selected_countries = ['Sweden', 'Denmark', 'Finland', 'Norway']
        selected_countries.sort()
    elif 'reset_button' in changed_id:
        selected_countries = start_countries
        selected_countries.sort()

    if selected_cases == 'confirmed cases':
        df = df_conf_all[selected_countries]
    elif selected_cases == 'deaths':
        df = df_deaths_all[selected_countries]

    traces, layout = new_vs_total(df, descr=selected_cases, window=selected_window)

    layout.update(dict(
        xaxis={'title': 'Total {}'.format(selected_cases), 'type': 'log'},
        yaxis={'title': 'New {}'.format(selected_cases), 'type': 'log'},
    ))

    return {
        'data': traces,
        'layout': layout,
    }


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8050)
