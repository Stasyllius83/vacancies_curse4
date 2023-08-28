import requests
from exceptions import ParsingError


def get_currencies():
    response = requests.get("https://www.cbr.ru/scripts/XML_daily.asp")
    try:
        if response.status_code != 200:
            raise ParsingError(f"Ошибка получения курса валют! Статус: {response.status_code}")
        currencies = parse(response.content)
        formatted_currencies = {}
        for currency in currencies["ValCurs"]["Valute"]:
            value = float(currency["Value"].replace(",", "."))
            nominal = float(currency["Nominal"])
        formatted_currencies["RUR"] = 1
        return formatted_currencies
    except ParsingError as error:
        print(error)
        return {
            "AUD": 52.2056,
            "AZN": 47.0495,
            "GBP": 98.9163,
            "AMD": 0.206998,
            "BYN": 27.3216,
            "BGN": 44.0805,
            "BRL": 16.1679,
            "HUF": 0.229615,
            "VND": 0.00337543,
            "HKD": 10.2295,
            "GEL": 30.907,
            "DKK": 11.5825,
            "AED": 21.7816,
            "USD": 79.9841,
            "EUR": 85.8767,
            "EGP": 2.58902,
            "INR": 0.9697589999999999,
            "IDR": 0.005366259999999999,
            "KZT": 0.1799660000000001,
            "CAD": 58.8898,
            "QAR": 21.9737,
            "KGS": 0.913165,
            "CNY": 11.2816,
            "MDL": 4.50744,
            "NZD": 48.7103,
            "NOK": 7.29355999999999,
            "PLN": 19.028,
            "RON": 17.3156,
            "RUR": 1,
            "XDR": 106.6212,
            "SGD": 59.1423,
            "TJS": 7.32865000000000006,
            "THB": 2.3065,
            "TRY": 4.02377,
            "TMT": 22.8526,
            "UZS": 0.00700509,
            "UAH": 2.3065,
            "CZK": 3.6442500000000004,
            "SEK": 7.47599,
            "CHF": 88.3022,
            "RSD": 0.732326,
            "ZAR": 4.1435699999999995,
            "KRW": 0.0603198,
            "JPY": 0.573692
        }