import sys
from tkinter import *
import webbrowser
import pandas as pd

from token_verification import token_ver
from download_history import download_history_data
from download_history_target import download_history_target
from get_structure import get_structure


# Функция получения токена у пользователя и проверки его на корректность.
def get_token():
    # Функция открытия ссылки в браузере
    def callback(url):
        webbrowser.open_new(url)

    # функция получения токена и числа дней истории в виде текста, для последующей аутентификации.
    def input_data():
        global token
        global days
        token = txt0.get()
        days = txt1.get()
        wnd.destroy()

    # Создаем окно с текстом и кнопками для приема токена
    wnd = Tk()
    wnd.title("Securities_value_forecasting_system")
    wnd.attributes('-toolwindow', True)
    wnd.geometry("1400x400")

    lbl0 = Label(wnd, text='Для использования данной системы вам необходимо быть клиентом "Тинькофф банк"',
                 font=("Times New Roman", 14))
    lbl0.place(x=100, y=100)

    lbl1 = Label(wnd, text='Перед использованием системы пожалуйста получите токен согласно инструкции',
                 font=("Times New Roman", 14))
    lbl1.place(x=100, y=125)

    lbl2 = Label(wnd, text='https://tinkoff.github.io/investAPI/token/', font=("Times New Roman", 14),
                 foreground="blue")
    lbl2.place(x=770, y=125)
    lbl2.bind("<Button-1>", lambda e: callback("https://tinkoff.github.io/investAPI/token/"))

    lbl3 = Label(wnd, text='Введите ваш токен ниже', font=("Times New Roman", 14))
    lbl3.place(x=100, y=175)

    txt0 = Entry(wnd, width=130, font=("Times New Roman", 14))
    txt0.place(x=100, y=200)

    btn1 = Button(wnd, text='OK', font=("Times New Roman", 14), command=input_data, justify="center", width=40,
                  height=1)
    btn1.place(x=500, y=350)

    lbl4 = Label(wnd,
                 text='Введите целое число дней истории ниже',
                 font=("Times New Roman", 14))
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
        wnd_error.attributes('-toolwindow', True)
        wnd_error.geometry("270x100")
        lbl_error = Label(wnd_error, text='Введенный токен неисправен', font=("Times New Roman", 14))
        lbl_error.place(x=10, y=10)
        btn_error = Button(wnd_error, text="OK", font=("Times New Roman", 10), command=wnd_error.destroy, width=10,
                           justify="center")
        btn_error.place(x=90, y=50)
        sys.exit()

    return token, days


# Функция получения и сохранения актуальных данных.
def get_data(token, days):
    structure = get_structure('TRUR')['items']

    # Загружаем данные.
    history_feature = download_history_data(token, days, structure)

    # Загружаем таргеты для исторических данных.
    history_target = download_history_target(token, days)

    # Соединяем данные, чтобы они полностью сходились по датам и размерам.
    data = pd.merge(history_feature, history_target, on='time', how='inner')

    data.to_csv('safe_data.csv', index=False)

    return data
