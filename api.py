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


def predict_rub_salary(vacancy):
    salary = vacancy["salary"]
    print(salary)
    if salary is None:
        return "No salary data"
    else:
        if salary["from"] is None and salary["to"] is None:
            return None
        elif salary["from"] is None:
            avg_salary = salary["to"] * 0.8
            return avg_salary
        elif salary["to"] is None:
            avg_salary = salary["from"] * 1.2
            return avg_salary
        else:
            avg_salary = (salary["from"] + salary["to"]) / 2
            return avg_salary


vacancy_role = "Программист Python"
filtered_vacancies = get_vacancies(vacancy_role)

for vacancy in filtered_vacancies["items"]:
    print(predict_rub_salary(vacancy))
