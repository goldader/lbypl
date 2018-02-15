import requests

url="https://auth.truelayer.com/api/providers"
providers={}

z=requests.get(url)
providers=(z.content)
print(providers)