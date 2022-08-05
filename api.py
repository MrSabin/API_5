import requests

base_api_url = "https://api.hh.ru/vacancies"
payload = {"HH-User-Agent": "dvmn_salary", "professional_role": "96", "area": "1"}
response = requests.get(base_api_url, params=payload)
total_vacancies = response.json().get("found")
print("Total developer vacancies in Moscow: {}".format(total_vacancies))

payload["period"] = "30"
response = requests.get(base_api_url, params=payload)
total_vacancies = response.json().get("found")
print("Total developer vacancies in Moscow last month: {}".format(total_vacancies))
