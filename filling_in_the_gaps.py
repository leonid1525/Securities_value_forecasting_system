from download_history import download_history_data

from tkinter.ttk import *
from tkinter import *

import warnings

warnings.filterwarnings("ignore")


# Поскольку хранятся данные только сделок, и большинство сделок происходит в самое разное время - при сборе всего этого в 1 таблицу, появляется много пропусков.
# Данная функция заполняет пропуски особым образом. Пропуска до первого значения в колонке заполняются первым значением.
# Пропуска после любого значения в колонке заполняются этим значением.
def filling_in_the_gaps(token, days: int):
    # Получаем данные.
    history_data = download_history_data(token, days)

    # Удаляем первую строку.
    history_data.drop(index=0, inplace=True)

    # Восстанавливаем индексы.
    history_data = history_data.reset_index(drop=True)

    # Сортируем датафрейм по датам, от старых к новым.
    history_data = history_data.sort_values(by='time', ascending=True)

    # Восстанавливаем индексы.
    history_data = history_data.reset_index(drop=True)

    # Заполняем все пропуска отрицательным значением.
    history_data.fillna(-1, inplace=True)

    # Делаем список колонок, по которым будем итерироваться.
    column = history_data.columns.to_list()
    del column[0]

    # Создаем прогрессбар заполнение пропусков.
    tk = Tk()
    tk.title("Заполнение пропусков в исторических данных")
    progress = Progressbar(tk, orient=HORIZONTAL, maximum=len(column) * history_data.shape[0], value=0, length=500,
                           mode='determinate')
    progress.grid(column=1, row=0)

    # Итерируемся по каждой ячейке, заполняя пропуски.
    for x in column:
        for y in range(0, history_data.shape[0]):
            progress['value'] = progress['value'] + 1
            tk.update()

            if y == 0 and history_data.loc[y, x] == -1:
                first_value = (history_data.loc[history_data[x] > -1, x]).reset_index(drop=True)
                history_data.loc[y, x] = first_value[0]
                print(x, y)
                continue
            if history_data.loc[y, x] == -1:
                history_data.loc[y, x] = history_data.loc[y - 1, x]

    return history_data
