"""module to unpack Truelayer json responses into arrays or individual items"""
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
    #add code to automatically expand a second key of the same name with a 1,2,3 to ensure the list is correct
    a = dict_generator2(json_input)
    dataset = {}
    try:
        a = dict_generator2(json_input)
        previous=''
        count=0
        while True:
            value = next(a)
            if len(value) > 2:
                value.pop(0)
            if value[0]==previous:
                count+=1
                value[0]+=" - %s" % count
            else:
                count=0
            # print(value)
            dataset[value[0]] = value[1]
    except StopIteration:
        pass
    finally:
        return(dataset)

#""" lines used for testing and develompent

import auth
import requests

auth.Auth('bill@fred.com')
token=auth.access_token('mock')

info_url="https://api.truelayer.com/data/v1/info"
token_phrase="Bearer %s" % token
headers = {'Authorization': token_phrase}

z=requests.get(info_url, headers=headers)

all_results=z.json()
results=all_results['results']

x=dict_generator2(results[1])
for i in range(0,9):
    print(next(x))

for i in range(0,len(results)):
    #print(results[i])
    print(json_output(results[i]))

#"""