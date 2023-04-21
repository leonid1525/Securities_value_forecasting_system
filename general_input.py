import sys
from tkinter import *
import webbrowser
import datetime
import pandas as pd

from token_verification import token_ver
from filling_in_the_gaps import filling_in_the_gaps
from download_history_target import download_history_target
from learn_model import learn_model

import warnings

warnings.filterwarnings("ignore")


# Функция открытия ссылки в браузере
def callback(url):
    webbrowser.open_new(url)


# функция получения токена в виде текста, для последующей аутентификации
def input_data():
    global token
    global days
    token = txt0.get()
    days = txt1.get()
    days = int(days)
    wnd.destroy()


# Проверяем текущее время. Если в данный момент не работает московская биржа, то работа приложения не будет продолжена.
now = datetime.datetime.now()
if ((now.hour < 9 or now.hour >= 18) and now.isoweekday() < 5) or (
        now.isoweekday() == 5 and now.time() > datetime.time(16, 45, 0, 0)):
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

# Создаем окно с текстом и кнопками для приема токена
wnd = Tk()
wnd.title("Securities_value_forecasting_system")
wnd.geometry("1400x400")

lbl0 = Label(wnd, text='Для использования данной системы вам необходимо быть клиентом "Тинькофф банк"',
             font=("Times New Roman", 14))
lbl0.place(x=100, y=100)

lbl1 = Label(wnd, text='Перед использованием системы пожалуйста получите токен согласно инструкции',
             font=("Times New Roman", 14))
lbl1.place(x=100, y=125)

lbl2 = Label(wnd, text='https://tinkoff.github.io/investAPI/token/', font=("Times New Roman", 14), foreground="blue")
lbl2.place(x=770, y=125)
lbl2.bind("<Button-1>", lambda e: callback("https://tinkoff.github.io/investAPI/token/"))

lbl3 = Label(wnd, text='Введите ваш токен ниже', font=("Times New Roman", 14))
lbl3.place(x=100, y=175)

txt0 = Entry(wnd, width=130, font=("Times New Roman", 14))
txt0.place(x=100, y=200)

btn1 = Button(wnd, text='OK', font=("Times New Roman", 14), command=input_data, justify="center", width=40, height=1)
btn1.place(x=500, y=350)

lbl4 = Label(wnd, text='Введите целое число дней истории ниже', font=("Times New Roman", 14))
lbl4.place(x=100, y=250)

txt1 = Entry(wnd, width=50, font=("Times New Roman", 14))
txt1.place(x=100, y=300)

wnd.mainloop()

# Проверяем токен, вызывая с помощью него некоторые данные. Если токен неисправен появится соответствующая ошибка.
try:
    token_ver(token)
except:
    wnd_error = Tk()
    wnd_error.title("Неисправный токен")
    wnd_error.geometry("270x100")
    lbl_error = Label(wnd_error, text='Введенный токен неисправен', font=("Times New Roman", 14))
    lbl_error.place(x=10, y=10)
    btn_error = Button(wnd_error, text="OK", font=("Times New Roman", 10), command=wnd_error.destroy, width=10,
                       justify="center")
    btn_error.place(x=90, y=50)

# Загружаем данные.
history_feature = filling_in_the_gaps(token, days)

# Загружаем таргеты для исторических данных.
history_target = download_history_target(token, days)

# Соединяем данные, чтобы они полностью сходились по датам и размерам.
data = pd.merge(history_feature, history_target, on='time', how='inner')

# Создаем отдельную выборку из признаков.
X = data.drop(['closing_data'], axis=1)

# Переводим колонку time в тип данных datetime.
X['time'] = pd.to_datetime(X['time'])

# Создаем новые признаки из времени.
X['minute'] = X['time'].dt.minute
X['hour'] = X['time'].dt.hour
X['day_of_week'] = X['time'].dt.day_of_week

# Удаляем время из признаков.
X=X.drop(['time'], axis=1)

# Выборка таргетов отдельно.
Y = data['closing_data']

model=learn_model(X, Y)