import unittest
from pandas.core.frame import DataFrame
import json
import cbs
import pandas as pd


class TestCBSElectricityAndGas(unittest.TestCase):

    def test_extract_args(self):
        args = list(['--source=00372eng,84575ENG',
                     '--date-range=2018-01-01,2016-06-01',
                     '--year=2020'])
        filters = cbs.extract_args(args)
        sources: list = filters.get('sources')
        date_range = filters.get('date_range')

        self.assertEqual(len(sources), 2)
        self.assertTrue("00372eng" in sources)
        self.assertEqual(len(date_range), 2)
        self.assertTrue("2018-01-01" in date_range)

    def test_transform_date(self):
        period = '2021MM03'
        quarterly_period = '2021KW01'
        td = cbs.transform_date(period)
        tn = cbs.transform_date(quarterly_period)

        self.assertEqual(td, '2021-03-01')
        self.assertIsNone(tn)

    def test_transform_gas(self):
        df = cbs.transformer(
            dataframe=pd.read_csv('test_datasets/gas_test.csv'),
            datasets_url=cbs.get_urls("00372eng"),
            column="ElectricityPowerPlants_12",
            commodity="gas")
        result_df = pd.read_csv('test_datasets/gas.csv')

        self.assertEqual(df.size, result_df.size)
        self.assertEqual(df.columns.size, result_df.columns.size)

    def test_transform_electricity(self):
        el_prods_df = cbs.transformer(
            dataframe=pd.read_csv('test_datasets/electricity_test.csv'),
            datasets_url=cbs.get_urls('84575ENG'),
            column="NetProductionTotal_3",
            commodity="el_prods")
        el_cons_df = cbs.transformer(
            dataframe=pd.read_csv('test_datasets/electricity_test.csv'),
            datasets_url=cbs.get_urls('84575ENG'),
            column="NetConsumptionCalculated_30",
            commodity="el_cons")
        result_df = pd.read_csv('test_datasets/electricity.csv')
        dfs = [el_prods_df, el_cons_df]
        agg_dfs = pd.concat(dfs)

        self.assertEqual(agg_dfs.size, result_df.size)
        self.assertEqual(agg_dfs.columns.size, result_df.columns.size)
        self.assertEqual(el_cons_df.size, el_prods_df.size)

    def test_find_value_in_list_of_dicts(self):
        value = cbs.find_value_in_list_of_dicts(
            key="name",
            value="jane",
            ret_key="fname",
            list_of_dict=[{"name": "jane", "fname": "doe"},
                          {"name": "john", "fname": "bean"}]
        )
        self.assertEqual(value, "doe")

    def test_filter_date_range(self):
        df: DataFrame = cbs.filter_date_range(
            df=pd.read_csv('test_datasets/gas.csv'),
            date_range=['2020-12-01', '2021-03-01'])
        self.assertEqual(df[df['Date'] < "2020-12-01"].size, 0)
        self.assertEqual(df[df['Date'] > "2021-03-01"].size, 0)

    def test_get_data(self):
        config: dict = {}
        with open('config.json', 'r') as c:
            config = json.load(c)
        datasets_url = cbs.get_urls("00372eng")
        config["00372eng"]['datasets'] = datasets_url
        df = cbs.get_data(config=config, item="00372eng")
        self.assertIsNotNone(df)


if __name__ == '__main__':
    unittest.main()
