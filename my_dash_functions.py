import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

from utils import datetimeify


width = 2


def total_vs_time(df, descr):
    date_list = datetimeify(df.index)

    traces = []
    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        if country == 'Sweden':
            width = 4
        else:
            width = 2
        traces.append(
            dict(
                line=dict(width=width),
                mode='lines+markers',
                name=str(country),
                x=date_list,
                y=df[country]))

    layout = dict(
        title='Covid-19 {}'.format(descr),
        autosize=False,
        width=800,
        height=600,
    )

    return traces, layout


def new_vs_total(df, descr, window=1):
    # Create figure
    traces = []

    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        if country == 'Sweden':
            width = 4
        else:
            width = 2
        traces.append(
            dict(
                line=dict(width=width),
                name=str(country),
                mode='lines+markers',
                x=df[country].rolling(window=window).mean(),
                y=df.diff()[country].rolling(window=window).mean()))

    layout = dict(title='Covid-19 {} rolling mean of {} days'.format(descr, window),
                  autosize=False,
                  width=800,
                  height=600,
                  )
    return traces, layout


def new_vs_time(df, descr, window=1, countries=['Sweden', 'Norway', 'Denmark', 'Finland']):
    date_list = datetimeify(df.index)

    # Create figure
    traces = []
    # Add traces, one for each slider step
    for ii, country in enumerate(countries):
        traces.append(
            dict(
                line=dict(width=width),
                mode='lines+markers',
                name=str(country),
                x=date_list[39:],
                y=df.iloc[39:].diff()[country].rolling(window).mean()))

    layout = dict(
        title='Covid-19 new {} rolling mean of {} days'.format(descr, window),
        autosize=False,
        width=800,
        height=600,
    )

    return traces, layout
