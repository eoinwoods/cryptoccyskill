import crypto_prices_skill
import unittest
import datetime
import json

class TestCryptoPricesSkill(unittest.TestCase):


    # This isn't a unit test as it connects to AWS
    def test_get_latest_timestamp(self):
        ts = crypto_prices_skill.get_latest_timestamp()

    def test_time_difference(self):
        ts = datetime.datetime.now()
        ts2 = ts + datetime.timedelta(0, 130)
        self.assertEquals(2, crypto_prices_skill.calc_time_difference_in_minutes(ts, ts2))

    def test_time_difference_less_than_one_minute(self):
        ts = datetime.datetime.now()
        ts2 = ts + datetime.timedelta(0, 20)
        self.assertEquals(0, crypto_prices_skill.calc_time_difference_in_minutes(ts, ts2))

    def test_prices_converted_to_text(self):
        json_record = '{"pricesTimestamp" : "2017-07-30T21:01:35.793823", "ETH": {"EUR": 1.0, "GBP": 2.0, "USD": 3.0}, "BTC": {"EUR": 4.0, "GBP": 5.0, "USD": 6.0}, "LTC": {"EUR": 7.0, "GBP": 8.0, "USD": 9.0}}'
        text = crypto_prices_skill.json_prices_to_text(json.loads(json_record))
        print("CONV TEXT:" + str(text))
        self.assertTrue(len(text) > 20)
        self.assertRegex(text, ".*Bitcoin.*Ethereum.*Litecoin.*")

    # This isn't a unit test as it connects to AWS
    def test_get_prices(self):
        ts = crypto_prices_skill.get_latest_timestamp()
        resp = crypto_prices_skill.get_latest_prices(ts)

    # This isn't a unit test as it connects to AWS
    def test_prices_response(self):
        resp = crypto_prices_skill.get_prices_response()
        prices_text = resp['response']['outputSpeech']['text']
        self.assertTrue(len(prices_text) > 30)
        self.assertRegex(prices_text, "[0-9][0-9]* minutes ago, Bitcoin cost [0-9]*\.[0-9]* dollars, Ethereum cost [0-9]*\.[0-9]* dollars, Litecoin cost [0-9]*\.[0-9]* dollars") 

    def test_new_session(self):
        event = {
            'request' : {
                'requestId' : "Req123",
                'type' : "NONE"
            },
            'session' : {
                'sessionId' : "Session123",
                'application' : {
                    'applicationId' : "App123"
                },
                'new' : True
            }
        }
        crypto_prices_skill.lambda_handler(event, {})
        self.assertTrue(True)

    def test_launch_request(self):
        event = {
            'request' : {
                'requestId' : "Req123",
                'type' : "LaunchRequest"
            },
            'session' : {
                'sessionId' : "Session123",
                'application' : {
                    'applicationId' : "App123"
                },
                'new' : False
            }
        }
        output = crypto_prices_skill.lambda_handler(event, {})
        response = output['response']
        self.assertRegex((response['outputSpeech']['text']), "[0-9][0-9]* minutes ago, .*")

    def test_intent_request(self):
        event = {
            'request' : {
                'requestId' : "Req123",
                'type' : "IntentRequest"
            },
            'session' : {
                'sessionId' : "Session123",
                'application' : {
                    'applicationId' : "App123"
                },
                'new' : False
            }
        }
        output = crypto_prices_skill.lambda_handler(event, {})
        response = output['response']
        self.assertRegex((response['outputSpeech']['text']), "[0-9][0-9]* minutes ago, .*")

    def test_session_ended_request(self):
        event = {
            'request' : {
                'requestId' : "Req123",
                'type' : "SessionEndedRequest"
            },
            'session' : {
                'sessionId' : "Session123",
                'application' : {
                    'applicationId' : "App123"
                },
                'new' : False
            }
        }
        crypto_prices_skill.lambda_handler(event, {})
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()