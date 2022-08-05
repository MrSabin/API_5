import requests

base_api_url = "https://api.hh.ru/vacancies"
payload = {"HH-User-Agent": "dvmn_salary", "professional_role": "96"}
response = requests.get(base_api_url, params=payload)
print(response.text)
