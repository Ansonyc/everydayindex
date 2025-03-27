import mysql.connector
import pandas as pd

# MySQL配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '12345678',
    'database': 'options_data',
}

def get_remain_days_contracts(cursor, trade_date, table_name):
    sql = """
    WITH code AS (
        SELECT security_code, security_name
        FROM options_data.{0} 
        WHERE trade_date = %s
    )
    SELECT 
        COUNT(DISTINCT sub.security_code) as contract_count,
        sub.remain_days,
        sub.month
    FROM (
        SELECT 
            h.security_code,
            REGEXP_REPLACE(h.security_name, '.*购|.*沽|月.*', '') as month,
            COUNT(DISTINCT t.trade_date) as remain_days
        FROM options_data.{0} h
        JOIN code ON h.security_code = code.security_code
        LEFT JOIN options_data.{0} t 
            ON h.security_code = t.security_code 
            AND t.trade_date >= %s
        WHERE h.trade_date = %s
        GROUP BY h.security_code, h.security_name
    ) sub
    GROUP BY sub.remain_days, sub.month
    ORDER BY sub.remain_days DESC
    """.format(table_name)
    
    cursor.execute(sql, (trade_date, trade_date, trade_date))
    return cursor.fetchall()

def get_trading_contracts(cursor, current_date, table_name):
    sql = """
    SELECT security_code, security_name, close_price
    FROM options_data.{}
    WHERE trade_date = %s
    """.format(table_name)
    cursor.execute(sql, (current_date,))
    return pd.DataFrame(cursor.fetchall(), columns=['security_code', 'security_name', 'close_price'])