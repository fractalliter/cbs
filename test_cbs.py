import unittest
from cbs_elec_gas import extract_args, transform_date, transform_electricity, transform_gas, get_data, config
import pandas as pd


class TestCBSElectricityAndGas(unittest.TestCase):

    def test_extract_args(self):
        args = list(['--source=gas,electricity',
                     '--date-range=2018-01-01,2016-06-01'])
        filters = extract_args(args)
        self.assertEqual(len(filters.get('sources')), 2)
        self.assertEqual(len(filters.get('date_range')), 2)

    def test_transform_date(self):
        period = '2021MM03'
        quarterly_period = '2021KW01'
        td = transform_date(period)
        self.assertEqual(td, '2021-03-01')
        tn = transform_date(quarterly_period)
        self.assertIsNone(tn)

    def test_transform_gas(self):
        df = transform_gas(pd.read_csv('test_datasets/gas_test.csv'))
        result_df = pd.read_csv('test_datasets/gas.csv')
        self.assertEqual(df.size, result_df.size)
        self.assertEqual(df.columns.size, result_df.columns.size)

    def test_transform_electricity(self):
        df = transform_electricity(pd.read_csv(
            'test_datasets/electricity_test.csv'))
        result_df = pd.read_csv('test_datasets/electricity.csv')
        self.assertEqual(df.size, result_df.size)
        self.assertEqual(df.columns.size, result_df.columns.size)
        com_df = df['Commodity']
        com_res_df = result_df['Commodity']
        self.assertEqual(com_df.where(com_df == 'el_prod').size,
                         com_res_df.where(com_res_df == 'el_cons').size)

    def test_get_data(self):
        # elec = config.get('electricity')
        # df = get_data(
        #         url=elec.get('url'),
        #         transformer=elec.get('transformer'),
        #     )
        pass


if __name__ == '__main__':
    unittest.main()
