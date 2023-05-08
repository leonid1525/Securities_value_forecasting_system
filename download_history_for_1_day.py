import pandas as pd
import datetime
from tinkoff.invest.schemas import CandleInterval
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import *
from CONSTANTC import GIGA


# Данная функция загружает исторические данные за 1 день.
def download_history_for_1_day(st: datetime.datetime, day: int, token: str, structure):

    # Создаем столбик из даты и времени с интервалом в 1 минуту.
    times = pd.DataFrame(pd.date_range(start=st - datetime.timedelta(days=1), end=st, freq="T", tz="UTC"),
                         columns=["time"])

    # Создаем список для хранения figi. FIGI - (англ.: Financial Instrument Global Identifier) — глобальный идентификатор финансового инструмента. 
    # Представляет собой 12-символьный код из латинских букв и цифр, определяется как идентификатор ценной бумаги на торговой площадке (бирже), 
    # которая является некоторым "источником цен".
    list_figi = []

    for y in range(10):
        with RetryingClient(token=token, settings=RetryClientSettings()) as client:

            # Проверяем и заменяем типы ценных бумаг, так как в библиотеке tinkoff.invest немного по другому пишутся типы ценных бумаг.
            if structure[y]['type'] == 'Stock':
                structure[y]['type'] = 'share'
            elif structure[y]['type'] == 'Currency':
                structure[y]['type'] = 'currency'
            elif structure[y]['type'] == 'Bond':
                structure[y]['type'] = 'bond'

            # Выполняем поиск того что нужно среди всех инструментов по тикерам.
            c = client.instruments.find_instrument(query=structure[y]['ticker'])

            # Итерируемся по найденным инструментам, и проверяем на соответствие того что есть в БПИФ на самом деле.
            for x in range(len(c.instruments)):
                if c.instruments[x].instrument_type == structure[y]['type'] and c.instruments[x].name == structure[y][
                    'name'] and \
                        c.instruments[x].class_code != 'SMAL':

                    # Загружаем общие данные по инструменту.
                    first_data = client.market_data.get_candles(figi=c.instruments[x].figi,
                                                                from_=st - datetime.timedelta(days=day),
                                                                to=st - datetime.timedelta(days=day - 1),
                                                                interval=CandleInterval.CANDLE_INTERVAL_1_MIN)

                    # Формируем список значений цен значений.
                    clossing_data = [x.close.units + x.close.nano / GIGA for x in first_data.candles]

                    # Формируем список времен.
                    time_data = [x.time for x in first_data.candles]

                    # Формируем таблицу.
                    data = pd.DataFrame(data={'time': time_data,
                                              f'{c.instruments[x].figi}': clossing_data})

                    # Едем дальше если таблица пуста.
                    if data.shape[0] == 0:
                        continue

                    # Округляем время в таблице на всякий случай и присоединяем таблицу с временем и ценами к общей таблице с временами.
                    else:
                        data['time'] = data["time"].dt.round("T")
                        times = pd.merge(times, data, how="outer", on="time")

                        # Сохраняем figi.
                        list_figi.append(c.instruments[x].figi)
                        break

    with RetryingClient(token=token, settings=RetryClientSettings()) as client:

        fund_figi = client.instruments.find_instrument(query='Тинькофф Вечный портфель RUB').instruments[0].figi

        # Загружаем общие данные по инструменту.
        data_closing_invest_fund = client.market_data.get_candles(figi=fund_figi,
                                                                  from_=st - datetime.timedelta(days=day),
                                                                  to=st - datetime.timedelta(days=day - 1),
                                                                  interval=CandleInterval.CANDLE_INTERVAL_1_MIN)

        # Формируем список значений цен значений.
        clossing_data_invest_fund = [x.close.units + x.close.nano / GIGA for x in data_closing_invest_fund.candles]

        # Формируем список времен.
        time_data_invest_fund = [x.time for x in data_closing_invest_fund.candles]

        # Формируем таблицу.
        data = pd.DataFrame(data={'time': time_data_invest_fund,
                                  fund_figi: clossing_data_invest_fund})

        data['time'] = pd.to_datetime(data['time'])
        data['time'] = data["time"].dt.round("T")
        times = pd.merge(times, data, how="outer", on="time")

        list_figi.append(fund_figi)

    return times, list_figi
