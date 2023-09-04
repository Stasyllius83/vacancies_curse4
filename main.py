from classes import HeadHunter, SuperJob, Connector


def main():
    vacancies_json = []
    keyword = input("Введите ключевое слово для поиска: ")

    sj = SuperJob(keyword)
    hh = HeadHunter(keyword)
    for api in (hh, sj):
        api.get_vacancies(pages_count=10)
        vacancies_json.extend(api.get_formatted_vacancies())
    connector = Connector(keyword=keyword)
    connector.insert(vacancies_json=vacancies_json)

    while True:
        command = input(
            "1 - Вывести список вакансий; \n"
            "2 - Отсортировать по минимальной зарплате; \n"
            "exit - для выхода. \n"
        )
        if command.lower() == "exit":
            break
        elif command == "1":
            vacancies = connector.select()
        elif command == "2":
            vacancies = api.sort_by_salary_from()

        for vacancy in vacancies:
            print(vacancy, end='\n')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
