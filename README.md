Crypto Prices Skill for Alexa
=============================

Two lambda functions, one to retrieve prices from a 3rd party network service every 10 minutes, one to respond to an Alexa request from the data.

Build and Deploy
----------------

Uses serverless to build and deploy, following AWS's instructions on packaging as the "request" library and its dependencies are needed as a dependency.

1. pip install request -t $PWD # install to this root directory
2. serverless test
3. serverless deploy --verbose

The serverless deployment will create an IAM role, the lambda functions and a DynamoDB table to hold the price data.
