#!/usr/bin/env python3

import sys
from types import FunctionType
import pandas as pd
from pandas.core.frame import DataFrame
import requests
from requests.exceptions import HTTPError
from requests.models import Response


def extract_args(args: list):
    filters = {}
    for i in args:
        if '--source' in i:
            source: list[str] = i.split("=")
            filters['sources'] = source[1].split(",")
        if '--date-range' in i:
            rng: list[str] = i.split("=")
            filters['date_range'] = rng[1].split(",")
    return filters


def transform_date(period: str):
    if "MM" in period:
        year = period[:4]
        month = period[-2:]
        return "{year}-{month}-01".format(year=year, month=month)

    else:
        return None


def transform_gas(dataframe: DataFrame):
    dataframe['Date'] = pd.to_datetime(
        dataframe['Periods'].apply(transform_date))
    dataframe = dataframe.dropna(subset=['Date'])
    dataframe = dataframe.assign(
        Value=dataframe['ElectricityPowerPlants_12'],
        Time=dataframe['Date'].dt.strftime('%H:%M'),
        Frequency='monthly',
        Commodity='gas',
        Unit='mlnm3'
    )
    return dataframe[['Date', 'Time', 'Value', 'Commodity', 'Frequency', 'Unit']]


def transform_electricity(dataframe: DataFrame):
    dataframe['Date'] = pd.to_datetime(
        dataframe['Periods'].apply(transform_date))
    dataframe = dataframe.dropna(subset=['Date'])
    prod_df = dataframe.assign(
        Value=dataframe['NetProductionTotal_3'],
        Time=dataframe['Date'].dt.strftime('%H:%M'),
        Frequency='monthly',
        Commodity='el-prod',
        Unit='mlnkWh'
    )
    consume_df = dataframe.assign(
        Value=dataframe['NetConsumptionCalculated_30'],
        Time=dataframe['Date'].dt.strftime('%H:%M'),
        Frequency='monthly',
        Commodity='el-cons',
        Unit='mlnkWh'
    )
    frames = [
        prod_df[['Date', 'Time', 'Value', 'Commodity', 'Frequency', 'Unit']],
        consume_df[['Date', 'Time', 'Value', 'Commodity', 'Frequency', 'Unit']]
    ]
    return pd.concat(frames).sort_values(by='Date')


def filter_year(df: DataFrame, year: int, item):
    year_2018 = df[df['Date'].dt.year == year]
    year_2018.to_csv('{title}_2018.csv'.format(
        title=item), index=False)


def filter_date_range(df: DataFrame, date_range: list):
    min_date = min(date_range)
    max_date = max(date_range)
    return df[(df['Date'] > min_date) & (df['Date'] < max_date)]


def get_data(url: str, transformer: FunctionType, date_range: list):
    try:
        resp: Response = requests.get(url)
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}', file=sys.stderr)
    except Exception as err:
        print(f'Other error occurred: {err}', file=sys.stderr)
    else:
        data: dict = resp.json()
        df: DataFrame = pd.DataFrame(data.get('value'))
        return transformer(df)


config = {
    "gas": {
        "url": "https://opendata.cbs.nl/ODataApi/odata/00372eng/TypedDataSet",
        "transformer": transform_gas
    },
    "electricity": {
        "url": "https://opendata.cbs.nl/ODataApi/odata/84575ENG/TypedDataSet",
        "transformer": transform_electricity
    }
}


if __name__ == '__main__':
    list_of_dfs: dict = {}
    filters: dict = extract_args(sys.argv[1:])
    sources = filters.get('sources')
    date_range = filters.get('date_range')

    # check for source argument of command line
    if sources:
        for item in sources:
            df: DataFrame = get_data(
                url=config.get(item).get('url'),
                transformer=config.get(item).get('transformer'),
                date_range=date_range
            )
            list_of_dfs[item] = df

    else:
        for title, values in config.items():
            df: DataFrame = get_data(
                url=values.get('url'),
                transformer=values.get('transformer'),
                date_range=date_range
            )
            list_of_dfs[title] = df

    for title, df in list_of_dfs.items():
        filter_year(df=df, year=2018, item=title)

        if len(date_range) == 2:
            df = filter_date_range(df=df, date_range=date_range)

        df.to_csv('{t}.csv'.format(t=title), index=False)
