from tinkoff.invest import Client

# Функция запроса данных. Используется только для проверки токена.
def token_ver():
    with Client(token) as client:
        r = client.instruments.find_instrument(query="Тинькофф Вечный портфель RUB")