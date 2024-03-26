import json
import requests
import threading
import copy

def makeRequest(endpoint, headers, offset, maxReturned, baseKey, offsetKey, limitKey, requestType, body):
    response = {}
    try:
        if requestType == 'GET':
            response = requests.get(f'{endpoint}{offsetKey}={offset}&{limitKey}={maxReturned}', headers=headers).json()
        elif requestType == 'POST':
            response = requests.post(f'{endpoint}{offsetKey}={offset}&{limitKey}={maxReturned}', headers=headers, json=body).json()
        elif requestType == 'PUT':
            response = requests.put(f'{endpoint}{offsetKey}={offset}&{limitKey}={maxReturned}', headers=headers, json=body).json()
        elif requestType == 'DELETE':
            response = requests.delete(f'{endpoint}{offsetKey}={offset}&{limitKey}={maxReturned}', headers=headers).json()
    except:
        response[baseKey] = f'Error getting for offset: {offset}'
    return response


# TODO Make this available for post and put requests
def multiRequest(endpoint, maxReturned, totalToReturn, headers, startOffset=0, order=False, baseKey='items', offsetKey='offset', limitKey='limit', requestType='GET', body={}):
    endpoint += '&' if '?' in endpoint else '?'

    return multiThreadRequest(lambda offset: makeRequest(endpoint, headers, offset, maxReturned, baseKey, offsetKey, limitKey, requestType, body)[baseKey], maxReturned, totalToReturn, startOffset, order)

def prettyDict(d):
    print(json.dumps(d, indent=4))

def putInJsonFile(data, filename='output.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def getNestedItem(data, path):
    for key in path:
        data = data[key]
    return data

def multiThreadRequest(request, maxReturned, totalToReturn, startOffset=0, order=False):
    callFit = totalToReturn / maxReturned
    numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1
    allItems = []
    allThreads = []
    for i in range(startOffset, numOfCalls):
        offset = i * maxReturned
        if order:
            extendOrAppend(allItems, request(offset))
        else:
            # for some reason when this is not a lambda function, it simply waits until one thread is finished to start the next one
            t = threading.Thread(target=lambda: extendOrAppend(allItems, request(offset)))
            t.start()
            allThreads.append(t)

    for t in allThreads:
        t.join()
    
    return allItems

def extendOrAppend(data, value):
    if type(value) == list:
        data.extend(value)
    else:
        data.append(value)
