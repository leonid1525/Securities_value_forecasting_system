import pandas as pd
import datetime
from tinkoff.invest import *
import time
from download_history_for_1_day import download_history_for_1_day

# Функция загрузки исторических данных, для обучения модели
def download_history_data(token):

    # Записываем текущее время и дату, после чего округляем до даты
    st=datetime.datetime.now()
    st=datetime.datetime(st.date().year, st.date().month, st.date().day, 0, 0, 0, 0)

    # Создаем первичный датафрейм, к нему потом будем в цикле присоединять данные по дням. 
    # Ограничение таково, что в одном запросе при максимальной точности в 1 минуту, можно загружать только 1 день.
    firsty_data=pd.DataFrame(data={'time':[datetime.datetime(year=2000, month=1, day=1, hour=1, minute=1, second=1)], 
                                    '0':[-199], 
                                    '1':[-199], 
                                    '2':[-199], 
                                    '3':[-199], 
                                    '4':[-199], 
                                    '5':[-199], 
                                    '6':[-199], 
                                    '7':[-199],
                                    '8':[-199],
                                    '9':[-199]})

    
    # По каждому дню в году собираем данные и присоединяем к таблице.
    for x in range(1, 366):

        # При каждом 25 дне, делаем минутный перерыв, в связи с лимитной политикой запросов.
        if x%25==0:
            time.sleep(60)

        new_day=download_history_for_1_day(st=st, day=x, token=token)
        firsty_data=(pd.concat([firsty_data, new_day], axis=0)).reset_index(drop=True)
        print(x)
        
    return firsty_data