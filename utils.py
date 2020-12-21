import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from pandas import ExcelWriter
from pandas import ExcelFile


def get_xl_sheets(file, nbr_of_sheets=6):
    """Returns a list of DataFrames where each DataFrame is a sheet of the excel
    file at `file`.

    Parameters
    ----------
    file : string
        Filename of, or path to, excel file.
    nbr_of_sheets : type
        Number of sheets to extract from the excel file. Must be equal to or
        lower than the actual number of sheets in the file.

    Returns
    -------
    List
        List of Dataframes.

    """
    sheets = []
    for ii in range(nbr_of_sheets):
        sheet = pd.read_excel(file, ii)
        sheets.append(sheet)
    return sheets


width = 2


def get_frame(name):
    url = (
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/'
        f'csse_covid_19_time_series/time_series_covid19_{name}_global.csv')
    return pd.read_csv(url, index_col='Country/Region')


def process_df(df):
    """Process DataFrame read from COVID-19 database

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
        processed DataFrame

    """
    df.pop('Province/State')
    df.pop('Lat')
    df.pop('Long')
    data_dict = {}

    for country in df.index.unique():
        if len(df.loc[country].shape) > 1:
            sum = df.loc[country].sum()
        else:
            sum = df.loc[country]
        data_dict[country] = sum

    return pd.DataFrame(data_dict)


def get_df(file_path):
    df = pd.read_csv(file_path, index_col='Country/Region')
    df = process_df(df)
    return df


def datetimeify(ind):
    date_list = []
    for ii, stamp in enumerate(ind):
        if len(stamp.split('/')[0]) == 1:
            stamp = '0' + stamp
        try:
            date = datetime.strptime(stamp, '%m/%d/%Y')
        except ValueError:
            date = datetime.strptime(stamp, '%m/%d/%y')

        date_list.append(date)
    return date_list


def total_vs_time(df, descr):
    date_list = datetimeify(df.index)
    # Create figure
    fig = go.Figure()

    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        if country == 'Sweden':
            width = 4
        else:
            width = 2
        fig.add_trace(
            go.Scatter(
                line=dict(width=width),
                name=str(country),
                x=date_list,
                y=df[country]))

    fig.update_layout(yaxis_type="log",
                      xaxis_title='Date',
                      yaxis_title='Covid-19 {}'.format(descr),
                      title='Covid-19 {}'.format(descr))

    fig.update_layout(
        autosize=False,
        width=950,
        height=750,)

    fig.show()


def new_vs_total(df, descr, window=1):
    # Create figure
    fig = go.Figure()

    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        if country == 'Sweden':
            width = 4
        else:
            width = 2
        fig.add_trace(
            go.Scatter(
                line=dict(width=width),
                name=str(country),
                x=df[country].rolling(window=window).mean(),
                y=df.diff()[country].rolling(window=window).mean()))

    fig.update_layout(yaxis_type="log",
                      xaxis_type='log',
                      yaxis_title='New {} per day'.format(descr),
                      xaxis_title='Total {}'.format(descr),
                      title='Covid-19 {} rolling mean of {} days'.format(descr, window))

    fig.update_layout(
        autosize=False,
        width=950,
        height=750,)

    fig.show()


def new_vs_time(df, descr, window=1):
    date_list = datetimeify(df.index)
    # Create figure
    fig = go.Figure()

    # Add traces, one for each slider step
    for ii, country in enumerate(df.keys()):
        fig.add_trace(
            go.Scatter(
                line=dict(width=width),
                mode='lines+markers',
                name=str(country),
                x=date_list[39:],
                y=df.iloc[39:].diff()[country].rolling(window).mean()))

    fig.update_layout(
        yaxis_title='New {} per day'.format(descr),
        xaxis_title='Date',
        title='Covid-19 new {} rolling mean of {} days'.format(descr, window))

    fig.update_layout(
        autosize=False,
        width=950,
        height=750,)

    fig.show()
