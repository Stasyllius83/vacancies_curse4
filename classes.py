from abc import abstractmethod, ABC

from utils import get_currencies
from exceptions import ParsingError
import json
import requests


class Engine(ABC):
    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunter(Engine):

    def __init__(self, keyword, page=0):
        self.url = "https://api.hh.ru/vacancies"
        self.params = {
            "per_page": 100,
            "page": page,
            "text": keyword,
            "archive": False,
        }
        self.vacancies = []

    def get_request(self):
        response = requests.get(self.url, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус: {response.status_code}")
        return response.json()["items"]

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        # currencies = get_currencies()
        sj_currencies = {
            "rub": "RUR",
            "uah": "UAH",
            "uzs": "UZS",
        }

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["employer"],
                "title": vacancy["name"],
                "url": vacancy["url"],
                "api": "HeadHunter",
                "salary_from": vacancy["salary"] if vacancy["salary"] and vacancy["salary"] != 0 else None,
                "salary_to": vacancy["salary"] if vacancy["salary"] and vacancy["salary"] != 0 else None,
            }

            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        self.vacancies = []  # Очищаем список вакансий
        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f"({self.__class__.__name__}) Парсинг страницы {page} -", end=" ")
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}")
            if len(page_vacancies) == 0:
                break


class SuperJob(Engine):
    url = "https://api.superjob.ru/2.0/vacancies/"

    def __init__(self, keyword, page=0):
        self.params = {
            "count": 100,
            "page": page,
            "keyword": keyword,
            "archive": False,
        }
        self.headers = {
            "X-Api-App-Id": "v3.r.137769082.9ebd46ae49865b587c70ff0a30ef47dac5f8857e.72919bdbe2cad8aa6b8d16a8c9b09f4731248454"
        }
        self.vacancies = []

    def get_request(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус: {response.status_code}")
        return response.json()["objects"]

    def get_formatted_vacancies(self):
        formatted_vacancies = []
        # currencies = get_currencies()
        sj_currencies = {
            "rub": "RUR",
            "uah": "UAH",
            "uzs": "UZS",
        }

        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["firm_name"],
                "title": vacancy["profession"],
                "url": vacancy["link"],
                "api": "SuperJob",
                "salary_from": vacancy["payment_from"] if vacancy["payment_from"] and vacancy[
                    "payment_from"] != 0 else None,
                "salary_to": vacancy["payment_to"] if vacancy["payment_to"] and vacancy["payment_to"] != 0 else None,
            }

            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        self.vacancies = []  # Очищаем список вакансий
        for page in range(pages_count):
            page_vacancies = []
            self.params["page"] = page
            print(f"({self.__class__.__name__}) Парсинг страницы {page} -", end=" ")
            try:
                page_vacancies = self.get_request()
            except ParsingError as error:
                print(error)
            else:
                self.vacancies.extend(page_vacancies)
                print(f"Загружено вакансий: {len(page_vacancies)}")
            if len(page_vacancies) == 0:
                break


class Vacancy:
    def __init__(self, vacancy):
        self.employer = vacancy["employer"]
        self.title = vacancy["title"]
        self.url = vacancy["url"]
        self.api = vacancy["api"]
        self.salary_from = vacancy["salary_from"]
        self.salary_to = vacancy["salary_to"]
        # self.currency = vacancy["currency"]
        # self.currency_valve = vacancy["currency_valve"]

    def __str__(self):
        if not self.salary_from and not self.salary_to:
            salary = "Не указана"
        else:
            salary_from, salary_to = "", ""
            # if self.salary_from:
            #    salary_from = f"от {self.salary_from} {self.currency}"
            #    if self.currency != "RUR":
            #        salary_from += f" ({round(self.salary_from * self.currency_valve, 2)} RUR)"
            # if self.salary_to:
            #    salary_to = f"до {self.salary_to} {self.currency}"
            #    if self.currency != "RUR":
            #        salary_to += f" ({round(self.salary_to * self.currency_valve, 2)} RUR)"
            salary = " ".join([salary_from, salary_to]).strip()
        return f"""
    Работодатель: \"{self.employer}\"
    Вакансия: \"{self.title}\"
    Зарплата: {salary}
    Ссылка: {self.url}
        """


class Connector:
    def __init__(self, keyword):
        self.filename = f"{keyword.title()}.json"

    def insert(self, vacancies_json):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(vacancies_json, file, indent=4)

    def select(self):
        with open(self.filename, "r", encoding="utf-8") as file:
            vacancies = json.load(file)
        return [Vacancy(x) for x in vacancies]
