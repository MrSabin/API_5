import requests
from itertools import count
from environs import Env
from terminaltables import AsciiTable


def get_vacancies_count(role):
    base_api_url = "https://api.hh.ru/vacancies"
    payload = {"HH-User-Agent": "dvmn_salary", "area": "1", "text": role}
    response = requests.get(base_api_url, params=payload)
    total_vacancies = response.json().get("found")
    return total_vacancies


def get_vacancies_hh(role):
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


def predict_salary(salary_from, salary_to):
    if salary_from is None and salary_to is None:
        return None
    elif salary_from is None:
        avg_salary = salary_to * 0.8
        return avg_salary
    elif salary_to is None:
        avg_salary = salary_from * 1.2
        return avg_salary
    else:
        avg_salary = (salary_from + salary_to) / 2
        return avg_salary


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if salary is None or salary["currency"] != "RUR":
        return None
    else:
        salary_from = salary["from"]
        salary_to = salary["to"]
        return predict_salary(salary_from, salary_to)


def vacancy_statistic_hh(languages):
    salaries_statistic = {}
    for language in languages:
        role = "Программист {}".format(language)
        total_vacancies = get_vacancies_count(role)
        salaries = []
        vacancies = get_vacancies_hh(role)
        for vacancy in vacancies:
            salary = predict_rub_salary_hh(vacancy)
            if salary is not None:
                salaries.append(salary)
        avg_salary = sum(salaries) / len(salaries)
        processed_vacancies = len(salaries)
        total_information = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": processed_vacancies,
            "average_salary": int(avg_salary)
        }
        salaries_statistic[language] = total_information
    return salaries_statistic


def predict_rub_salary_sj(vacancy):
    if vacancy["currency"] != "rub":
        return None
    else:
        salary_from = vacancy["payment_from"] if vacancy["payment_from"] != 0 else None
        salary_to = vacancy["payment_to"] if vacancy["payment_to"] != 0 else None
        return predict_salary(salary_from, salary_to)


def get_vacancies_sj(key, language):
    superjob_api_url = "https://api.superjob.ru/2.0/vacancies/"
    vacancies = []
    headers = {"X-Api-App-Id": key}
    for page in count(0):
        payload = {"catalogues": "48", "town": "4", "keyword": language, "count": "100", "page": page}
        response = requests.get(superjob_api_url, headers=headers, params=payload)
        response.raise_for_status()
        all_vacancies = response.json()
        for vacancy in all_vacancies["objects"]:
            vacancies.append(vacancy)
        if page == 5 or not all_vacancies["more"]:
            break
    return vacancies


def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_KEY")
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]
    for language in languages:
        get_vacancies_sj(superjob_secret_key, language)


if __name__ == "__main__":
    main()