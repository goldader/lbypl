import requests
import csv
from datetime import datetime

client_id="goldader-znsm"
client_secret="xlbucdespuhv4zsdf8y2z"

token_url="https://auth.truelayer.com/connect/token"
red_url="https://console.truelayer.com/redirect-page"
access_code='dafbed9a729d46a51447f0849510f23a0f632ecca8e8af1fcba4676089507a75'
refresh_token='ae10e0615508755f575e99db5b16ddc374fb2285d5be3eb4f56d910c131712e5'
my_file='/Users/jgoldader/Desktop/truelayer.txt'
my_dict={}

def new_auth(access_code): #gets an access code from Truelayer that must then be turned into an access token
    payload = {'grant_type': 'authorization_code', 'client_id': client_id, \
               'client_secret': client_secret, 'redirect_uri': red_url, 'code': access_code}
    z=requests.post('https://auth.truelayer.com/connect/token',data=payload)
    if z.status_code==200:
        #print(z.json())
        return(z.json())
    else:
        print('Authorisation failed with status code %s ' % z.status_code)
        return(z.status_code)

def refresh_auth(refresh_token):
    payload = {'grant_type': 'refresh_token', 'client_id': client_id, \
               'client_secret': client_secret, 'refresh_token': refresh_token}
    z=requests.post('https://auth.truelayer.com/connect/token', data=payload)
    if z.status_code==200:
        #print(z.json())
        return(z.json())
    else:
        print('Refresh failed with status code %s ' % z.status_code)
        return(z.status_code)

#my_dict=new_auth(access_code)
my_dict=refresh_auth(refresh_token)
call_time=datetime.now() #used to set the time for token refresh

#refresh_auth(refresh_token)
with open(my_file,"a",newline='') as f:
    for k , v in my_dict.items():
        f.write('"%s","%s"\n' % (k,v))
    f.write('"time","%s"\n' % call_time)
    if f.closed==False:
        f.close()

