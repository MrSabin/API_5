import requests


def get_vacancies_count(role):
    base_api_url = "https://api.hh.ru/vacancies"
    payload = {"HH-User-Agent": "dvmn_salary", "area": "1", "text": role}
    response = requests.get(base_api_url, params=payload)
    total_vacancies = response.json().get("found")
    return total_vacancies


def get_vacancies(role):
    base_api_url = "https://api.hh.ru/vacancies"
    payload = {"HH-User-Agent": "dvmn_salary", "area": "1", "text": role}
    response = requests.get(base_api_url, params=payload)
    vacancies = response.json()
    return vacancies


def vacancy_by_language():
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]
    search_result = {}
    for language in languages:
        role = "Программист {}".format(language)
        vacancies_count = get_vacancies_count(role)
        search_result[language] = vacancies_count
    print(search_result)


vacancy_role = "Программист Python"
filtered_vacancies = get_vacancies(vacancy_role)

for vacancy in filtered_vacancies["items"]:
    print(vacancy["salary"])