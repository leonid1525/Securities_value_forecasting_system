from download_load_history import download_history_data

# Поскольку хранятся данные только сделок, и большинство сделок происходит в самое разное время - при сборе всего этого в 1 таблицу, появляется много пропусков.
# Данная функция заполняет пропуски особым образом. Пропуска до первого значения в колонке заполняются первым значением.
# Пропуска после любого значения в колонке заполняются этим значением.
def filling_in_the_gaps(token):

    # Получаем данные.
    history_data=download_history_data(token)

    # Удаляем первую строку.
    history_data.drop(index=0, inplace=True)

    # Заполняем все пропуска отрицательным значением.
    history_data.fillna(-1, inplace=True)

    # Делаем список колонок, по которым будем итерироваться.
    column=history_data.columns.to_list()
    del column[0]

    # Итерируемся по каждой ячейке.
    for x in column:
        for y in range(1, history_data.shape[0]+1):
            if y==1 and history_data.loc[y, x]==-1:
                first_value=(history_data.loc[history_data[x]>-1, x]).reset_index(drop=True)
                history_data.loc[y, x]=first_value[0]
                print(x, y)
                continue
            if history_data.loc[y, x]==-1:
                history_data.loc[y, x]=history_data.loc[y-1, x]

    return history_data
