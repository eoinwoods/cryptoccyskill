import crypto_prices_skill
import unittest
from datetime import datetime
import json

class TestCryptoPricesSkill(unittest.TestCase):

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
        self.assertTrue((response['outputSpeech']['text']).startswith("The crypto currency prices are"))

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
        crypto_prices_skill.lambda_handler(event, {})
        self.assertTrue(True)

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