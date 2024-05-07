import json
import requests
import threading
import copy


def make_request(
    endpoint,
    headers,
    offset,
    max_returned,
    base_key,
    offset_key,
    limit_key,
    request_type,
    body,
):
    response = {}
    try:
        if request_type == "GET":
            response = requests.get(
                f"{endpoint}{offset_key}={offset}&{limit_key}={max_returned}",
                headers=headers,
            ).json()
        elif request_type == "POST":
            response = requests.post(
                f"{endpoint}{offset_key}={offset}&{limit_key}={max_returned}",
                headers=headers,
                json=body,
            ).json()
        elif request_type == "PUT":
            response = requests.put(
                f"{endpoint}{offset_key}={offset}&{limit_key}={max_returned}",
                headers=headers,
                json=body,
            ).json()
        elif request_type == "DELETE":
            response = requests.delete(
                f"{endpoint}{offset_key}={offset}&{limit_key}={max_returned}",
                headers=headers,
            ).json()
    except:
        response[base_key] = f"Error getting for offset: {offset}"
    return response


# TODO Make this available for post and put requests
def multi_request(
    endpoint,
    max_returned,
    total_to_return,
    headers,
    start_offset=0,
    base_key="items",
    offset_key="offset",
    limit_key="limit",
    request_type="GET",
    body={},
):
    endpoint += "&" if "?" in endpoint else "?"

    return multi_thread_request(
        lambda offset: make_request(
            endpoint,
            headers,
            offset,
            max_returned,
            base_key,
            offset_key,
            limit_key,
            request_type,
            body,
        )[base_key],
        max_returned,
        total_to_return,
        start_offset=start_offset,
    )


def pretty_dict(d):
    print(json.dumps(d, indent=4))


def put_in_json_file(data, filename="output.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def get_nested_item(data, path):
    for key in path:
        data = data[key]
    return data


def multi_thread_request(request, max_returned, total_to_return, start_offset=0):
    call_fit = total_to_return / max_returned
    num_of_calls = int(call_fit) if call_fit.is_integer() else int(call_fit) + 1
    all_items = [None for i in range(start_offset, num_of_calls)]
    all_threads = []
    for i in range(start_offset, num_of_calls):
        offset = i * max_returned
        # for some reason when this is not a lambda function, it simply
        # waits until one thread is finished to start the next one
        t = threading.Thread(
            target=lambda i, offset: add_unique_id(all_items, request(offset), i),
            args=(i, offset),
        )
        t.start()
        all_threads.append(t)

    for t in all_threads:
        t.join()

    # as the 'request' function may return a list of its own this needs to be spread and entered into the returned array
    one_dim_array = []

    for item in all_items:
        extend_or_append(one_dim_array, item)

    return one_dim_array


def add_unique_id(data, value, id):
    data[id] = value


def extend_or_append(data, value):
    if type(value) == list:
        data.extend(value)
    else:
        data.append(value)
