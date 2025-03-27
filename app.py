from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def get_today_index_pb_pe_info():
    return "{\"test\":\"123\"}"