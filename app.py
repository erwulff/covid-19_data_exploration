import subprocess
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


import pandas as pd
import numpy as np
from datetime import datetime
import wget

from utils import get_df, process_df, get_frame, get_xl_sheets
from my_dash_functions import total_vs_time, new_vs_time, new_vs_total
from my_dash_functions import landskap

import wget


# Colors
extra_layout_vars = dict(
    paper_bgcolor="rgba(0, 0, 0, 0.3)",
    plot_bgcolor="rgb(32, 42, 53)",
    font={"color": "white"},
)
gridcolor = "rgba(0, 0, 0, 0.3)"
dropdown_style = {
    "color": "white",
    "background-color": "#00bc8c",
}


df_conf_all = process_df(get_frame("confirmed"))
df_deaths_all = process_df(get_frame("deaths"))
all_countries = list(df_conf_all.keys())

country_options = [{"label": country, "value": country} for country in all_countries]

# Get Swedish data
url = "https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data"
wget.download(url, out="sweden_xl_file.xlsx")

sheets = get_xl_sheets(file="sweden_xl_file.xlsx")

# Pick countries to plot


def get_start_conutries():
    start_countries = [
        "Sweden",
        "Norway",
        "Denmark",
        "Finland",
        "France",
        "Spain",
        "Germany",
        "Switzerland",
        "US",
        "Italy",
        "United Kingdom",
    ]
    start_countries.sort()
    return start_countries


start_countries = get_start_conutries()

# Filter DataFrames
df_conf = df_conf_all[start_countries]
df_deaths = df_deaths_all[start_countries]

# style sheets for dash app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# dash app starts here
app = dash.Dash(__name__)  # , external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(
    [
        dcc.Markdown(
            """
    # Covid-19 data visualization

    > *by Eric Wulff*

    The visualizations presented here are based on data from the Johns Hopkins
    University's GitHub [repository](https://github.com/CSSEGISandData/COVID-19).

    The data presented under **A closer look at Sweden** is taken from the
    Swedish Health Authorities'
    [website](https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/bekraftade-fall-i-sverige/)
    (www.folkhalsomyndigheten.se). More specifically, data from [this](https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data)
    download link is used.

    The source code of this app is published on GitHub
    [here](https://github.com/erwulff/covid-19_data_exploration).

    Use the search box to add countries to the graphs or click on
    **DEFAULT COUNTRIES** or **NORDIC COUNTRIES** to populate the graphs with a
    predefined set of countries.
    """
        ),
        html.Div(
            [
                dcc.Dropdown(
                    placeholder="Search countries...",
                    id="country_dropdown",
                    multi=True,
                    options=country_options,
                    value=start_countries,
                    style=dropdown_style,
                ),
            ],
            className="twelve columns",
        ),
        html.Div(
            [
                html.Button("Default countries", id="reset_button", n_clicks=0),
                html.Button("Nordic countries", id="button1", n_clicks=0),
            ],
            style=dict(padding_top="100px"),
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
                     ## Total confirmed cases/deaths
                     Click on countries in the legend to hide or show them
                     """
                ),
            ],
            className="twelve columns",
        ),
        html.Div(
            [
                html.Div(
                    dcc.Dropdown(
                        id="dropdown",
                        options=[
                            {"label": "Deaths", "value": "deaths"},
                            {"label": "Confirmed cases", "value": "confirmed cases"},
                        ],
                        value="confirmed cases",
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
                html.Div(
                    dcc.Dropdown(
                        id="axis_dropdown",
                        options=[
                            {"label": "Linear", "value": "linear"},
                            {"label": "Logarithmic", "value": "log"},
                        ],
                        value="log",
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            dcc.Graph(
                id="graph1", style={"height": "600px", "width": "85vw"}, responsive=True
            ),
            className="twelve columns",
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
        ## New confirmed cases/deaths per day
        Click on countries in the legend to hide or show them

        """
                ),
            ],
            className="twelve columns",
        ),
        html.Div(
            [
                html.Div(
                    dcc.Dropdown(
                        id="dropdown2",
                        options=[
                            {"label": "Deaths", "value": "deaths"},
                            {"label": "Confirmed cases", "value": "confirmed cases"},
                        ],
                        value="confirmed cases",
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
                html.Div(
                    dcc.Dropdown(
                        id="axis_dropdown2",
                        options=[
                            {"label": "Linear", "value": "linear"},
                            {"label": "Logarithmic", "value": "log"},
                        ],
                        value="log",
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
                html.Div(
                    dcc.Dropdown(
                        id="window_selector",
                        options=[
                            {
                                "label": "Rolling mean: {}".format(ii + 1),
                                "value": ii + 1,
                            }
                            for ii in range(14)
                        ],
                        value=7,
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            dcc.Graph(
                id="graph2", style={"height": "600px", "width": "85vw"}, responsive=True
            ),
            className="twelve columns",
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
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
        Click on countries in the legend to hide or show them
        """
                ),
            ],
            className="twelve columns",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="dropdown3",
                            options=[
                                {"label": "Deaths", "value": "deaths"},
                                {
                                    "label": "Confirmed cases",
                                    "value": "confirmed cases",
                                },
                            ],
                            value="confirmed cases",
                            style=dropdown_style,
                        ),
                    ],
                    className="three columns",
                ),
                html.Div(
                    dcc.Dropdown(
                        id="window_selector2",
                        options=[
                            {
                                "label": "Rolling mean: {}".format(ii + 1),
                                "value": ii + 1,
                            }
                            for ii in range(14)
                        ],
                        value=7,
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            dcc.Graph(
                id="graph3", style={"height": "600px", "width": "85vw"}, responsive=True
            ),
            className="twelve columns",
        ),
        html.Div(
            [
                dcc.Markdown(
                    """
        ## A closer look at Sweden
        Click on regions in the legend to hide or show them

        Data presented here is taken from the Swedish Health Authorities'
        [website](https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/bekraftade-fall-i-sverige/)
        (www.folkhalsomyndigheten.se).
        """
                ),
            ],
            className="twelve columns",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="dropdown_sweden",
                            options=[
                                {"label": "New cases", "value": "new"},
                                {"label": "Total cases", "value": "total"},
                            ],
                            value="new",
                            style=dropdown_style,
                        ),
                    ],
                    className="three columns",
                ),
                html.Div(
                    dcc.Dropdown(
                        id="axis_dropdown_sweden",
                        options=[
                            {"label": "Linear", "value": "linear"},
                            {"label": "Logarithmic", "value": "log"},
                        ],
                        value="log",
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
                html.Div(
                    dcc.Dropdown(
                        id="window_selector_sweden",
                        options=[
                            {
                                "label": "Rolling mean: {}".format(ii + 1),
                                "value": ii + 1,
                            }
                            for ii in range(14)
                        ],
                        value=7,
                        style=dropdown_style,
                    ),
                    className="three columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            dcc.Graph(
                id="graph_sweden",
                style={"height": "600px", "width": "85vw"},
                responsive=True,
            ),
            className="twelve columns",
        ),
    ]
)


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
        o
        for o in country_options
        if (search_value in o["label"] or o["value"] in (value or []))
        or (search_value.capitalize() in o["label"] or o["value"] in (value or []))
    ]


@app.callback(
    Output("graph1", "figure"),
    [
        Input("dropdown", "value"),
        Input("axis_dropdown", "value"),
        Input("country_dropdown", "value"),
        Input("button1", "n_clicks"),
        Input("reset_button", "n_clicks"),
    ],
)
def update_figure(
    selected_cases, selected_axis_type, selected_countries, button, reset
):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "button1" in changed_id:
        selected_countries = ["Sweden", "Denmark", "Finland", "Norway"]
        selected_countries.sort()
    elif "reset_button" in changed_id or (
        reset == 0 and button == 0 and selected_countries == get_start_conutries()
    ):
        selected_countries = start_countries
        selected_countries.sort()

    if selected_cases == "confirmed cases":
        df = df_conf_all[selected_countries]
    elif selected_cases == "deaths":
        df = df_deaths_all[selected_countries]

    traces, layout = total_vs_time(df, descr=selected_cases)

    layout.update(
        dict(
            xaxis={"title": "Date", "gridcolor": gridcolor,},
            yaxis={
                "title": "Total {}".format(selected_cases),
                "type": selected_axis_type,
                "gridcolor": gridcolor,
            },
        )
    )
    layout.update(extra_layout_vars)
    return {
        "data": traces,
        "layout": layout,
    }


@app.callback(
    Output("graph2", "figure"),
    [
        Input("dropdown2", "value"),
        Input("axis_dropdown2", "value"),
        Input("window_selector", "value"),
        Input("country_dropdown", "value"),
        Input("button1", "n_clicks"),
        Input("reset_button", "n_clicks"),
    ],
)
def update_figure2(
    selected_cases,
    selected_axis_type,
    selected_window,
    selected_countries,
    button,
    reset,
):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "button1" in changed_id:
        selected_countries = ["Sweden", "Denmark", "Finland", "Norway"]
        selected_countries.sort()
    # Checking if buttons have 0 clicks makes sure the figures are rendered correctly first time app loads
    elif "reset_button" in changed_id or (
        reset == 0 and button == 0 and selected_countries == get_start_conutries()
    ):
        selected_countries = start_countries
        selected_countries.sort()

    if selected_cases == "confirmed cases":
        df = df_conf_all[selected_countries]
    elif selected_cases == "deaths":
        df = df_deaths_all[selected_countries]

    traces, layout = new_vs_time(df, descr=selected_cases, window=selected_window)

    layout.update(
        dict(
            xaxis={"title": "Date", "gridcolor": gridcolor,},
            yaxis={
                "title": "New {}".format(selected_cases),
                "type": selected_axis_type,
                "gridcolor": gridcolor,
            },
        )
    )
    layout.update(extra_layout_vars)
    return {
        "data": traces,
        "layout": layout,
    }


@app.callback(
    Output("country_dropdown", "value"),
    [Input("button1", "n_clicks"), Input("reset_button", "n_clicks")],
)
def update_drowdown2(button, reset):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "button1" in changed_id:
        return ["Sweden", "Denmark", "Finland", "Norway"]
    elif "reset_button" in changed_id or (reset == 0 and button == 0):
        return get_start_conutries()


@app.callback(
    Output("graph3", "figure"),
    [
        Input("dropdown3", "value"),
        Input("window_selector2", "value"),
        Input("country_dropdown", "value"),
        Input("button1", "n_clicks"),
        Input("reset_button", "n_clicks"),
    ],
)
def update_figure3(
    selected_cases, selected_window, selected_countries, button, reset,
):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "button1" in changed_id:
        selected_countries = ["Sweden", "Denmark", "Finland", "Norway"]
        selected_countries.sort()
    elif "reset_button" in changed_id or (
        reset == 0 and button == 0 and selected_countries == get_start_conutries()
    ):
        selected_countries = start_countries
        selected_countries.sort()

    if selected_cases == "confirmed cases":
        df = df_conf_all[selected_countries]
    elif selected_cases == "deaths":
        df = df_deaths_all[selected_countries]

    traces, layout = new_vs_total(df, window=selected_window)

    layout.update(
        dict(
            xaxis={
                "title": "Total {}".format(selected_cases),
                "type": "log",
                "gridcolor": gridcolor,
            },
            yaxis={
                "title": "New {}".format(selected_cases),
                "type": "log",
                "gridcolor": gridcolor,
            },
        )
    )
    layout.update(extra_layout_vars)
    return {
        "data": traces,
        "layout": layout,
    }


@app.callback(
    Output("graph_sweden", "figure"),
    [
        Input("dropdown_sweden", "value"),
        Input("axis_dropdown_sweden", "value"),
        Input("window_selector_sweden", "value"),
    ],
)
def update_figure4(
    selected_cases, selected_axis_type, selected_window,
):

    df = sheets[0]
    if selected_cases == "total":
        traces, layout = landskap(df, total=True, window=selected_window)
    elif selected_cases == "new":
        traces, layout = landskap(df, total=False, window=selected_window)
    else:
        print("Something went wrong")

    layout.update(
        dict(
            xaxis={"title": "Date", "gridcolor": gridcolor,},
            yaxis={
                "title": selected_cases.capitalize() + " cases",
                "type": selected_axis_type,
                "gridcolor": gridcolor,
            },
        )
    )
    layout.update(extra_layout_vars)
    return {
        "data": traces,
        "layout": layout,
    }


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
