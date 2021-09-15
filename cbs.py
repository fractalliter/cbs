#!/usr/bin/env python3

import json
import sys
import pandas as pd
from pandas.core.frame import DataFrame
import requests
from requests.exceptions import HTTPError
from requests.models import Response

cbs = 'https://opendata.cbs.nl/ODataApi/odata/'


def find_value_in_list_of_dicts(
    key: str,
    value,
    ret_key: str,
    list_of_dict: "list[dict]"
):
    row: dict = next(x for x in list_of_dict if x[key] == value)
    return row.get(ret_key)


def extract_args(args: list) -> dict:
    filters = {}
    for arg in args:
        if '--source' in arg:
            source: list[str] = arg.split("=")
            filters['sources'] = source[1].split(",")
        if '--date-range' in arg:
            rng: list[str] = arg.split("=")
            filters['date_range'] = rng[1].split(",")
        if '--year' in arg:
            year: list = arg.split("=")
            filters['year'] = int(year[1])
    return filters


def transform_date(period: str) -> str:
    if "MM" in period:
        year = period[:4]
        month = period[-2:]
        return "{year}-{month}-01".format(year=year, month=month)

    else:
        return None


def transformer(
        dataframe: DataFrame,
        datasets_url: "list[dict]",
        column: str,
        commodity: str) -> DataFrame:
    table_info: Response = requests.get(find_value_in_list_of_dicts(
        'name', 'TableInfos', 'url', datasets_url))
    info = table_info.json()
    data_propertiese: Response = requests.get(find_value_in_list_of_dicts(
        'name', 'DataProperties', 'url', datasets_url))
    props = data_propertiese.json()

    dataframe['Date'] = pd.to_datetime(
        dataframe['Periods'].apply(transform_date))
    dataframe = dataframe.dropna(subset=['Date'])
    dataframe = dataframe.assign(
        Value=dataframe[column],
        Time=dataframe['Date'].dt.strftime('%H:%M'),
        Frequency=info.get('value')[0].get('Frequency'),
        Commodity=commodity,
        Unit=find_value_in_list_of_dicts(
            'Key', column, 'Unit', props.get('value')).replace(" ", "")
    )
    return dataframe[['Date', 'Time', 'Value', 'Commodity', 'Frequency', 'Unit']]


def filter_year(df: DataFrame, year: int, item):
    yearly: DataFrame = df[df['Date'].dt.year == year]
    yearly.to_csv('{title}_{year}.csv'.format(
        title=item, year=year), index=False)


def filter_date_range(df: DataFrame, date_range: list) -> DataFrame:
    min_date = min(date_range)
    max_date = max(date_range)
    return df[(df['Date'] > min_date) & (df['Date'] < max_date)]


def get_data(config: dict, item) -> DataFrame:
    datasets_url: list = config.get(item).get('datasets')
    columns: list = config.get(item).get('columns')
    commodity: dict = config.get(item).get('commodity')
    try:
        data: Response = requests.get('{url}?$select={columns}'.format(url=find_value_in_list_of_dicts(
            'name', 'TypedDataSet', 'url', datasets_url), columns=','.join(columns)))
        data.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}', file=sys.stderr)
    except Exception as err:
        print(f'Other error occurred: {err}', file=sys.stderr)
    else:
        data: dict = data.json()
        df: DataFrame = pd.DataFrame(data.get('value'))
        dt = []
        cols = columns[1:]
        if len(cols) > 1:
            for col in cols:
                d = transformer(
                    dataframe=df,
                    datasets_url=datasets_url,
                    column=col,
                    commodity=commodity.get(col))
                dt.append(d)
            return pd.concat(dt).sort_values(by='Date')
        else:
            return transformer(
                dataframe=df,
                datasets_url=datasets_url,
                column=columns[1],
                commodity=commodity.get(cols[0]))


def get_urls(dataset: str):
    data = requests.get(
        '{base_url}/{ds}'.format(base_url=cbs, ds=dataset))
    data = data.json()
    return data.get('value')


if __name__ == '__main__':
    configs: dict = {}
    dataframes: dict = {}
    filters: dict = extract_args(sys.argv[1:])
    sources: "list[str]" = filters.get('sources')
    date_range: "list[str]" = filters.get('date_range')

    with open('config.json') as c:
        configs = json.loads(c)
    for key, value in configs.items():
        datasets_url = get_urls(key)
        configs[key]['datasets'] = datasets_url

    # check for source argument from command line
    if sources:
        for item in sources:
            df: DataFrame = get_data(config=configs, item=item)
            dataframes[configs.get(item).get('title')] = df

    else:
        for title, values in configs.items():
            df: DataFrame = get_data(config=configs, item=title)
            dataframes[configs.get(title).get('title')] = df

    for title, df in dataframes.items():
        filter_year(df=df, year=filters.get('year') or 2018, item=title)

        if date_range and len(date_range) == 2:
            df = filter_date_range(df=df, date_range=date_range)

        df.to_csv('{t}.csv'.format(t=title), index=False)
