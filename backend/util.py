import json
import requests
import threading

def makeRequest(endpoint, headers, offset, maxReturned, baseKey, offsetKey, limitKey):
    try:
        response = requests.get(f'{endpoint}{offset}={offsetKey}&{limitKey}={maxReturned}', headers=headers).json()
    except:
        response[baseKey] = f'Error getting for offset: {offset}'
    return response


# TODO Make this available for post and put requests
def multiRequest(endpoint, maxReturned, totalToReturn, headers, startOffset=0, order=False, baseKey='items', offsetKey='offset', limitKey='limit'):
    callFit = totalToReturn / maxReturned
    numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1
    allItems = []
    allThreads = []

    endpoint += '&' if '?' in endpoint else '?'

    for i in range(startOffset, numOfCalls):
        offset = i * maxReturned
        if order:
            allItems.extend(makeRequest(endpoint, headers, offset, maxReturned, baseKey, offsetKey, limitKey)[baseKey])
        else:
            t = threading.Thread(target=lambda: allItems.extend(makeRequest(endpoint, headers, offset, maxReturned, baseKey, offsetKey, limitKey)[baseKey]))
            t.start()
            allThreads.append(t)

    for t in allThreads:
        t.join()

    return allItems

def prettyDict(d):
    print(json.dumps(d, indent=4))

def putInJsonFile(data, filename='output.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
