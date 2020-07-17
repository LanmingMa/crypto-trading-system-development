import requests

def marketData(currency):
    return requests.get('https://api.binance.com/api/v3/ticker/24hr?symbol=' + currency.upper()).json()


def candlestick(currency):
    return requests.get('https://api.binance.com/api/v3/klines?symbol=' + currency.upper() + '&interval=1d').json()


def weekData(currency):
    weekData = []
    for i in range(0, 7):
        weekData.append(float(currency[493 + i][4]))
    return weekData
