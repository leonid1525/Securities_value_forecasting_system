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
    # Создаем прогресс бар.
    tk = Tk()
    tk.title("Загрузка исторических данных и заполнение пропусков")
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

    # Создаем список дней и разворачиваем его.
    rang = range(1, days)
    rang = reversed(rang)

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
        new_day = download_history_for_1_day(st=st, day=day, token=token)

        # Заполняем пропуски нулями.
        new_day.fillna(-1, inplace=True)

        # Делаем список колонок и удаляем оттуда время и дату.
        column = new_day.columns.to_list()
        del column[0]

        # Итерируемся по ячейкам, заполняя пропуски особым образом.
        for x in column:
            for y in range(0, new_day.shape[0]):
                if y == 0 and new_day.loc[y, x] == -1:

                    # Для первой строки с пропуском, залезаем в предыдущий день, и берем последнее значение столбика с таким же названием.
                    # Проверяем на нормальность, так как при заполнении пропусков в первый день (он загружается первым), из предыдущего дня покажется аномальное значение.
                    # Если значение оказалось аномальным, то берем первое нормальное непустое значение из датафрейма, в котором заполняем пропуски. 
                    tail_value = firsty_data.tail(1)
                    tail_value = tail_value.reset_index(drop=True)
                    if tail_value.loc[0, x] == -199:
                        first_value = (new_day.loc[new_day[x] > -1, x]).reset_index(drop=True)
                        new_day.loc[y, x] = first_value[0]
                    else:
                        new_day.loc[y, x] = tail_value.loc[0, x]
                    continue
                if new_day.loc[y, x] == -1:
                    new_day.loc[y, x] = new_day.loc[y - 1, x]

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
