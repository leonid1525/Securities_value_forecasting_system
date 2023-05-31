import pandas as pd
import datetime
from download_history_for_1_day import download_history_for_1_day
from tkinter.ttk import *
from tkinter import *

import warnings

warnings.filterwarnings("ignore")


# Функция загрузки исторических данных, для обучения модели
def download_history_data(token: str, days: int, structure):
    # Создаем прогресс бар.
    tk = Tk()
    tk.title("Загрузка исторических данных и заполнение пропусков")
    progress = Progressbar(tk, orient=HORIZONTAL, maximum=days, value=0, length=500, mode='determinate')
    progress.grid(column=1, row=0)

    # Записываем текущее время и дату, после чего округляем до даты
    st = datetime.datetime.utcnow()
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
                                     '9': [-199],
                                     'close_invest_fund': [-199]})

    # Создаем список дней и разворачиваем его.
    rang = list(range(1, days))
    rang = reversed(rang)

    count = days

    # По каждому дню в году собираем данные и присоединяем к таблице.
    for day in rang:

        # Если дата выпадает на выходной день или на январские праздники, то такой день пропускается. Так как в этот день не ведутся торги.
        if (st - datetime.timedelta(days=day)).isoweekday() > 5 or (
                (st - datetime.timedelta(days=day - 1)).month == 1 and 1 < (
                st - datetime.timedelta(days=day - 1)).day < 8):
            progress['value'] = progress['value'] + 1
            tk.update()
            print(st - datetime.timedelta(days=day))
            continue

        # Обновляем прогресс бар.
        progress['value'] = progress['value'] + 1
        tk.update()

        # Загружаем данные по каждому дню и присоединяем их.
        new_day, list_figi = download_history_for_1_day(st=st, day=day, token=token, structure=structure)

        if count == days:
            firsty_data = firsty_data.rename(columns={'0': list_figi[0],
                                                      '1': list_figi[1],
                                                      '2': list_figi[2],
                                                      '3': list_figi[3],
                                                      '4': list_figi[4],
                                                      '5': list_figi[5],
                                                      '6': list_figi[6],
                                                      '7': list_figi[7],
                                                      '8': list_figi[8],
                                                      '9': list_figi[9],
                                                      'close_invest_fund': list_figi[10]})

        count = count - 1

        # Заполняем пропуски.
        new_day=new_day.fillna(method='ffill').fillna(method='backfill')

        # Присоединяем к предыдущим дням, заполненный текущий день.
        firsty_data = (pd.concat([firsty_data, new_day], axis=0)).reset_index(drop=True)

        print(day)

    # Удаляем первое значение, так как оно остается от первичного датафрейма и является аномальным.
    firsty_data.drop(index=0, inplace=True)
    firsty_data = firsty_data.reset_index(drop=True)

    # Убираем прогресс бар.
    progress.pack()
    tk.destroy()

    # Меняем тип данных у колонки со временем и датой. Сортируем по времени и дате. Удаляем дубликаты колонке с временем. Удаляем, на всякий случай, оставшиеся пропуски.
    firsty_data['time'] = pd.to_datetime(firsty_data['time'])
    firsty_data = firsty_data.sort_values(by='time', ascending=True)
    firsty_data = firsty_data.reset_index(drop=True)
    firsty_data = firsty_data.drop_duplicates(subset=['time'], keep='last')
    firsty_data = firsty_data.dropna(axis=0, how='any')
    print(firsty_data)
    print(firsty_data.isna().sum())

    return firsty_data
