import requests
from itertools import count
from environs import Env


def get_vacancies_count(role):
    base_api_url = "https://api.hh.ru/vacancies"
    payload = {"HH-User-Agent": "dvmn_salary", "area": "1", "text": role}
    response = requests.get(base_api_url, params=payload)
    total_vacancies = response.json().get("found")
    return total_vacancies


def get_vacancies(role):
    base_api_url = "https://api.hh.ru/vacancies"
    vacancies = []
    for page in count(0):
        print("Downloading page {} of role {}".format(page, role))
        payload = {"HH-User-Agent": "dvmn_salary", "area": "1", "text": role, "per_page": "100", "page": page}
        response = requests.get(base_api_url, params=payload)
        vacancies_page = response.json()
        for vacancy in vacancies_page["items"]:
            vacancies.append(vacancy)
        if page == 19 or page >= vacancies_page["pages"]:
            break
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
    if salary is None or salary["currency"] != "RUR":
        return None
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


def average_salary_by_language():
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]
    salary_info = {}
    for language in languages:
        role = "Программист {}".format(language)
        total_vacancies = get_vacancies_count(role)
        salaries = []
        vacancies = get_vacancies(role)
        for vacancy in vacancies:
            salary = predict_rub_salary(vacancy)
            if salary is not None:
                salaries.append(salary)
        avg_salary = sum(salaries) / len(salaries)
        processed_vacancies = len(salaries)
        total_information = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": processed_vacancies,
            "average_salary": int(avg_salary)
        }
        salary_info[language] = total_information
    print(salary_info)


env = Env()
env.read_env()
superjob_secret_key = env.str("SUPERJOB_KEY")
superjob_api_url = "https://api.superjob.ru/2.0/vacancies/"
headers = {"X-Api-App-Id": superjob_secret_key}
payload = {}
response = requests.get(superjob_api_url, headers=headers, params=payload)
response.raise_for_status()
all_vacancies = response.json()
for vacancy in all_vacancies["objects"]:
    print(vacancy["profession"])