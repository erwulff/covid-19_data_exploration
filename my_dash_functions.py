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
        traces.append(
            dict(
                line=dict(width=width),
                mode='lines+markers',
                name=str(country),
                x=date_list,
                y=df[country]))

    layout = dict(
        title='Total Covid-19{}'.format(descr),
        autosize=True,
        width=800,
        height=600,
    )

    return traces, layout


def new_vs_total(df, descr, window=1):
    # Create figure
    traces = []

    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        traces.append(
            dict(
                line=dict(width=width),
                name=str(country),
                mode='lines+markers',
                x=df[country].rolling(window=window).mean(),
                y=df.diff()[country].rolling(window=window).mean()))

    layout = dict(title='Rolling mean of {} days'.format(window),
                  autosize=True,
                  width=800,
                  height=600,
                  )
    return traces, layout


def new_vs_time(df, descr, window=1):
    date_list = datetimeify(df.index)

    # Create figure
    traces = []
    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        traces.append(
            dict(
                line=dict(width=width),
                mode='lines+markers',
                name=str(country),
                x=date_list[39:],
                y=df.iloc[39:].diff()[country].rolling(window).mean()))

    layout = dict(
        title='New Covid-19 {} rolling mean of {} days'.format(descr, window),
        autosize=True,
        width=800,
        height=600,
    )

    return traces, layout
