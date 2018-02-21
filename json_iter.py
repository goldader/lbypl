"""module for accessing data via truelayer for a given account"""

import auth
import requests

def depth(x):
    if type(x) is dict and x:
        return 1 + max(depth(x[a]) for a in x)
    if type(x) is list and x:
        return 1 + max(depth(a) for a in x)
    return 0

def dict_generator2(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in dict_generator2(value, [key] + pre):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in dict_generator2(v, [key] + pre):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield pre + [indict]

def json_output(json_input):
    a = dict_generator2(json_input)
    dataset = {}
    try:
        a = dict_generator2(json_input)
        while True:
            value = next(a)
            if len(value) > 2:
                value.pop(0)
            # print(value)
            dataset[value[0]] = value[1]
    except StopIteration:
        pass
    finally:
        return(dataset)

auth.Auth('bill@fred.com')
token=auth.access_token('mock')

info_url="https://api.truelayer.com/data/v1/info"
token_phrase="Bearer %s" % token
headers = {'Authorization': token_phrase}

z=requests.get(info_url, headers=headers)

all_results=z.json()
results=all_results['results']

for i in range(0,len(results)):
    print(json_output(results[i]))