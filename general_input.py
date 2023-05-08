import sys
from tkinter import *
import datetime
import pandas as pd
import warnings
import os

from learn_model import learn_model
from get_data import *
from predict import predict

warnings.filterwarnings("ignore")

# Проверяем текущее время. Если в данный момент не работает московская биржа, то появится соответствующее окно и работа приложения не будет продолжена.
now = datetime.datetime.now()
if (now.hour < 9 and now.minute < 50) or (now.hour >= 23 and now.minute >= 58):
    wnd_closing = Tk()
    wnd_closing.title("Биржа закрыта в данное время")
    wnd_closing.geometry("280x100")
    lbl_closing = Label(wnd_closing, text='Биржа закрыта в данное время.', font=("Times New Roman", 14))
    lbl_closing.place(x=10, y=10)
    btn_closing = Button(wnd_closing, text="OK", font=("Times New Roman", 10), command=wnd_closing.destroy, width=10,
                         justify="center")
    btn_closing.place(x=100, y=50)
    wnd_closing.mainloop()
    sys.exit()

# Получаем токен.
token, days = get_token()

# Проверяем переменную, так как необязательно указывать число дней, если данные уже были загружены сегодня.
if days.isdigit():
    days = int(days)

# Проверяем наличие файла с загруженными файлами.
if os.path.isfile('safe_data.csv'):

    # Читаем файл, чтобы потом проверить его на корректность и актуальность.
    data = pd.read_csv('safe_data.csv', index_col=False)

    # Проверяем чтобы первым столбцом шло время и дата.
    if data.columns[0] == 'time':

        # Проверяем чтобы последняя дата и время были вчера.
        data['time'] = pd.to_datetime(data['time'])
        data = data.sort_values(by='time', ascending=True)
        tail_date = datetime.datetime.now().date()
        print(tail_date)
        if data.loc[data.shape[0] - 1, 'time'] != tail_date:
            # Если дата и время более старые чем нужно, то загружаем актуальные данные.
            data = get_data(token, days)
    else:

        # Если файл некорректный, то загружаем актуальные данные.
        data = get_data(token, days)

else:

    # Если файла нет, то загружаем актуальные данные.
    data = get_data(token, days)

print(data)

# Создаем отдельную выборку из признаков.
x = data.drop(['closing_data'], axis=1)

# Переводим колонку time в тип данных datetime.
x['time'] = pd.to_datetime(x['time'])

# Создаем новые признаки из времени.
x['minute'] = x['time'].dt.minute
x['hour'] = x['time'].dt.hour
x['day_of_week'] = x['time'].dt.day_of_week

# Удаляем время из признаков.
x = x.drop(['time'], axis=1)

# Выборка таргетов отдельно.
y = data['closing_data']

# Обучаем и валидируем модель.
model = learn_model(x, y)

predict(model, token, x)
