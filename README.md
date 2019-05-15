# speech-api-server

## Token server

We don't have to expose subscription key to client.

```
cd token-server
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
SPEECH_SERVICE_KEY=the_key uvicorn token-server:app --reload
```
