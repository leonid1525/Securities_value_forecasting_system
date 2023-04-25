import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, median_absolute_error, max_error
from hyperopt import *
import tkinter
from tkinter.ttk import *


# Функция подбора параметров и обучения модели случайного леса
def learn_model(X: pd.DataFrame, Y: pd.DataFrame):
    # Функция получение порога ошибки и типа ошибки.
    def input_loss():
        global thr_loss
        global error_name
        thr_loss = txt0.get()
        thr_loss = float(thr_loss)
        error_name = combobox.get()
        window_input_loss.destroy()

    # Делаем окно с текстовым полем, текстом и кнопкой для получения порога ошибки и типа ошибки.
    window_input_loss = tkinter.Tk()
    window_input_loss.title("Введите порог ошибки и выберите валидационную ошибку.")
    window_input_loss.attributes('-toolwindow', True)
    window_input_loss.geometry("500x250")

    lbl0 = Label(window_input_loss, text='Введите порог ошибки ниже',
                 font=("Times New Roman", 14))
    lbl0.place(x=10, y=10)

    errors = ['Среднее абсолютное отклонение', 'Медианное абсолютное отклонение', 'Максимальное абсолютное отклонение']
    combobox = Combobox(window_input_loss, values=errors, width=50, font=("Times New Roman", 14))
    combobox.place(x=10, y=100)

    txt0 = Entry(window_input_loss, width=50, font=("Times New Roman", 14))
    txt0.place(x=10, y=50)

    btn0 = tkinter.Button(window_input_loss, text='OK', font=("Times New Roman", 14), command=input_loss,
                          justify="center", width=40, height=1)
    btn0.place(x=10, y=150)
    window_input_loss.mainloop()

    # Делим загруженные данные на обучающие и тестовые.
    X_train = X.head(X.shape[0] - 60 * 24 * 7)
    Y_train = Y.head(Y.shape[0] - 60 * 24 * 7)
    X_test = X.tail(60 * 24 * 7)
    Y_test = Y.tail(60 * 24 * 7)

    # Определяем признаковое пространство.
    params = {
        'n_estimators': hp.randint("n_estimators", 1, 1000),
        'criterion': hp.choice('criterion', options=['squared_error', 'friedman_mse', 'absolute_error', 'poisson']),
        'max_depth': hp.randint("max_depth", 1, 10000),
        'max_features': hp.choice('max_features', options=['auto', 'sqrt', 'log2'])}

    # Функция обучения модели и записи данных.
    def objective(params):

        # Определяем случайный лес со случайными параметрами.
        pipeline = RandomForestRegressor(**params, random_state=2023)

        # Обучаем модель со случайными параметрами.
        pipeline.fit(X_train, Y_train)

        # Проверяем какой тип ошибки выбрал пользователь и считаем соответствующую ошибку для записи в хранилище результатов.
        if error_name == 'Среднее абсолютное отклонение':
            loss = mean_absolute_error(Y_test, pipeline.predict(X_test))
        elif error_name == 'Медианное абсолютное отклонение':
            loss = median_absolute_error(Y_test, pipeline.predict(X_test))
        elif error_name == 'Максимальное абсолютное отклонение':
            loss = max_error(Y_test, pipeline.predict(X_test))

        print(params)
        print(f'max_error {max_error(Y_test, pipeline.predict(X_test))}')
        print(f'mean_absolute_error {mean_absolute_error(Y_test, pipeline.predict(X_test))}')
        print(f'median_absolute_error {median_absolute_error(Y_test, pipeline.predict(X_test))}')
        print(
            '-----------------------------------------------------------------------------------------------------------')

        # Возвращаем ошибку и соответствующие параметры для записи в хранилище результатов.
        return {'loss': loss, 'params': params, 'status': STATUS_OK}

    # Хранилище результатов. На основании данных в хранилище определяется вектор в изучении пространства признаков. Неперспективные места просто не изучаются.
    trials = Trials()
    best = fmin(

        # Указываем нашу кастомную функцию обучения модели и записи данных.
        fn=objective,

        # Указываем изучаемое признаковое пространство.
        space=params,

        # Указываем алгоритм изучения признакового пространства.
        algo=tpe.suggest,

        # Указываем пороговое значение отклонения. При достижении отклонения ниже этого порога прекратится поиск.
        loss_threshold=thr_loss,

        # Указываем хранилище результатов.
        trials=trials,

        # Показываем прогресс бар.
        show_progressbar=True
    )

    print(trials.best_trial['result']['params'])

    # Обучаем модель с лучшими параметрами.
    model = RandomForestRegressor(**trials.best_trial['result']['params'])
    model.fit(X, Y)

    return model
