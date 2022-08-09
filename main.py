from itertools import count

import requests
from environs import Env
from terminaltables import AsciiTable


def get_vacancies_hh(role) -> list:
    base_api_url = "https://api.hh.ru/vacancies"
    vacancies = []
    max_pages = 19
    area_id = 1                                 # Moscow
    for page in count(0):
        payload = {
            "HH-User-Agent": "dvmn_salary",
            "area": area_id,
            "text": role,
            "per_page": "100",
            "page": page}
        response = requests.get(base_api_url, params=payload)
        response.raise_for_status()
        vacancies_page = response.json()
        for vacancy in vacancies_page["items"]:
            vacancies.append(vacancy)
        if page == max_pages or page >= vacancies_page["pages"]:
            break
    return vacancies


def get_vacancies_sj(key, language) -> list:
    superjob_api_url = "https://api.superjob.ru/2.0/vacancies/"
    vacancies = []
    headers = {"X-Api-App-Id": key}
    max_pages = 5
    profession_id = 48                          # "Programming and development"
    town_id = 4                                 # Moscow
    for page in count(0):
        payload = {
            "catalogues": profession_id,
            "town": town_id,
            "keyword": language,
            "count": "100",
            "page": page}
        response = requests.get(superjob_api_url, headers=headers, params=payload)
        response.raise_for_status()
        all_vacancies = response.json()
        for vacancy in all_vacancies["objects"]:
            vacancies.append(vacancy)
        if page == max_pages or not all_vacancies["more"]:
            break
    return vacancies


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    elif not salary_from:
        avg_salary = salary_to * 0.8
        return avg_salary
    elif not salary_to:
        avg_salary = salary_from * 1.2
        return avg_salary
    else:
        avg_salary = (salary_from + salary_to) / 2
        return avg_salary


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if salary and salary["currency"] == "RUR":
        salary_from = salary["from"]
        salary_to = salary["to"]
        return predict_salary(salary_from, salary_to)


def predict_rub_salary_sj(vacancy):
    if vacancy["currency"] == "rub":
        salary_from = vacancy["payment_from"] if vacancy["payment_from"] else None
        salary_to = vacancy["payment_to"] if vacancy["payment_to"] else None
        return predict_salary(salary_from, salary_to)


def vacancy_statistic_hh(languages):
    salaries_statistic = {}
    for language in languages:
        role = "Программист {}".format(language)
        salaries = []
        vacancies = get_vacancies_hh(role)
        total_vacancies = len(vacancies)
        for vacancy in vacancies:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
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


def vacancy_statistic_sj(key, languages):
    salaries_statistic = {}
    for language in languages:
        salaries = []
        vacancies = get_vacancies_sj(key, language)
        total_vacancies = len(vacancies)
        for vacancy in vacancies:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
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


def process_statistic(fetched_statistic, title):
    column_headers = ["Язык программирования", "Вакансий найдено",
                      "Вакансий обработано", "Средняя зарплата"]
    processed_statistic = [column_headers]
    for language, stats in fetched_statistic.items():
        statistic = [language]
        statistic.extend(stats.values())
        processed_statistic.append(statistic)
    table_instance = AsciiTable(processed_statistic, title)
    return table_instance.table


def main():
    env = Env()
    env.read_env()
    superjob_secret_key = env.str("SUPERJOB_KEY")
    languages = ["JavaScript", "Java", "Python", "Ruby", "PHP", "C++", "C#", "C", "Go"]
    print("Downloading SuperJob vacancies...")
    collected_sj_statistic = vacancy_statistic_sj(superjob_secret_key, languages)
    print("Downloading HeadHunter vacancies...")
    collected_hh_statistic = vacancy_statistic_hh(languages)
    print(process_statistic(collected_sj_statistic, "SuperJob Moscow"))
    print(process_statistic(collected_hh_statistic, "HeadHunter Moscow"))


if __name__ == "__main__":
    main()
