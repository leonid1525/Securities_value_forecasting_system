import pandas as pd
import datetime
import time
from download_history_for_1_day import download_history_for_1_day
from tkinter.ttk import *
from tkinter import *

import warnings

warnings.filterwarnings("ignore")


# Функция загрузки исторических данных, для обучения модели
def download_history_data(token: str, days: int):
    # Создаем прогрессбар.
    tk = Tk()
    tk.title("Загрузка исторических данных")
    progress = Progressbar(tk, orient=HORIZONTAL, maximum=days, value=0, length=500, mode='determinate')
    progress.grid(column=1, row=0)

    # Записываем текущее время и дату, после чего округляем до даты
    st = datetime.datetime.now()
    st = datetime.datetime(st.date().year, st.date().month, st.date().day, 0, 0, 0, 0)

    # Создаем первичный датафрейм, к нему потом будем в цикле присоединять данные по дням. 
    # Ограничение таково, что в одном запросе при максимальной точности в 1 минуту, можно загружать только 1 день.
    firsty_data = pd.DataFrame(data={'time': [datetime.datetime(year=2000, month=1, day=1, hour=1, minute=1, second=1)],
                                     '0': [-199],
                                     '1': [-199],
                                     '2': [-199],
                                     '3': [-199],
                                     '4': [-199],
                                     '5': [-199],
                                     '6': [-199],
                                     '7': [-199],
                                     '8': [-199],
                                     '9': [-199]})

    # По каждому дню в году собираем данные и присоединяем к таблице.
    for x in range(1, days):

        # Обновляем прогрессбар.
        progress['value'] = progress['value'] + 1
        tk.update()

        # При каждом 25 дне, делаем минутный перерыв, в связи с лимитной политикой запросов.
        if x % 20 == 0:
            time.sleep(60)

        # Загружаем данные по каждому дню и присоединяем их.
        new_day = download_history_for_1_day(st=st, day=x, token=token)
        firsty_data = (pd.concat([firsty_data, new_day], axis=0)).reset_index(drop=True)
        print(x)

    # Убираем прогрессбар.
    progress.pack()
    tk.destroy()

    return firsty_data
