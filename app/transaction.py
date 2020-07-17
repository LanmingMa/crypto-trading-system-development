import decimal
from flask import session, render_template

class Transaction:
    def __init__(self, id, name, side, amount, price, time):
        self.id = id
        self.name = name
        self.side = side
        self.amount = amount
        self.price = price
        self.time = time

    def adjust_side(self):
        self.amount = self.amount * (-1)

    def get_amount(self):
        return self.amount * self.price


def get_remaining_cash(cursor, conn, userId):
    cursor.execute("SELECT amount FROM crypto_bank WHERE crypto_id = 4 AND user_id = %s", (userId,))
    remaining_cash = cursor.fetchone()[0]
    return remaining_cash


def enough_cash_to_buy(remaining_cash, need_cash):
    if remaining_cash < need_cash:
        return False
    else:
        return True


def update_cash(cursor, conn, updated_cash, userId):
    cursor.execute("UPDATE crypto_bank SET amount = %s WHERE crypto_id = 4 AND user_id = %s",
                   (updated_cash, userId,))


def get_remaining_coin(cursor, conn, crypto_id, userId):
    remaining_coin_q = """SELECT amount FROM crypto_bank WHERE crypto_id = %s AND user_id = %s"""
    v = (crypto_id, userId,)
    cursor.execute(remaining_coin_q, v)
    remaining_coin = cursor.fetchone()[0]
    return remaining_coin


def update_RPL(cursor, conn, crypto_id, trans, userId, price):
    cursor.execute("SELECT RPL FROM PnL WHERE crypto_id = %s AND user_id = %s",
                   (crypto_id, userId,))
    RPL = cursor.fetchone()[0]

    VWAP_q = """SELECT VWAP FROM PnL WHERE crypto_id = %s AND user_id = %s"""
    v = (crypto_id, userId,)
    cursor.execute(VWAP_q, v)
    VWAP = cursor.fetchone()[0]

    updated_RPL = RPL + ((decimal.Decimal(price) - VWAP) * (decimal.Decimal(trans.amount)*(-1)))
    cursor.execute("UPDATE PnL SET RPL = %s WHERE crypto_id = %s AND user_id = %s",
                   (updated_RPL, crypto_id, userId,))


def get_VWAP(cursor, conn, crypto_id, userId):
    VWAP_q = """SELECT VWAP FROM PnL WHERE crypto_id = %s AND user_id = %s"""
    v = (crypto_id, userId,)
    cursor.execute(VWAP_q, v)
    VWAP = cursor.fetchone()[0]
    return VWAP


def update_VWAP(cursor, conn, crypto_id, userId, updated_VWAP):
    update_VWAP_q = """UPDATE PnL SET VWAP = %s WHERE crypto_id = %s AND user_id = %s"""
    v = (updated_VWAP, crypto_id, userId,)
    cursor.execute(update_VWAP_q, v)


def update_blotter(cursor, conn, crypto_id, amount, price, time, side, userId):
    sql = """INSERT INTO blotter (crypto_id, quantity, price, trading_date, side, user_id)
                                        VALUES (%s, %s, %s, %s, %s, %s)"""
    val = (crypto_id, amount, price, time, side, userId,)
    cursor.execute(sql, val)


def update_crypto_bank(cursor, conn, crypto_id, remaining_coin, userId):
    cursor.execute("UPDATE crypto_bank SET amount = %s WHERE crypto_id = %s AND user_id = %s",
                   (remaining_coin, crypto_id, userId,))

def display_blotter_PnL(cursor, conn, userId):
    show_blotter = """SELECT b.trading_date, c.crypto_name, b.quantity, b.price, b.side 
                                FROM blotter b, crypto_bank bk, crypto c
                                WHERE b.crypto_id = bk.crypto_id and b.crypto_id = c.crypto_id
                                AND b.user_id = %s AND bk.user_id = %s
                                ORDER BY trading_date DESC"""
    v = (userId, userId)
    cursor.execute(show_blotter, v)
    records = cursor.fetchall()
    blotter_list = []
    for record in records:
        blotter_list.append(
            [record[0], record[1], float(record[2]), float(record[3]), record[4], float(record[2] * record[3])])

    PnL_list = []
    get_coins = """SELECT cr.crypto_name, bk.amount, p.UPL, p.RPL, p.VWAP
                               FROM PnL p INNER JOIN crypto_bank bk INNER JOIN crypto cr
                                WHERE p.crypto_id = bk.crypto_id AND p.user_id = bk.user_id AND cr.crypto_id = bk.crypto_id
                                AND bk.crypto_id <> 4
                                AND p.user_id = %s"""
    v = (userId,)
    cursor.execute(get_coins, v)
    coins = cursor.fetchall()
    print(coins)
    for coin in coins:
        PnL_list.append([coin[0], coin[1], coin[2], coin[3], coin[4]])
    return blotter_list, PnL_list
