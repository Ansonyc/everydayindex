import sys
from flask import Flask, request
sys.path.append('./basic_option_functions')
from basic_option_functions.fetch_etf_history import *
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get_today_index_pb_pe_info():
    # 获取请求参数中的symbol
    symbol = request.args.get('symbol')
    useCache = request.args.get('useCache')
    if useCache == None:
        useCache = False
    else:
        useCache = useCache.lower() == 'true'

    if symbol == None or len(symbol) == 0:
        return 'symbol invalid'
    print(f'query useCache:{useCache} symbol:{symbol}')
    output_path = './data'
    if os.path.exists(output_path) == False:
        os.makedirs(output_path)
    if useCache and os.path.exists(output_path + '/' + symbol + '.csv'):
        df = pd.read_csv(output_path + '/' + symbol + '.csv')
        print('use cache :\n')
    else:
        print('fetch data')
        df = fetch_data(symbol, output_path=output_path)
        df.to_csv(output_path + '/' + symbol + '.csv')

    print('return content :\n')
    print(df)
    # Convert DataFrame to JSON and return
    return df.to_json(orient='records', force_ascii=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9222, debug=True)