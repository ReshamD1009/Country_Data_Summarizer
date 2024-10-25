import requests

api_url = 'https://api.api-ninjas.com/v1/country?name=india'
response = requests.get(api_url, headers={'X-Api-Key': 'cRBINTpjZI0EBPp3m+wcLQ==q18ceQBWOn2zV4m7'})
if response.status_code == requests.codes.ok:
    print(response.text)
else:
    print("Error:", response.status_code, response.text)
