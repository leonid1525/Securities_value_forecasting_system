import pandas as pd
import datetime
from tinkoff.invest import *
from tinkoff.invest.schemas import CandleInterval
from get_structure import get_structure

def download_history_for_1_day(st:datetime.datetime, day:int, token:str) -> pd.DataFrame:

    times=pd.DataFrame(pd.date_range(start=st-datetime.timedelta(days=1), end=st, freq="T", tz="UTC"), columns=["time"])
    for y in range(10):
        with Client(token) as client:
            m=get_structure('TRUR')['items'][y]
            if m['type']=='Stock':
                m['type']='share'
            elif m['type']=='Currency':
                m['type']='currency'
            elif m['type']=='Bond':
                m['type']='bond'
            c=client.instruments.find_instrument(query=m['ticker'])
            for x in range(len(c.instruments)):
                if c.instruments[x].instrument_type==m['type'] and c.instruments[x].name==m['name'] and c.instruments[x].class_code!='SMAL':
                    first_data = client.market_data.get_candles(figi=c.instruments[x].figi, from_=st-datetime.timedelta(days=day), to=st-datetime.timedelta(days=day-1), interval=CandleInterval.CANDLE_INTERVAL_1_MIN)
                    clossing_data=[x.close.units+x.close.nano/1000000000 for x in first_data.candles]
                    time_data=[x.time for x in first_data.candles]
                    data=pd.DataFrame(data={'time':time_data,
                                                f'{y}':clossing_data})
                    if data.shape[0]==0:
                        continue
                    else:
                        data['time']=data["time"].dt.round("T")
                        times=pd.merge(times, data, how="outer", on="time")
                        break
    return times
