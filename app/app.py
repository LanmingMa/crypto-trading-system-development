import decimal

from flask import Flask
from flask import render_template, redirect, url_for, request, flash, session, jsonify
import datetime
import requests
import asyncio
import time
import hashlib
from datetime import timedelta

import mysqlConfig
from mysql.connector import Error
from mysql.connector import errorcode

import transaction as ts
import api

app = Flask(__name__)
app.secret_key = 'please-generate-a-random-secret_key'


@app.before_request
def set_session_timeout():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)


def validateLogin():
    if 'userId' in session:
        return True
    else:
        return False


@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        cursor, conn = mysqlConfig.mysql_connection()
        input_email = request.form['email']
        input_password = request.form['password']
        m = hashlib.md5()
        m.update(input_password.encode('utf-8'))
        cursor.execute("SELECT user_id FROM user WHERE email = %s AND password = %s", (input_email, m.hexdigest(),))
        temp = cursor.fetchone()
        if temp is None:
            error_message = 'Credential is incorrect. Please try again.'
            return render_template('error.html', error_message=error_message)
        else:
            userid = int(temp[0])
            session['userId'] = userid;
            return redirect(url_for('overview'))
        cursor.close()
        conn.close()
    return render_template('login.html')


@app.route('/logout', methods=["GET"])
def logout():
    session.pop('userId', None)
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":

        register_email = str(request.form['register_email'])
        register_username = str(request.form['register_username'])
        register_password = str(request.form['register_password'])
        m = hashlib.md5()
        m.update(register_password.encode('utf-8'))

        cursor, conn = mysqlConfig.mysql_connection()
        cursor.execute("SELECT * FROM user WHERE email = %s or user_name = %s", (register_email, register_username,))
        duplicates = cursor.fetchall()

        if len(duplicates) > 0:
            error_message="That email is already taken, please choose another"
            return render_template('error.html',error_message=error_message)
        else:
            sql = """INSERT INTO user (email, user_name, PASSWORD) VALUES (%s, %s, %s)"""
            val = (register_email, register_username, m.hexdigest(),)
            cursor.execute(sql, val)
            conn.commit()

            cursor.execute("SELECT user_id FROM user WHERE email = %s", (register_email,))
            user_id = cursor.fetchone()[0]

            sql_list = ["INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (1, 0.00, 0.00, 0.00, %s)",
                        "INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (2, 0.00, 0.00, 0.00, %s)",
                        "INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (3, 0.00, 0.00, 0.00, %s)",
                        "INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (4, 0.00, 0.00, 0.00, %s)",
                        "INSERT INTO crypto_bank (user_id, crypto_id, amount) VALUES (%s, 1, 0.00)",
                        "INSERT INTO crypto_bank (user_id, crypto_id, amount) VALUES (%s, 2, 0.00)",
                        "INSERT INTO crypto_bank (user_id, crypto_id, amount) VALUES (%s, 3, 0.00)",
                        "INSERT INTO crypto_bank (user_id, crypto_id, amount) VALUES (%s, 4, 0.00)"]
            val = (user_id,)
            for sql in sql_list:
                cursor.execute(sql, val)
            conn.commit()
            return redirect(url_for('login'))
        cursor.close()
        conn.close()
    return render_template('register.html')


@app.route('/Overview')
def overview():
    if not validateLogin():
        return render_template('login.html')

    Bitcoin = api.candlestick('btcusdt')
    Ethrium = api.candlestick('ethusdt')
    Litecoin = api.candlestick('ltcusdt')
    XRP = api.candlestick('xrpusdt')
    TRON = api.candlestick('trxusdt')

    BitcoinWeekData = api.weekData(Bitcoin)
    EthriumWeekData = api.weekData(Ethrium)
    LitecoinWeekData = api.weekData(Litecoin)
    XRPWeekData = api.weekData(XRP)
    TRONWeekData = api.weekData(TRON)

    class currencyData:
        def __init__(self, name, marketData, weekdata, imageName):
            self.name = name
            self.marketData = marketData
            self.weekdata = weekdata
            self.imageName = imageName

    BitcoinData = currencyData('Bitcoin', api.marketData('btcusdt'), BitcoinWeekData, 'btc')
    EthriumData = currencyData('Ethrium', api.marketData('ethusdt'), EthriumWeekData, 'eth')
    LitecoinData = currencyData('Litecoin', api.marketData('ltcusdt'), LitecoinWeekData, 'ltc')
    BitCoinCashData = currencyData('BitCoin Cash', api.marketData('BCHBTC'), '', 'btcc')
    XRPData = currencyData('XRP', api.marketData('xrpusdt'), XRPWeekData, 'xrp')
    TRONData = currencyData('TRON', api.marketData('trxusdt'), TRONWeekData, 'tron')
    currencies = [BitcoinData, EthriumData, LitecoinData, XRPData, TRONData, BitCoinCashData]
    return render_template('market-overview.html', len=len(currencies), currencies=currencies)


@app.route('/Trading', methods=["GET", "POST"])
def trading():
    if not validateLogin():
        return render_template('login.html')

    if request.method == "POST":
        try:
            cursor, conn = mysqlConfig.mysql_connection()
            conn.autocommit = False

            # show ask price and bid price
            cursor.execute("SELECT crypto_id FROM crypto WHERE crypto_name = %s", (request.form['crypto_name'],))
            crypto_id = cursor.fetchone()[0]
            side = request.form['side']
            time = datetime.datetime.now()
            time.strftime('%Y-%m-%d %H:%M:%S')

            if side == 'Buy':
                # create transaction
                trans = ts.Transaction(crypto_id,
                                       request.form['crypto_name'],
                                       side,
                                       float(request.form['buy_amount']),
                                       float(request.form['buy_price']),
                                       time)

                # check if valid price
                coin_name = trans.name.lower() + 'usdt'
                compare_price = float(api.marketData(coin_name)['askPrice'])
                if trans.price < compare_price * 0.95:
                    error_message = "The price you set is 5% lower than the current ask price. Please reset a valid one."
                    return render_template('error.html',error_message=error_message)
                if trans.price > compare_price * 1.1:
                    error_message = 'The price you set is 10% higher than the current ask price. Please reset a valid one.'
                    return render_template('error.html',error_message=error_message)

                # check if enough cash
                remaining_cash = ts.get_remaining_cash(cursor, conn, session['userId'])
                if not ts.enough_cash_to_buy(remaining_cash, trans.get_amount()):
                    error_message = "You don't have enough cash to buy. Please go to Account-Deposit to refill your account."
                    return render_template('error.html',error_message=error_message)

                # update vwap
                remaining_coin = ts.get_remaining_coin(cursor, conn, trans.id, session['userId'])
                VWAP = ts.get_VWAP(cursor, conn, trans.id, session['userId'])
                updated_VWAP = (VWAP * remaining_coin + decimal.Decimal(trans.get_amount())) / (
                        remaining_coin + decimal.Decimal(trans.amount))
                ts.update_VWAP(cursor, conn, trans.id, session['userId'], updated_VWAP)

            if side == 'Sell':
                # create transaction
                trans = ts.Transaction(crypto_id,
                                       request.form['crypto_name'],
                                       side,
                                       float(request.form['sell_amount']),
                                       float(request.form['sell_price']),
                                       time)
                trans.adjust_side()

                # check if valid price
                coin_name = trans.name.lower() + 'usdt'
                if trans.price > float(api.marketData(coin_name)['bidPrice']) * 1.05:
                    error_message = 'The price you set is 5% higher than the current bid price. Please reset a valid one.'
                    return render_template('error.html',error_message=error_message)
                elif trans.price < float(api.marketData(coin_name)['bidPrice']) * 0.9:
                    error_message = 'The price you set is 10% lower than the current bid price. Please reset a valid one.'
                    return render_template('error.html',error_message=error_message)

                # check if we have enough coin
                remaining_coin = ts.get_remaining_coin(cursor, conn, trans.id, session['userId'])
                if remaining_coin < abs(trans.amount):
                    error_message = "You don't have enough coin to sell. Please try again."
                    return render_template('error.html',error_message=error_message)

                # update RPL
                ts.update_RPL(cursor, conn, crypto_id, trans, session['userId'], trans.price)

            # update cash
            remaining_cash = ts.get_remaining_cash(cursor, conn, session['userId'])
            updated_cash = remaining_cash - decimal.Decimal(trans.get_amount())
            ts.update_cash(cursor, conn, updated_cash, session['userId'])


            # update blotter
            ts.update_blotter(cursor, conn, trans.id, trans.amount, trans.price, trans.time,
                              trans.side, session['userId'])

            # update crypto_bank
            remaining_coin += decimal.Decimal(trans.amount)
            ts.update_crypto_bank(cursor, conn, crypto_id, remaining_coin, session['userId'])

            conn.commit()

        except conn.Error as error:
            print("Failed to update record to database rollback: {}".format(error))
            # reverting changes because of exception
            conn.rollback()

        finally:
            if (conn.is_connected()):
                cursor.close()
                conn.close()
                print("connection is closed")

        return redirect(url_for('trading'))

    else:
        Bitcoin = api.candlestick('btcusdt')
        Ethrium = api.candlestick('ethusdt')
        Litecoin = api.candlestick('ltcusdt')

        BitcoinWeekData = api.weekData(Bitcoin)
        EthriumWeekData = api.weekData(Ethrium)
        LitecoinWeekData = api.weekData(Litecoin)

        class currencyData:
            def __init__(self, name, marketData, weekdata, imageName):
                self.name = name
                self.marketData = marketData
                self.weekdata = weekdata
                self.imageName = imageName

        BitcoinData = currencyData('Bitcoin', api.marketData('btcusdt'), BitcoinWeekData, 'btc')
        EthriumData = currencyData('Ethrium', api.marketData('ethusdt'), EthriumWeekData, 'eth')
        LitecoinData = currencyData('Litecoin', api.marketData('ltcusdt'), LitecoinWeekData, 'ltc')
        currencies = [BitcoinData, EthriumData, LitecoinData]

        cursor, conn = mysqlConfig.mysql_connection()
        # update UPL
        coins = ['btcusdt', 'ethusdt', 'ltcusdt']
        bid_price = []
        userId = session['userId']
        remaining_coin_q = """SELECT amount FROM crypto_bank WHERE user_id = %s"""
        cursor.execute(remaining_coin_q, (userId,))
        results = cursor.fetchall()

        VWAP_list = []
        crypto_id_list = [1, 2, 3]
        for crypto_id in crypto_id_list:
            VWAP = ts.get_VWAP(cursor, conn, crypto_id, session['userId'])
            VWAP_list.append(VWAP)

        for i in range(len(coins)):
            result = results[i]
            amount = float(str(result).strip("(Decimal(''),)"))
            upl = (float(api.marketData(coins[i])['bidPrice']) - float(VWAP_list[i])) * amount
            bid_price.append(upl)
            cursor.execute("UPDATE PnL SET UPL = %s WHERE crypto_id = %s AND user_id = %s",
                           (bid_price[i], i + 1, userId,))
        conn.commit()

        # display blotter the pnl & Cash
        cursor, conn = mysqlConfig.mysql_connection()
        blotter_list, PnL_list = ts.display_blotter_PnL(cursor, conn, session['userId'])
        Cash_quantity = ts.get_remaining_cash(cursor, conn, session['userId'])
        cursor.close()
        conn.close()

    return render_template('trading.html', Cash_quantity = Cash_quantity, blotter_list=blotter_list, PnL_list=PnL_list,len=len(currencies), currencies=currencies)


@app.route('/Account', methods=["GET", "POST"])
def account():
    if not validateLogin():
        return render_template('login.html')
    cursor, conn = mysqlConfig.mysql_connection()
    if request.method == "POST":
        payment_amount = request.form['payment_amount']
        remaining_cash = ts.get_remaining_cash(cursor, conn, session['userId'])
        print(remaining_cash, type(remaining_cash))
        if request.form['operation'] == 'payment':
            updated_cash = decimal.Decimal(float(remaining_cash) + float(payment_amount))
        else:
            updated_cash = decimal.Decimal(float(remaining_cash) - float(payment_amount))
        # update cash amount
        ts.update_cash(cursor, conn, updated_cash, session['userId'])

    Cash_quantity = ts.get_remaining_cash(cursor, conn, session['userId'])
    blotter_list, PnL_list = ts.display_blotter_PnL(cursor, conn, session['userId'])
    cursor.close()
    conn.close()
    return render_template('withdrawl.html', Cash_quantity = Cash_quantity, blotter_list=blotter_list, PnL_list=PnL_list)


@app.route('/_dataUpdate', methods=['GET'])
def dataUpdate():
    return jsonify(result=time.time())


@app.route('/_stuff', methods=['GET'])
def stuff():
    Bitcoin = api.candlestick('btcusdt')
    Ethrium = api.candlestick('ethusdt')
    Litecoin = api.candlestick('ltcusdt')
    XRP = api.candlestick('xrpusdt')
    TRON = api.candlestick('trxusdt')

    return jsonify(
        BTC=api.marketData('btcusdt'),
        ETH=api.marketData('ethusdt'),
        LTC=api.marketData('ltcusdt'),
        BTCC=api.marketData('BCHBTC'),
        XRP=api.marketData('xrpusdt'),
        TRON=api.marketData('trxusdt'),
        BitcoinWeekData=api.weekData(Bitcoin),
        EthriumWeekData=api.weekData(Ethrium),
        LitecoinWeekData=api.weekData(Litecoin),
        XRPWeekData=api.weekData(XRP),
        TRONWeekData=api.weekData(TRON)
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
