import time
import datetime
import re
# from pandas import to_datetime
from dateutil.parser import parse as dateparse
from typing import Dict, List, Optional, Tuple, Union


DATEHOURFORMAT = "%Y%m%d%H%M%S"
DATEFORMAT = "%Y%m%d"


def get_time(s):
    return time.time()


def get_time_ms(s):
    return int(time.time() * 1000)


def get_bar(bar='15m', direction=-1):
    now = time.localtime(time.time())
    return


def ts_to_hour(timestamp: Union[int, float], fmt=Optional[str]) -> str:
    """convert timestamp to str in date-hour format"""
    if fmt is None:
        fmt = DATEHOURFORMAT
    return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)


def ts_to_str(timestamp: Union[int, float], fmt=Optional[str]) -> str:
    """convert timestamp to str in date format"""
    if fmt is None:
        fmt = DATEFORMAT
    return datetime.datetime.fromtimestamp(timestamp).strftime(fmt)


def random_sleep(min_secs=90, max_secs=300) -> None:
    """sleep in random seconds"""
    hour = datetime.datetime.now().hour
    if hour in range(9):
        time.sleep(max_secs)
    else:
        time.sleep(min_secs)


def today_str(fmt=Optional[str]):
    """return today date in str"""
    if fmt is None:
        fmt = DATEFORMAT
    return datetime.datetime.today().strftime(fmt)


def shift_date(start, periods, fmt="%Y-%m-%d", include=True):
    if include:
        periods -= 1
    dt = datetime.datetime.strptime(start, fmt)
    out_date = (dt + datetime.timedelta(days=periods))
    return out_date.strftime(fmt)


def format_datetime(raw_time=None):
    if not raw_time:
        print("输入时间，转化为标准时间戳")
        print("Version1")
    # 1. 常用的都用pandas.to_datetime解决
    if isinstance(raw_time, int):
        raw_time = str(raw_time)
    # dt = to_datetime(raw_time).timestamp()
    dt = dateparse(raw_time).timestamp()
    # 2.to_datetime无效的格式
    #  'yyyymm'会被解释为'ddmmyy'， 例如to_datetime('201211')->2011-12-20 00:00:00
    return dt


def str_to_timestamp(date_str: str, fmt=Optional[str]) -> float:
    """convert from str to timestamp"""
    if fmt is None:
        fmt = DATEFORMAT
    return datetime.datetime.strptime(date_str, fmt).timestamp()


# def str_to_ts(dt, fmt="%Y-%m-%d"):
#     return datetime.datetime.strptime(dt, fmt).timestamp()
# def timedelta_to_ts(td, fmt="%H:%M"):


def trans_time_wb(txt):
    if '来自' in txt:
        txt = re.findall("^(.*?)来自", txt)  # 有些是  04月05日 10:35 来自来自浙江
    txt = txt.strip()
    today = datetime.datetime.today()
    year = today.year
    now = time.time()
    if '前' in txt:
        # xx分钟前 xx秒前
        freq_dict = {'分钟': 60, '秒': 1, '秒钟': 1}
        freq = re.findall(f'({"|".join(freq_dict.keys())})前', txt)[0]
        length = int(re.findall('(\d+)', txt)[0])
        secs = freq_dict[freq] * length
        new_time = now - secs
    elif '刚刚' in txt:
        new_time = now
    elif '今天' in txt:
        # 今天 xxx
        txt = txt.replace('今天', today.strftime('%Y-%m-%d'))
        new_time = datetime.datetime.strptime(txt, '%Y-%m-%d %H:%M').timestamp()
    elif '月' in txt:
        # 1月30日 18:01
        new_time = datetime.datetime.strptime(f'{year}年' + txt, '%Y年%m月%d日 %H:%M').timestamp()
    else:
        new_time = datetime.datetime.strptime(txt, '%Y-%m-%d %H:%M:%S').timestamp()
    return new_time


if __name__ == '__main__':
    print(format_datetime('201211'))
