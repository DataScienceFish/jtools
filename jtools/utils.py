import os
from datetime import datetime, timedelta
from typing import *
import pandas as pd

from . import consts as C


SH_STARTDATE, SH_ENDDATE = '19901219', '20991231'


def _wind_code2inst_id(wind_codes: List[str]) -> List[str]:
    """转换：wind_code（三位交易所代码）转inst_id（二位交易所代码）"""
    inst_ids = {}
    for wind_code in wind_codes:
        inst_name, wexchg_id = wind_code.split('.')
        exchg_id = C.MAP_WEXCHG_XTEXCHG.get(wexchg_id, wexchg_id)
        # TODO: inst_name有时候会有差异，例如M01M.DCE和m01.DF，wind_code需要删除多余的M
        inst_id = '.'.join([inst_name, exchg_id])
        # wind_codes.append()
        inst_ids[wind_code] = inst_id
    return inst_ids


def to_inst_id(symbols: List[str], source='wind_code') -> List[str]:
    """转换：转为inst_id（二位交易所代码）"""
    if source == 'wind_code':
        return _wind_code2inst_id(symbols)
    else:
        raise ValueError()
    

def get_trading_dates(market, startdate: str, enddate: str) -> List[str]:
    """获取交易日"""
    startdate, enddate = startdate.replace('-', ''), enddate.replace('-', '')
    today = datetime.today()
    # enddate = min(today.strftime("%Y%m%d"), enddate)
    enddate = min(enddate, today.strftime("%Y1231")) # 改为当年最后一日（一般holiday是一年一次更新）
    
    exdates = C.HOLIDAYS.get(market, 'SH')
    if startdate < "20241231":
        fp_his = os.path.join(os.path.dirname(__file__), f'data/trddt_{market}.csv')
        # fp_his = f'data/trddt_{market}.csv'
        all_hisdates = pd.read_csv(fp_his, header=None, dtype=str)[0]
        all_hisdates = all_hisdates[(all_hisdates>=startdate) & (all_hisdates<=enddate)].values.tolist()
    else:
        # 起点超过历史范围：直接使用最新生成数据
        all_hisdates = []
    if enddate > '20241231':
        all_bdates = pd.bdate_range(start=max(startdate, "20241231"), end=enddate).strftime("%Y%m%d").tolist()
    else:
        # 起止都在历史范围，直接调用历史数据
        all_bdates = []
    all_trddts = list(sorted(set(all_hisdates + all_bdates) - set(exdates)))
    return all_trddts


def get_last_trddt(market='SH', n=0, enddate=None) -> str:
    """获取：上一个成交日
    
    - 当日非交易日，默认返回前一个交易日
    - 当日交易日，返回当日
    :param n: 多少个交易日
    :param enddate: 从哪一天开始的上一个交易日
    :return: trddt in %Y%m%d format
    """
    if enddate is None:
        _now = datetime.today()
    else:
        _now = datetime.strptime(enddate, "%Y%m%d")
    _stdate = (_now - timedelta(days=30)).strftime("%Y%m%d")
    # TODO：对于自然日的last_trddt就是最新trddt，例如周末更新宏观数据
    _trddts = get_trading_dates(market, _stdate, _now.strftime("%Y%m%d"))
    return _trddts[-n-1]


def get_next_trddt(startdate=None, n=0, market="SH"):
    """获取：下一个交易日（含当日）
    - 当日非交易日，默认返回下一个交易日
    - 当日交易日，返回当日
    :param startdate: 从哪一天开始的上一个交易日
    :param n: 多少个交易日
    :return: trddt in %Y%m%d format
    """
    if startdate is None:
        _stdate = datetime.today()
    else:
        _stdate = datetime.strptime(startdate, "%Y%m%d")
    _eddate = (_stdate + timedelta(days=30)).strftime("%Y%m%d")
    _trddts = get_trading_dates(market, _stdate.strftime("%Y%m%d"), _eddate)
    return _trddts[n]


def get_latest_trddt(market='SH') -> str:
    """获取：最近交易日

    - 当日交易日，返回当日
    - 当日非交易日，默认返回下一个交易日
    """
    _now = datetime.today()
    _eddate = (_now + timedelta(days=30)).strftime("%Y%m%d")
    _trddts = get_trading_dates(market, _now.strftime("%Y%m%d"), _eddate)
    return _trddts[0]


def is_trading_date(trddt, market='SH') -> bool:
    """判断：是否是交易日
    
    :param trddt: 交易日，支持：datetime(2025, 8, 25), '20250825', '2025-08-25', 20250825, 1747929600000, 1747929600
    :param market: 市场，默认："SH"上交所
    """
    if isinstance(trddt, str):
        trddt = trddt.replace('-', '')
    elif isinstance(trddt, (float, int)):
        if trddt > 1e10:
            trddt /= 1e3  # 转为秒
        trddt = datetime.fromtimestamp(trddt).strftime("%Y%m%d")
    else:
        assert isinstance(trddt, datetime)
        trddt = trddt.strftime("%Y%m%d")
    
    if trddt in CACHE_TRDDTS:
        return True
    else:
        return False


CACHE_TRDDTS = get_trading_dates(market='SH', startdate=SH_STARTDATE, enddate=SH_ENDDATE)
