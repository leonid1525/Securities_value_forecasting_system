import datetime
import pandas as pd
# from tinkoff.invest import *
from tinkoff.invest.schemas import CandleInterval, InstrumentClosePriceRequest
from tinkoff.invest.retrying.sync.client import RetryingClient
from tinkoff.invest.retrying.settings import *
from time import sleep
from visual import visual
from CONSTANTC import GIGA


# Функция, которая прогнозирует цены сначала на час вперед, потом делает запрос каждую минуту и по полученным данным делает прогноз закрывающей цены через час.
# Также, каждую минуту запрашивает закрывающую цену последней минуты фонда, по которым делаются прогнозы.
# Все полученные данные сохраняет в текстовые файлы. Чтобы потом функция визуализации прочитала файлы.
def predict(model, token: str, x: pd.DataFrame):

    # Создаем список колонок. Удаляем колонки, которые не имеют отношения к фондам. В названиях колонок записаны номера FIGI.
    # Подробнее про FIGI вот тут: https://tinkoff.github.io/investAPI/faq_instruments/.
    col = x.columns.to_list()
    col.remove('minute')
    col.remove('hour')
    col.remove('day_of_week')

    # Выравниваем время начала работы функции.
    now = datetime.datetime.now()
    if now.second != 0:
        sleep(60 - now.second)

    # Фиксируем текущее время по UTC, с точностью до минуты.
    utc_now = datetime.datetime.utcnow()
    utc_now_round_minute = datetime.datetime(year=utc_now.year, month=utc_now.month, day=utc_now.day, hour=utc_now.hour,
                                             minute=utc_now.minute,
                                             second=0)

    # Создаем датафрейм с колонкой времени, чтобы потом к ней присоединить данные свечей.
    time = pd.DataFrame(
        data={'time': pd.date_range(start=utc_now - datetime.timedelta(days=1), end=utc_now, freq='T', tz="UTC")})

    # Запрашиваем данные за последний день.
    # Не за последний час, потому что биржа может только открылась, а программа уже запущена.
    with RetryingClient(token=token, settings=RetryClientSettings()) as client:
        for figi in col:
            data = client.market_data.get_candles(figi=figi,
                                                  from_=utc_now_round_minute - datetime.timedelta(days=1),
                                                  to=utc_now_round_minute,
                                                  interval=CandleInterval.CANDLE_INTERVAL_1_MIN)

            # Формируем список значений цен значений.
            clossing_data = [x.close.units + x.close.nano / GIGA for x in data.candles]

            # Формируем список времен.
            time_data = [x.time for x in data.candles]

            # Формируем таблицу.
            data = pd.DataFrame(data={'time': time_data,
                                      f'{figi}': clossing_data})

            data["time"] = pd.to_datetime(data["time"], utc=True)
            data['time'] = data["time"].dt.round("T")
            time = pd.merge(time, data, how="outer", on="time")
            print(figi)

    # Заполняем пропуски аномальным значением.
    time.fillna(-1, inplace=True)

    # Меняем аномальные значения на нормальные. 
    # Первые аномальные значения в колонках меняем на первые нормальные значения.
    for figi in col:
        for y in range(time.shape[0]):
            if y == 0 and time.loc[y, figi] == -1:
                first_value = (time.loc[time[figi] > -1, figi]).reset_index(drop=True)
                time.loc[y, figi] = first_value[0]
                continue

            # Меняем последующие аномальные значения на предыдущие нормальные значения.
            if time.loc[y, figi] == -1:
                time.loc[y, figi] = time.loc[y - 1, figi]

    # Создаем новые признаки из времени.
    time['minute'] = time['time'].dt.minute
    time['hour'] = time['time'].dt.hour
    time['day_of_week'] = time['time'].dt.day_of_week

    # Отбираем последний час данных.
    time = time[time['time'] > pd.to_datetime(utc_now_round_minute - datetime.timedelta(hours=1), utc=True)]

    # Удаляем время из признаков.
    time = time.drop(['time'], axis=1)

    print(time)

    # Делаем предсказания на следующий час.
    predicted = model.predict(time)

    # Делаем датафрейм, с датой и временем с точностью до минуты.
    now = datetime.datetime.now()
    now_round_minute = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute,
                                         second=0)
    next_hour = pd.DataFrame(data={'hours': pd.date_range(start=now_round_minute,
                                                          end=now_round_minute + datetime.timedelta(
                                                              hours=1),
                                                          freq='T')})

    # Переводим все массивы в списки для визуализации.
    times = next_hour['hours'].to_list()
    predicted = predicted.tolist()
    list_real = []

    # Преобразуем datetime в str.
    for elem in range(len(times)):
        times[elem] = times[elem].strftime('%H:%M')

    # Делаем запрос на получение FIGI фонда.
    with RetryingClient(token=token, settings=RetryClientSettings()) as client:
        figi = client.instruments.find_instrument(query='Тинькофф Вечный портфель RUB').instruments[0].figi

    # Создаем вечный цикл.
    while True:
        # Открываем файлы для дозаписи.
        with RetryingClient(token=token, settings=RetryClientSettings()) as client:
            # Печатаем FIGI для осведомленности об активности процесса.
            print(figi)

            # Получаем реальное значение закрывающей цены.
            request = client.market_data.get_close_prices(
                instruments=[InstrumentClosePriceRequest(instrument_id=figi)]).close_prices[0].price
            real = request.units + request.nano / GIGA

            last_data = {}

            # Записываем последние цены в виде класса в словарь, после чего из класса достаем значения его атрибутов и превращаем их в float.
            for col in time.columns:
                last_data[col] = client.market_data.get_close_prices(
                    instruments=[InstrumentClosePriceRequest(instrument_id=col)]).close_prices[0].price
                last_data[col] = last_data[col].units + last_data[col].nano / GIGA

            # Получаем признаки из текущего времени.
            last_data['minute'] = datetime.datetime.utcnow().minute
            last_data['hour'] = datetime.datetime.utcnow().hour
            last_data['day_of_week'] = datetime.datetime.utcnow().isoweekday()

            # Преобразуем словарь в датафрейм.
            last_data = pd.DataFrame(data=last_data, index=[0])

            # Делаем прогноз на основе данных.
            pred = model.predict(last_data)

            # Округляем прогноз и превращаем в строку.
            pred = round(float(pred), 4)

            # Получаем значение времени и даты, через час.
            now = datetime.datetime.now()
            now_round_minute = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour,
                                                 minute=now.minute, second=0)
            next_round_minute = (now_round_minute + datetime.timedelta(hours=1)).strftime('%H:%M')

            # Добавляем в списки полученные значения.
            predicted.append(pred)
            times.append(next_round_minute)
            list_real.append(real)

            # Вызываем функцию отрисовки графика.
            visual(predicted, times, list_real)
