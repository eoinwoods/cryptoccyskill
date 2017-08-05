import boto3
import env_settings as env
import datetime
import calendar
import json
import math

# TODO - should be environment really
REGION = env.REGION
PRICE_TABLE = env.PRICE_TABLE
LATEST_TABLE = env.LATEST_TABLE


def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_prices_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_prices_response()

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# -------------------- Utility procedures --------------

def calc_time_difference_in_minutes(startTime, endTime):
    return round((endTime - startTime).seconds/60)

def iso8601_timestamp_to_datetime(timestamp_string):
    return datetime.datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%S.%f")

def wrap_as_ssml(string):
    return "<speak>" + string + "</speak>"

def format_price(price):
    msg = ""

    (dollars, cents) = str(price).split(".")
    if (int(cents) > 0):
        msg = "{} dollars and {} cents".format(dollars, cents)
    else:
        msg = "{} dollars exactly".format(dollars)

    return msg

def json_prices_to_text(json_prices):
    price_msg_fragment = "Bitcoin cost {}, Ethereum cost {}, Litecoin cost {}"
    delayed_price_msg = wrap_as_ssml("{} minute{} ago, " + price_msg_fragment)
    # the odd markup in this string is SSML which you can find out more about at the URL
    # below - TLDR is that AWS Alexa uses it to direct the voice synthesis pronunciation
    # which we need for the word "minute"
    # Ref: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/speech-synthesis-markup-language-ssml-reference
    current_price_msg = wrap_as_ssml("less than a <phoneme alphabet='ipa' ph='mˈɪnɪt'>minute</phoneme> ago, " + \
                        price_msg_fragment)
    ts = iso8601_timestamp_to_datetime(json_prices["pricesTimestamp"]) 

    minutes_ago = calc_time_difference_in_minutes(ts, datetime.datetime.now())
    msg = ""
    if (minutes_ago < 1) :
        msg = current_price_msg.format(format_price(json_prices["BTC"]["USD"]), 
                                       format_price(json_prices["ETH"]["USD"]), 
                                       format_price(json_prices["LTC"]["USD"]))
    else:
        msg = delayed_price_msg.format(minutes_ago, 
                                       ("s" if minutes_ago > 1 else ""),
                                       format_price(json_prices["BTC"]["USD"]), 
                                       format_price(json_prices["ETH"]["USD"]), 
                                       format_price(json_prices["LTC"]["USD"]))
    return msg


# -------------------- Response handling procedures --------------

def get_prices_response():
    session_attributes = {}
    card_title = "Crypto Currency Prices"
    speech_output = get_prices_text()
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_prices_text():
    ts = get_latest_timestamp()
    prices = get_latest_prices(ts)
    return json_prices_to_text(prices)

def get_latest_timestamp():
    dynamo = boto3.resource("dynamodb", region_name=REGION)
    latestTable = dynamo.Table(LATEST_TABLE)
    latestResult = latestTable.get_item(
        Key = { 'latestKey' : "LATEST"}
    )
    latest_timestamp = latestResult['Item']['latestTimestamp']
    return latest_timestamp

def get_latest_prices(item_timestamp):
    dynamo = boto3.resource("dynamodb", region_name=REGION)
    pricesTable = dynamo.Table(PRICE_TABLE)
    pricesResult = pricesTable.get_item(
        Key = { 'pricesTimestamp' : item_timestamp}
    )
    return pricesResult['Item']


# --------------- Procedures to create response structures ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

