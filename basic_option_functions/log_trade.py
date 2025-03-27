from datetime import datetime

def log_trade(message, filename):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(message)
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f'[{timestamp}] {message}\n')