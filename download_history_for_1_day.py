import pandas as pd
import datetime
from tinkoff.invest import *
from tinkoff.invest.schemas import CandleInterval
from get_structure import get_structure
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import *


# Данная функция загружает исторические данные за 1 день.
def download_history_for_1_day(st: datetime.datetime, day: int, token: str) -> pd.DataFrame:
    # Создаем столбик из даты и времени с интервалом в 1 минуту.
    times = pd.DataFrame(pd.date_range(start=st - datetime.timedelta(days=1), end=st, freq="T", tz="UTC"),
                         columns=["time"])

    # Делаем запрос на текущую структуру фонда.
    structure = get_structure('TRUR')['items']

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
                    clossing_data = [x.close.units + x.close.nano / 1000000000 for x in first_data.candles]

                    # Формируем список времен.
                    time_data = [x.time for x in first_data.candles]

                    # Формируем таблицу.
                    data = pd.DataFrame(data={'time': time_data,
                                              f'{y}': clossing_data})

                    # Едем дальше если таблица пуста.
                    if data.shape[0] == 0:
                        continue

                    # Округляем время в таблице на всякий случай и присоединяем таблицу с временем и ценами к общей таблице с временами.
                    else:
                        data['time'] = data["time"].dt.round("T")
                        times = pd.merge(times, data, how="outer", on="time")
                        break
    return times
