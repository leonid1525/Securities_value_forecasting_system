import pandas as pd
import datetime
from tinkoff.invest import *
from tinkoff.invest.schemas import CandleInterval
import time
from tkinter.ttk import *
from tkinter import *

import warnings

warnings.filterwarnings("ignore")


def download_history_target(token: str, days: int) -> pd.DataFrame:
    # Создаем прогрессбар для загрузки исторических данных.
    tk = Tk()
    tk.title("Загрузка исторических данных")
    progress = Progressbar(tk, orient=HORIZONTAL, maximum=days, value=0, length=500, mode='determinate')
    progress.grid(column=1, row=0)

    # Фиксиеруем текущую дату.
    st = datetime.datetime.now()
    st = datetime.datetime(st.date().year, st.date().month, st.date().day, 0, 0, 0, 0)

    # Создаем первичный датафрейм. К нему потом подсоединим остальные данные.
    firsty_data = pd.DataFrame(data={'time': [datetime.datetime(year=2000, month=1, day=1, hour=1, minute=1, second=1)],
                                     'closing_data': [-199]})

    with Client(token) as client:
        for day in range(1, days):

            # Обновляем прогрессбар.
            progress['value'] = progress['value'] + 1
            tk.update()

            # Делаем остановку, в загрузке, чтобы следовать лимитной политике.
            if day % 190 == 0:
                time.sleep(60)

            # Делаем запрос данных за день.
            candleses = client.market_data.get_candles(
                figi=client.instruments.find_instrument(query="Тинькофф вечный портфель RUB").instruments[0].figi,
                from_=st - datetime.timedelta(days=day),
                to=st - datetime.timedelta(days=day - 1),
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN)

            # Создаем список с данными цен закрытия.
            clossing_data = [x.close.units + x.close.nano / 1000000000 for x in candleses.candles]

            # Формируем список времен.
            time_data = [x.time for x in candleses.candles]

            # Формируем таблицу с датой, временем и ценами закрытия сделок.
            data = pd.DataFrame(data={'time': time_data,
                                      'closing_data': clossing_data})

            # Создаем маленький датафрейм на один день с датой и временем и минутным интервалом. 
            times = pd.DataFrame(
                pd.date_range(start=st - datetime.timedelta(days=day), end=st - datetime.timedelta(days=day - 1),
                              freq="T", tz="UTC"), columns=["time"])

            # Присоеднияем данные о сделках к маленькому датафрейму.
            times = pd.merge(times, data, how="outer", on="time")

            # Присоединяем полученные данные к предыдущим полученным данным.
            firsty_data = (pd.concat([firsty_data, times], axis=0)).reset_index(drop=True)

            print(day)

    # Заполняем пропуски аномальным значением, чтобы потом особым способом поменять аномальные значения на нужные.
    firsty_data.fillna(-1, inplace=True)

    # Убираем строку из первичного датафрейма. Там значение -199.
    firsty_data = firsty_data[firsty_data['closing_data'] > -2]

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

    # Создаем прогрессбар заполнения пропусков.
    tk1 = Tk()
    tk1.title("Заполнение пропусков в исторических данных таргетах")
    progress1 = Progressbar(tk1, orient=HORIZONTAL, maximum=firsty_data.shape[0], value=0, length=500,
                            mode='determinate')
    progress1.grid(column=1, row=0)

    # Итерируемся по строкам.
    for minute in range(firsty_data.shape[0]):

        # Обновляем прогрессбар
        progress1['value'] = progress1['value'] + 1
        tk1.update()

        # Для первой строки, если она заполнена аномальным значением -1, берем первое нормальное значение.
        if firsty_data.loc[minute, 'closing_data'] == -1 and minute == 0:
            first_value = (firsty_data.loc[firsty_data['closing_data'] > -1, 'closing_data']).reset_index(drop=True)
            firsty_data.loc[minute, 'closing_data'] = first_value[0]
            continue

        # Для последующих аномальных значений, берем значение выше.
        if firsty_data.loc[minute, 'closing_data'] == -1:
            firsty_data.loc[minute, 'closing_data'] = firsty_data.loc[minute - 1, 'closing_data']

    # Сортируем датафрейм по датам.
    firsty_data = firsty_data.sort_values(by='time', ascending=True)

    # Убираем прогрессбар.
    progress.pack()
    tk.destroy()

    return firsty_data
