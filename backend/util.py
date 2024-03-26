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
def multiRequest(endpoint, maxReturned, totalToReturn, headers, startOffset=0, baseKey='items', offsetKey='offset', limitKey='limit', requestType='GET', body={}):
    endpoint += '&' if '?' in endpoint else '?'

    return multiThreadRequest(lambda offset: makeRequest(endpoint, headers, offset, maxReturned, baseKey, offsetKey, limitKey, requestType, body)[baseKey], maxReturned, totalToReturn, startOffset=startOffset)

def prettyDict(d):
    print(json.dumps(d, indent=4))

def putInJsonFile(data, filename='output.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def getNestedItem(data, path):
    for key in path:
        data = data[key]
    return data

def multiThreadRequest(request, maxReturned, totalToReturn, startOffset=0):
    callFit = totalToReturn / maxReturned
    numOfCalls = int(callFit) if callFit.is_integer() else int(callFit) + 1
    allItems = [None for i in range(startOffset, numOfCalls)]
    allThreads = []
    for i in range(startOffset, numOfCalls):
        offset = i * maxReturned
        # for some reason when this is not a lambda function, it simply waits until one thread is finished to start the next one
        t = threading.Thread(target=lambda i, offset: addUniqueId(allItems, request(offset), i), args=(i, offset))
        t.start()
        allThreads.append(t)

    for t in allThreads:
        t.join()

    # as the 'request' function may return a list of its own this needs to be spread and entered into the returned array
    test = []

    for item in allItems:
        extendOrAppend(test, item)
    
    return test

def addUniqueId(data, value, id):
    data[id] = value

def extendOrAppend(data, value):
    if type(value) == list:
        data.extend(value)
    else:
        data.append(value)
