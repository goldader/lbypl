import requests

client_id="goldader-znsm"
client_secret="xlbucdespuhv4zsdf8y2z"

token_url="https://auth.truelayer.com/connect/token"
red_url="https://console.truelayer.com/redirect-page"
access_code='6f7eda26320258770a28ca90eac23ed43cdfa505860928e7c81f402ccfc84a82'
payload={'grant_type':'authorization_code','client_id':client_id,\
         'client_secret':client_secret,'redirect_uri':red_url,'code':access_code}

z=requests.post('https://auth.truelayer.com/connect/token',data=payload)
if z.status_code=='200':
    print(z)
    print(z.content)
    print(z.json)
else:
    print('Authorisation faile with status code %s ' % z.status_code)

#a=requests.post('https://auth.truelayer.com/connect/token?grant_type=authorization_code&client_id=goldader-znsm&client_secret=xlbucdespuhv4zsdf8y2z&redirect_uri=https://console.truelayer.com/redirect-page&code=6f7eda26320258770a28ca90eac23ed43cdfa505860928e7c81f402ccfc84a82')
#print(a)
#print(a.content)