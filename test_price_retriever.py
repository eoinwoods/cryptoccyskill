import price_retriever
import unittest
from datetime import datetime
import json
from decimal import Decimal

class TestPriceRetriever(unittest.TestCase):


    def test_iso8601_conversion(self):
        ts = datetime(2017, 7, 1, 11, 45, 15)
        ts_str = price_retriever.timestamp_to_iso8601(ts)
        self.assertEqual(ts_str, "2017-07-01T11:45:15")

    # This really isn't a unit test as it needs to call a network service
    def test_get_prices(self):
        url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD,EUR,GBP"
        price_data = price_retriever.get_crypto_prices(url)
        self.assertTrue(price_data['LTC']['USD'] > 1.0)
        self.assertTrue(price_data['BTC']['EUR'] > 1.0)
        self.assertTrue(price_data['ETH']['GBP'] > 1.0)

    def test_create_database_record(self):
        price_str = '{ "ETH": {"EUR": 11.01, "GBP": 22.02, "USD": 33.03}, "BTC": {"EUR": 44.04, "GBP": 55.05, "USD": 66.06}, "LTC": {"EUR": 77.07, "GBP": 88.08, "USD": 99.09} }'
        price_json = json.loads(price_str)
        db_record = price_retriever.create_database_record(price_json)
        self.assertTrue(db_record['pricesTimestamp'])
        self.assertTrue(db_record['ETH']['GBP'] > 1.0)

    def test_prices_to_json(self):
        prices_data = {'GBP': 22.02, 'EUR': 11.01, 'USD': 33.03}
        json = price_retriever.prices_to_json(prices_data)
        self.assertEqual(json['GBP'], Decimal('22.02'))
        self.assertEqual(json['EUR'], Decimal('11.01'))
        self.assertEqual(json['USD'], Decimal('33.03'))
        
if __name__ == '__main__':
    unittest.main()