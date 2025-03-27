import sys
from flask import Flask, request
sys.path.append('./basic_option_functions')
from basic_option_functions.fetch_etf_history import *
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get_today_index_pb_pe_info():
    # 获取请求参数中的symbol
    symbol = request.args.get('symbol')
    if symbol == None or len(symbol) == 0:
        return 'symbol invalid'

    output_path = './data'
    if os.path.exists(output_path) == False:
        os.makedirs(output_path)
    df = fetch_data(symbol, output_path=output_path)
    print('return content :\n')
    print(df)
    # Convert DataFrame to JSON and return
    return df.to_json(orient='records', force_ascii=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9222, debug=True)