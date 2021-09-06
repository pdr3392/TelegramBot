from decouple import config
import finnhub
import json

finnhub_client = finnhub.Client(api_key=config('FINNHUBCLIENT_API_KEY'))

test = finnhub_client.recommendation_trends('AAPL')

for item in test:
    if item['period'] >= '2021-01-01':
        print(item)

test2 = finnhub_client.financials_reported(symbol='AAPL', freq='annual')

print(json.dumps(test2, indent=4))
