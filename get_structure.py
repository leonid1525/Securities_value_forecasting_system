import requests

# Функция выполнения запроса текущей структуры фонда
def get_structure(ticker : str) -> dict:
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Accept-Language': 'ru',
        'Sec-Fetch-Mode': 'cors',
        'Host': 'www.tinkoff.ru',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
    }

    params = {
        'appName': 'invest',
        'appVersion': '1.312.0',
        'origin': 'web',
        'platform': 'web',
        'idKind': 'ticker',
    }

    response = requests.get(
        f'https://www.tinkoff.ru/api/invest-gw/fireg-advisory/api/web/v2/etf/assets/{ticker}/structure',
        params=params,

        headers=headers,
    )
    if response.status_code == 200:
        data = response.json()
    return data