import pandas as pd
import datetime
from tinkoff.invest.schemas import CandleInterval
from tkinter.ttk import *
from tkinter import *
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import *
from CONSTANTC import GIGA

import warnings

warnings.filterwarnings("ignore")


def download_history_target(token: str, days: int) -> pd.DataFrame:

    # Создаем прогрессбар для загрузки исторических данных.
    tk = Tk()
    tk.title("Загрузка исторических данных")
    tk.attributes('-toolwindow', True)
    progress = Progressbar(tk, orient=HORIZONTAL, maximum=days, value=0, length=500, mode='determinate')
    progress.grid(column=1, row=0)

    # Фиксируем текущую дату.
    st = datetime.datetime.utcnow()
    st = datetime.datetime(st.date().year, st.date().month, st.date().day, 0, 0, 0, 0)

    # Создаем первичный датафрейм. К нему потом подсоединим остальные данные.
    firsty_data = pd.DataFrame(data={'time': [datetime.datetime(year=2000, month=1, day=1, hour=1, minute=1, second=1)],
                                     'closing_data': [-199]})

    with RetryingClient(token=token, settings=RetryClientSettings()) as client:
        for day in range(1, days):

            # Если дата выпадает на выходной день или на январские праздники, то такой день пропускается. Так как в этот день не ведутся торги.
            if (st - datetime.timedelta(days=day)).isoweekday() > 5 or (
                    (st - datetime.timedelta(days=day - 1)).month == 1 and 1 < (
                    st - datetime.timedelta(days=day - 1)).day <= 8):
                progress['value'] = progress['value'] + 1
                tk.update()
                print(st - datetime.timedelta(days=days))
                continue

            # Обновляем прогресс бар.
            progress['value'] = progress['value'] + 1
            tk.update()

            # Делаем запрос данных за день.
            candleses = client.market_data.get_candles(
                figi=client.instruments.find_instrument(query="Тинькофф вечный портфель RUB").instruments[0].figi,
                from_=st - datetime.timedelta(days=day),
                to=st - datetime.timedelta(days=day - 1),
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN)

            # Создаем список с данными цен закрытия.
            clossing_data = [x.close.units + x.close.nano / GIGA for x in candleses.candles]

            # Формируем список времен.
            time_data = [x.time for x in candleses.candles]

            # Формируем таблицу с датой, временем и ценами закрытия сделок.
            data = pd.DataFrame(data={'time': time_data,
                                      'closing_data': clossing_data})

            # Создаем маленький датафрейм на один день с датой и временем и минутным интервалом. 
            times = pd.DataFrame(
                pd.date_range(start=st - datetime.timedelta(days=day), end=st - datetime.timedelta(days=day - 1),
                              freq="T", tz="UTC"), columns=["time"])

            # Присоединяем данные о сделках к маленькому датафрейму.
            times = pd.merge(times, data, how="outer", on="time")

            # Присоединяем полученные данные к предыдущим полученным данным.
            firsty_data = (pd.concat([firsty_data, times], axis=0)).reset_index(drop=True)

            print(day)

    # Заполняем пропуски.
    firsty_data=firsty_data.fillna(method='ffill').fillna(method='backfill')

    firsty_data=firsty_data[firsty_data['closing_data'] > 0]

    # Сортируем датафрейм и восстанавливаем индексы.
    firsty_data = firsty_data.sort_values(by='time', ascending=True)
    firsty_data = firsty_data.reset_index(drop=True)

    # Убираем первый час значений и восстанавливаем индексы.
    firsty_data = firsty_data.drop(index=range(60))
    firsty_data = firsty_data.reset_index(drop=True)

    # Создаем большой датафрейм с датами и временем со сдвигом на час вперед относительно зафиксированного времени.
    # Присоединяем датафрейм к нашему прошлому датафрейму.
    # Это делаем мы, для того чтобы сдвинуть значения таргетов относительно признаков на час вперед.
    # Таким образом мы можем предсказывать значения будущих таргетов по прошлым значениям признаков, в данном случае по прошлым стоимостям его активов: акций, облигаций, валют.
    timez = pd.DataFrame(
        data={'time': pd.date_range(start=st, end=st + datetime.timedelta(hours=1), freq="T", tz="UTC").to_list(),
              'closing_data': -1})
    firsty_data = (pd.concat([firsty_data, timez], axis=0)).reset_index(drop=True)

    # Убираем прогресс бар.
    progress.pack()
    tk.destroy()

    firsty_data=firsty_data[firsty_data['closing_data'] > 0]

    # Сортируем датафрейм по датам.
    firsty_data = firsty_data.sort_values(by='time', ascending=True)

    # Переводим колонку в нужный тип данных.
    firsty_data['time'] = pd.to_datetime(firsty_data['time'])

    return firsty_data
