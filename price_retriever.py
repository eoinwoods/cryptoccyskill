import json
import requests
import boto3
import env_settings as env
from datetime import datetime
from decimal import Decimal
import decimal 

# TODO - should be environment really
REGION = env.REGION
PRICE_TABLE = env.PRICE_TABLE
LATEST_TABLE = env.LATEST_TABLE
PRICE_URL = env.PRICE_URL

PRICES_TIMESTAMP_COLUMN = "pricesTimestamp"

def timestamp_to_iso8601(timestamp):
    return timestamp.isoformat()

def get_crypto_prices(url):
    resp = requests.get(url)
    return resp.json()

def create_database_record(prices_doc):
    ts = timestamp_to_iso8601(datetime.now())
    db_record = prices_doc
    db_record[PRICES_TIMESTAMP_COLUMN] = ts
    return db_record

def prices_to_json(prices):
    ret = {}
    for ccy in prices:
        ret[ccy] = Decimal(str(prices[ccy]))
    return ret 

def insert_database_record(db_record_json, price_table_name, latest_table_name, aws_region):
    dynamo = boto3.resource("dynamodb", region_name=aws_region)
    priceTable = dynamo.Table(price_table_name)
    latestTable = dynamo.Table(latest_table_name)
    priceTable.put_item(
        Item={
            PRICES_TIMESTAMP_COLUMN : db_record_json[PRICES_TIMESTAMP_COLUMN],
            'BTC': prices_to_json(db_record_json['BTC']),
            'ETH': prices_to_json(db_record_json['ETH']),
            'LTC': prices_to_json(db_record_json['LTC'])
        }
    )
    latestTable.put_item(
        Item = {
            'latestKey' : 'LATEST',
            'latestTimestamp' : db_record_json[PRICES_TIMESTAMP_COLUMN]
        }
    )

def get_prices(event, context):
    price_data = get_crypto_prices(PRICE_URL)
    db_record = create_database_record(price_data)
    insert_database_record(db_record, PRICE_TABLE, LATEST_TABLE, REGION)

    return {
        "message": "Got crypto price data at " + db_record[PRICES_TIMESTAMP_COLUMN],
        "event": event
    }
