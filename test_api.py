import requests
from random import randint
from requests.auth import HTTPBasicAuth

client_id="goldader-znsm"
client_secret="xlbucdespuhv4zsdf8y2z"
red_uri="https://console.truelayer.com/redirect-page&enable_mock=true"
scope="info%20accounts%20balance%20transactions%20cards%20offline_access"
nonce='2658939551' #randint(123456,123456789)
state="test"
response_type="code"
url='https://auth.truelayer.com/'

#auth_code="7339ab0699fd9d1a5e9328d6581e9843342da6b3b11a957e3794a621164cb14a"

payload={'response_type':response_type,'client_id':client_id,\
         'redirect_uri':red_uri,'scope':scope,'nonce':nonce,'state':state,'response_mode':'form_post'}
# redirect the user to the screen (or fake it with a login)
z = requests.get('https://auth.truelayer.com/?response_type=code&response_mode=form_post&client_id=goldader-znsm&nonce=2658939551&scope=info%20accounts%20balance%20transactions%20cards%20offline_access&redirect_uri=https://console.truelayer.com/redirect-page&enable_mock=true&connectorId=mock',auth=('john','doe'))
print(z)
print(z.status_code)
print(z.content)

a = requests.post(url,data=payload)
print("a = %s" % a)

""" to be used for a post for the token
 payload = {'key1': 'value1', 'key2': 'value2'}

>>> r = requests.post("http://httpbin.org/post", data=payload)
>>> print(r.text)

"""