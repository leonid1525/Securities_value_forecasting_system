import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, median_absolute_error, max_error
import pandas as pd
import datetime


# Функция отрисовки графика. Читает записи в файлах, после чего рисует график.
def visual(predict: list, times: list, real: list):
    # Рисуем график.
    plt.figure(num=1, figsize=(16, 9), clear=True)
    plt.plot(times, predict, label="Прогноз")
    plt.plot(times[0:len(real)], real, label="Реальные цены")
    plt.xlabel('Время, с точностью до минуты', loc='center')
    plt.ylabel('Закрывающие цены акций фонда')
    plt.xticks(rotation=80)
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    plt.title(
        f'График прогнозируемой и реальной закрывающих цен на час вперед.\n Максимальное отклонение - {round(max_error(pd.Series(real), pd.Series(predict[0:len(real)])), 4)}, среднее отклонение - {round(mean_absolute_error(pd.Series(real), pd.Series(predict[0:len(real)])), 4)}, медианное отклонение - {round(median_absolute_error(pd.Series(real), pd.Series(predict[0:len(real)])), 4)}')
    plt.ion()
    plt.show()
    plt.legend()

    # После паузы вечный цикл в функции predict начинается заново.
    plt.pause(59)
