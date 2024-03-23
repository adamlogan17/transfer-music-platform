import json
import requests

def multiRequest(endpoint, maxReturned, totalToReturn, headers, startOffset=0, baseKey='items', offsetKey='offset', limitKey='limit'):
    callFit = totalToReturn / maxReturned
    numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1
    allItems = []

    endpoint += '&' if '?' in endpoint else '?'

    for i in range(startOffset, numOfCalls):
        offset = i * maxReturned
        try:
            response = requests.get(f'{endpoint}{offset}={offsetKey}&{limitKey}={maxReturned}', headers=headers).json()
        except:
            response[baseKey] = f'Error getting for off set: {offset}'
        allItems.extend(response[baseKey])
    return allItems

def prettyDict(d):
    print(json.dumps(d, indent=4))

def putInJsonFile(data, filename='output.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
