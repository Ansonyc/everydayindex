import sys
import akshare as ak
import os
import pandas as pd

def index_option_50etf_qvix() -> pd.DataFrame:
    """
    50ETF 期权波动率指数 QVIX
    http://1.optbbs.com/s/vix.shtml?50ETF
    :return: 50ETF 期权波动率指数 QVIX
    :rtype: pandas.DataFrame
    """
    url = "http://1.optbbs.com/d/csv/d/k.csv"
    temp_df = pd.read_csv(url, encoding='gbk').iloc[:, :5]
    temp_df.columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
    ]
    temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce").dt.date
    temp_df['open'] = pd.to_numeric(temp_df['open'], errors="coerce")
    temp_df['high'] = pd.to_numeric(temp_df['high'], errors="coerce")
    temp_df['low'] = pd.to_numeric(temp_df['low'], errors="coerce")
    temp_df['close'] = pd.to_numeric(temp_df['close'], errors="coerce")
    return temp_df


def index_option_300etf_qvix() -> pd.DataFrame:
    """
    300 ETF 期权波动率指数 QVIX
    http://1.optbbs.com/s/vix.shtml?300ETF
    :return: 300 ETF 期权波动率指数 QVIX
    :rtype: pandas.DataFrame
    """
    url = "http://1.optbbs.com/d/csv/d/k.csv"
    temp_df = pd.read_csv(url, encoding='gbk').iloc[:, [0, 9, 10, 11, 12]]
    temp_df.columns = [
        "date",
        "open",
        "high",
        "low",
        "close",
    ]
    temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce").dt.date
    temp_df['open'] = pd.to_numeric(temp_df['open'], errors="coerce")
    temp_df['high'] = pd.to_numeric(temp_df['high'], errors="coerce")
    temp_df['low'] = pd.to_numeric(temp_df['low'], errors="coerce")
    temp_df['close'] = pd.to_numeric(temp_df['close'], errors="coerce")
    return temp_df

def preprocess_data(df_price_hfq, symbol = "上证50", symbol_h_l = 'sz50'):
    df_vix = None
    df_high_low = None
    df_pb = None
    df_pe = None
    df_below_net = None
    # 获取波动率历史
    if symbol == '沪深300':
        df_vix = index_option_300etf_qvix()
    else:
        df_vix = index_option_50etf_qvix()

    if df_vix is not None and len(df_vix) > 0:
        df_vix['vix_mid'] = (df_vix['high'] + df_vix['low']) / 2
        df_vix['ema_vix_mid'] = df_vix['vix_mid'].ewm(span=5).mean()
        if 'date' in df_vix.columns:
            df_vix = df_vix.rename(columns = {'date': '日期', 'open': 'vix_open', 'high': 'vix_high', 'low': 'vix_low', 'close': 'vix_close'})
            # df_vix.to_csv(f'{symbol}_vix.csv')
            print('vix.csv已完成')

    # 创新高/新低数
    if len(symbol_h_l) > 0:
        df_high_low = ak.stock_a_high_low_statistics(symbol=symbol_h_l)
        df_high_low = ak.stock_a_high_low_statistics(symbol=symbol_h_l)
        df_high_low = df_high_low.rename(columns={'date':'日期'})
        df_high_low['delta_20_highlow'] = df_high_low['high20'] - df_high_low['low20']
        df_high_low['delta_60_highlow'] = df_high_low['high60'] - df_high_low['low60']
        df_high_low['delta_120_highlow'] = df_high_low['high120'] - df_high_low['low120']
        df_high_low['ema_delta_20_highlow'] = df_high_low['delta_20_highlow'].ewm(span=20, adjust=False).mean()
        df_high_low['ema_delta_60_highlow'] = df_high_low['delta_60_highlow'].ewm(span=20, adjust=False).mean()
        df_high_low['ema_delta_120_highlow'] = df_high_low['delta_120_highlow'].ewm(span=20, adjust=False).mean()

        print('high_low.csv已完成')

    df_price_hfq = df_price_hfq.rename(columns = {"开盘":"open", "收盘": "close", "最高" : "high", "最低" : "low", "成交量": "volume"})
    
    try:
        # 获取市净率历史
        df_pb = ak.stock_index_pb_lg(symbol=symbol)
        print('pb.csv已完成')
    except:
        print('pb.csv获取失败')

    # 获取市盈率历史
    try:
        df_pe = ak.stock_index_pe_lg(symbol=symbol)
        print('pe.csv已完成')
    except:
        print('pe.csv获取失败')

    # 获取破净率历史
    try:
        df_below_net = ak.stock_a_below_net_asset_statistics(symbol=symbol)
        if 'date' in df_below_net.columns:
            df_below_net = df_below_net.rename(columns = {'date': '日期'})
    except:
        print('below_net.csv获取失败')

    return join_data(df_price_hfq, df_vix, df_high_low, df_pb, df_pe, df_below_net)

def join_data(df_price, df_vix, df_high_low, df_pb, df_pe, df_below_net):
    # 确保所有数据框的日期列都是datetime类型
    df_price['日期'] = pd.to_datetime(df_price['日期'])
    if df_vix is not None:
        df_vix['日期'] = pd.to_datetime(df_vix['日期'])
        df_vix = df_vix[['日期', 'vix_open', 'vix_high', 'vix_low', 'vix_close', 'ema_vix_mid']]
        # 确保日期范围匹配
        min_date = df_vix['日期'].min()
        df_price = df_price[df_price['日期'] >= min_date]
        df_price = pd.merge(df_price, df_vix, on='日期', how='left')
    
    if df_pb is not None:
        df_pb['日期'] = pd.to_datetime(df_pb['日期'])
        df_pb = df_pb[['日期','市净率','市净率中位数']]
        df_price = pd.merge(df_price, df_pb, on='日期', how='left')

    if df_pe is not None:
        df_pe['日期'] = pd.to_datetime(df_pe['日期'])
        df_pe = df_pe[['日期','滚动市盈率','滚动市盈率中位数']]
        df_price = pd.merge(df_price, df_pe, on='日期', how='left')

    if df_below_net is not None:
        df_below_net['日期'] = pd.to_datetime(df_below_net['日期'])
        df_below_net = df_below_net[['日期','below_net_asset_ratio']]
        df_price = pd.merge(df_price, df_below_net, on='日期', how='left')

    if df_high_low is not None:
        df_high_low['日期'] = pd.to_datetime(df_high_low['日期'])
        df_high_low = df_high_low[['日期','ema_delta_20_highlow','ema_delta_60_highlow','ema_delta_120_highlow']]
        df_price = pd.merge(df_price, df_high_low, on='日期', how='left')
    
    # 当前行的值为空，使用上一行同一列数值代替
    df_price = df_price.ffill()
    # 保存数据
    # df.to_csv('data.csv')
    return df_price

def fetch_data(symbol, output_path):
    symbol_map = {'510050': ['上证50', 'sz50'], 
    '510300': ['沪深300', 'hs300'],
    '588000': ['科创50', '']}

    for key, value in symbol_map.items():
        if key != symbol:
            continue
        symbol, symbol_h_l = value
        # 使用akshare获取50ETF前复权历史行情数据
        etf_qfq = ak.fund_etf_hist_em(symbol=key, adjust='qfq')

        # # 处理原始数据
        df_index = preprocess_data(etf_qfq, symbol = symbol, symbol_h_l = symbol_h_l)
        
        df_index.to_csv(f'{output_path}/{key}_index.csv', index=False)
        return df_index
    return None