from abc import abstractmethod, ABC

from utils import get_currencies
from exceptions import ParsingError
import json
import requests


class Engine(ABC):
    """
    Абстрактный класс для работы с методами get_request, get_vacancies
    """

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HeadHunter(Engine):
    """
    Класс для создания экземпляров классов вакансий с данными из HeadHunter
    """

    def __init__(self, keyword, page=0):
        self.url = "https://api.hh.ru/vacancies"
        self.params = {
            "per_page": 100,
            "page": page,
            "text": keyword,
            "archive": False,
            "only_with_salary": True
        }
        self.vacancies = []

    def get_request(self):
        """
        Функция для получения данных по url
        :return: Возвращает данные в формате json по ключу items
        """
        response = requests.get(self.url, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус: {response.status_code}")
        return response.json()["items"]

    def get_formatted_vacancies(self):
        """
        Функция форматирования данных в общий вид
        :return: Вовращает список
        """
        formatted_vacancies = []
        for vacancy in self.vacancies:
            formatted_vacancy = {
                "employer": vacancy["employer"]["name"],
                "title": vacancy["name"],
                "url": vacancy["url"],
                "api": "HeadHunter",
                "salary_from": vacancy["salary"]["from"] if vacancy["salary"] else None,
                "salary_to": vacancy["salary"]["to"] if vacancy["salary"] else None,
                "currency": vacancy["salary"]["currency"] if vacancy["salary"] else None,
                "rate": None,
            }
            if formatted_vacancy["currency"] != "RUR":
                rate = get_currencies(formatted_vacancy["currency"])
                formatted_vacancy["rate"] = rate

            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        """
        Функция для получения вакансий
        :param pages_count: счетчик страниц
        :return:
        """
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

    def sort_by_salary_from(self):
        """
        Функция сортировки вакансий по зарплате
        :return:
        """
        data = self.get_formatted_vacancies()
        sort_vacancies = sorted(data, key=lambda x: x["salary_from"], reverse=False)
        return sort_vacancies


class SuperJob(Engine):
    """
    Класс для создания экземпляров классов вакансий с данными из SuperJob
    """
    url = "https://api.superjob.ru/2.0/vacancies/"

    def __init__(self, keyword, page=0):
        self.params = {
            "count": 100,
            "page": page,
            "keyword": keyword,
            "archive": False,
            "no_agreement": 1
        }
        self.headers = {
            "X-Api-App-Id": "v3.r.137769082.9ebd46ae49865b587c70ff0a30ef47dac5f8857e.72919bdbe2cad8aa6b8d16a8c9b09f4731248454"
        }
        self.vacancies = []

    def get_request(self):
        """
        Функция для получения данных по url
        :return: Возвращает данные в формате json по ключу objects
        """
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения вакансий! Статус: {response.status_code}")
        return response.json()["objects"]

    def get_formatted_vacancies(self):
        """
        Функция форматирования данных в общий вид
        :return: Вовращает список
        """
        formatted_vacancies = []
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
                "currency": vacancy["currency"]
            }

            formatted_vacancies.append(formatted_vacancy)

        return formatted_vacancies

    def get_vacancies(self, pages_count=2):
        """
        Функция для получения вакансий
        :param pages_count: счетчик страниц:
        :return:
        """
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

    def sort_by_salary_from(self):
        """
        Функция сортировки вакансий по зарплате
        :return:
        """
        data = self.get_formatted_vacancies()
        sort_vacancies = sorted(data, key=lambda x: x["salary_from"], reverse=False)
        return sort_vacancies


class Vacancy:
    """
    Класс для работы с вакансиями
    """

    def __init__(self, vacancy):
        self.employer = vacancy["employer"]
        self.title = vacancy["title"]
        self.url = vacancy["url"]
        self.api = vacancy["api"]
        self.salary_from = vacancy["salary_from"]
        self.salary_to = vacancy["salary_to"]
        self.currency = vacancy["currency"]
        # self.currency_valve = vacancy["currency_valve"]

    def __str__(self):
        if not self.salary_from and not self.salary_to:
            salary = "Не указана"
        else:
            salary_from, salary_to = "", ""
            salary = " ".join([salary_from, salary_to]).strip()
        return f"""
    Работодатель: \"{self.employer}\"
    Вакансия: \"{self.title}\"
    Зарплата: {salary}
    Ссылка: {self.url}
        """

    def __repr__(self):
        return f"""
        Vacancy(title={self.title}, salary_from={self.salary_from}, salary_to={self.salary_to},
        employer={self.employer},url={self.url})
        """

    def __lt__(self, other):
        if self.salary_from is None:
            self_salary_from = 0
        else:
            self_salary_from = self.salary_from

        if other.salary_from is None:
            other_salary_from = 0
        else:
            other_salary_from = other.salary_from

        if self_salary_from != other_salary_from:
            return self_salary_from < other_salary_from
        else:
            if self.salary_to is None:
                self_salary_to = float('inf')
            else:
                self_salary_to = self.salary_to

            if other.salary_to is None:
                other_salary_to = float('inf')
            else:
                other_salary_to = other.salary_to

                return self_salary_to < other_salary_to

    def __eq__(self, other):
        return (self.salary_from, self.salary_to) == (other.salary_from, other.salary_to)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


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
