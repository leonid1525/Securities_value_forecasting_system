import pandas as pd
import datetime
from tinkoff.invest import *
import time
from download_history_for_1_day import download_history_for_1_day


# Функция загрузки исторических данных, для обучения модели
def load_history_data(token):

    # Записываем текущее время и дату, после чего округляем до даты
    st=datetime.datetime.now()
    st=datetime.datetime(st.date().year, st.date().month, st.date().day, 0, 0, 0, 0)

    # Создаем первичный датафрейм, к нему потом будем в цикле присоединять данные по дням. Ограничение таково, что в одном запросе при максимальной точности в 1 минуту, можно загружать только 1 день.
    firsty_data=pd.DataFrame(data={'time':[datetime.datetime(year=2000, month=1, day=1, hour=1, minute=1, second=1)], 
                                    '0':[0], 
                                    '1':[0], 
                                    '2':[0], 
                                    '3':[0], 
                                    '4':[0], 
                                    '5':[0], 
                                    '6':[0], 
                                    '7':[0],
                                    '8':[0],
                                    '9':[0]})
    # print(get_structure('TRUR')['items'])
    for x in range(1, 366):
        new_day=download_history_for_1_day(st=st, day=x, token=token)
        firsty_data=(firsty_data.append(new_day)).reset_index(drop=True)
        print(firsty_data)
    return firsty_data

