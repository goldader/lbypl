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
    #flattens nested json for use in various data management activities
    a = dict_generator2(json_input)
    dataset = {}
    try:
        a = dict_generator2(json_input)
        previous=None
        count=0
        while True:
            value = next(a)
            if len(value)==3:
                value[0]+=".%s" % value[1]
                value.pop(1)
            if value[0].lower()==previous:
                count+=1
                value[0]+="_%s" % count
            else:
                count=0
                previous=value[0].lower()
            #print(value)
            dataset[value[0].lower()] = value[1]
    except StopIteration:
        pass
    finally:
        return(dataset)


"""
import sqlite3
from auth import Auth, access_token
import requests
import tbl_maint

conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
c = conn.cursor()

tbl_maint.Tbl_maint('tl_user_card_accounts')
Auth('bill@fred.com')
user=Auth.uid
c.execute("select distinct provider_id from tl_accounts where user_id=?",[user])
token = access_token(c.fetchone()[0])

info_url="https://api.truelayer.com/data/v1/cards"
token_phrase="Bearer %s" % token
headers = {'Authorization': token_phrase}

z=requests.get(info_url, headers=headers)

all_results=z.json()
results=all_results['results']
print("Results len %s - %s" % (len(results),results))

for i in range(0,len(results)):
    json_output_results=json_output(results[i])
    print("Json Output len %s - %s" % (len(json_output_results),json_output_results))
    tbl_maint.Tbl_maint.create_tbl(json_output_results)
    break
"""