import os
import time

import trio
from fastapi import FastAPI
from requests_futures.sessions import FuturesSession

if 'SPEECH_SERVICE_KEY' in os.environ:
    subscription_key = os.environ['SPEECH_SERVICE_KEY']
else:
    print('Environment variable for your subscription key is not set.')
    exit()

if 'SPEECH_SERVICE_REGION' in os.environ:
    subscription_region = os.environ['SPEECH_SERVICE_REGION']
else:
    subscription_region = 'westus'

TIMEOUT = 500
THRESHOLD = 50

refreshed_at = time.time()
request_count = 0
app = FastAPI()
session = FuturesSession()

async def async_fetch_token(region, key):
    global refreshed_at
    global request_count
    fetch_token_url = 'https://'+region+'.api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': key
    }
    future = session.post(fetch_token_url, headers=headers)
    response = future.result()
    refreshed_at = time.time()
    request_count += 1
    return response.content


def fetch_token(region, key):
    return trio.run(async_fetch_token, region, key)

token = fetch_token(subscription_region, subscription_key)

@app.get('/')
async def send_token():
    global subscription_region
    global subscription_key
    global refreshed_at
    global TIMEOUT
    global request_count
    global THRESHOLD
    global token
    while True:
        print('requested - ' + str(request_count))
        print('refreshed - ' + str(refreshed_at))
        time_passed = time.time() - refreshed_at
        if time_passed > TIMEOUT:
            request_count = 0
            token = await async_fetch_token(subscription_region, subscription_key)
            return {token}
        elif request_count > THRESHOLD:
            print('throttled - ' + str(request_count))
            trio.run(trio.sleep, 1)
        else:
            request_count += 1
            return {token}
