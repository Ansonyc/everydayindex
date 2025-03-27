import math

def process_contract(security_code, from_date, days, cursor, table_name, isSell=False):
    # 获取合约名称和起始日期的收盘价
    sql = """
    SELECT security_name, close_price
    FROM {0}
    WHERE security_code = %s AND trade_date = %s
    """.format(table_name)
    cursor.execute(sql, (security_code, from_date))
    result = cursor.fetchone()
    security_name, entry_price = result
    
    # 获取从起始日期到结束日期的每日收盘价
    sql = """
    SELECT trade_date, close_price
    FROM {}
    WHERE security_code = %s 
    AND trade_date >= %s 
    ORDER BY trade_date
    limit %s
    """.format(table_name)
    cursor.execute(sql, (security_code, from_date, days))
    daily_data = cursor.fetchall()
    
    # total_investment = 10000
    # scale_factor = math.floor(total_investment / (10000 * entry_price))
    # 计算每日盈亏
    daily_pnls = []
    for day_data in daily_data:
        day_date, day_close = day_data
        # 如果是卖出合约，盈亏方向相反
        pnl = (entry_price - day_close) * 10000 if isSell else (day_close - entry_price) * 10000
        # pnl *= scale_factor
        daily_pnls.append((day_date, pnl, security_name, day_close))
        # if (0 - total_investment * 0.5) > pnl:
        #     log_trade(f"{day_date} 总盈亏: {pnl:.2f} 止损")
        #     break
    return daily_pnls
