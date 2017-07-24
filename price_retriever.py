import json
import requests
import boto3
from datetime import datetime

REGION = "eu-west-1"
DATABASE_TABLE = "cryptoPricesTable"
# TODO - should be environment really
PRICE_URL = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD,EUR,GBP"

def timestamp_to_iso8601(timestamp):
    return timestamp.isoformat()

def get_crypto_prices(url):
    resp = requests.get(url)
    return resp.json()

def create_database_record(prices_doc):
    ts = timestamp_to_iso8601(datetime.now())
    db_record = prices_doc
    db_record['timestamp'] = ts
    return db_record

def insert_database_record(db_record_json, table_name, aws_region):
    dynamo = boto3.resource("dynamodb", region_name=aws_region)
    table = dynamo.Table(table_name)
    response = table.put_item(
        Item={
            'timestamp': db_record_json['timestamp'],
            'BTC': json.dumps(db_record_json['BTC']),
            'ETH': json.dumps(db_record_json['ETH']),
            'LTC': json.dumps(db_record_json['LTC'])
        }
    )
    return response

def get_prices(event, context):

    price_data = get_crypto_prices(PRICE_URL)
    db_record = create_database_record(price_data)
    insert_database_record(db_record, DATABASE_TABLE, REGION)

    return {
        "message": "Got crypto price data at " + db_record['timestamp'],
        "event": event
    }
