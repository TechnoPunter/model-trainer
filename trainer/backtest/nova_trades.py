"""
    Remember: Make sure to handle entry & exit in same row
"""
import json
from datetime import datetime
from typing import Literal, Dict, get_args

from trainer.backtest.nova_order import OrderBook
from commons.consts.consts import IST
import logging

logger = logging.getLogger(__name__)

DIRECTION = Literal["BUY", "SELL", "EXIT"]
POS_QTY = 'pos_quantity'
TRADED_VAL = 'traded_value'
TRADE_LIST = 'trade_list'
TRADE_DIR = 'trade_direction'
SL_UPDATE_CNT = 'sl_update_count'


# @dataclass
class Trade:
    id: int
    scrip: str
    direction: str
    quantity: float
    price: float
    order_id: int
    time: int
    event: str

    def __init__(self, trade: Dict):
        for key, value in trade.items():
            setattr(self, key, value)
        self.__post_init__()

    def __post_init__(self):
        assert hasattr(self, "id"), "Need Id"
        assert hasattr(self, "scrip"), "Need Scrip"
        assert hasattr(self, "direction"), "Need Direction"
        assert hasattr(self, "quantity"), "Need Quantity"
        assert hasattr(self, "price"), "Need Price"
        assert hasattr(self, "order_id"), "Need Order Id"
        assert hasattr(self, "time"), "Need Order Time (Epoch)"
        assert hasattr(self, "event"), "Need Event"
        assert self.direction in get_args(DIRECTION), f"Direction should be {DIRECTION}"
        assert self.quantity != 0.0, "Quantity should be non-zero"
        assert self.price != 0.0, "Price should be non-zero"

    def get_dir_qty(self) -> float:
        if self.direction == "BUY":
            return self.quantity
        else:
            return -1 * self.quantity

    def __repr__(self):
        return f"""'Trade ID: {self.id}, Order ID: {self.order_id}, scrip: {self.scrip}, direction: {self.direction}, 
        quantity: {self.quantity} @ {self.price} on {datetime.fromtimestamp(self.time, tz=IST)},
        event: {self.event}'"""


class TradeBook:
    trades: [Trade]
    pos: Dict[int, Dict]
    results: list[Dict[str, str]]
    order_book: OrderBook

    def __init__(self, order_book):
        self.trades = []
        self.pos = {}
        self.results = []
        self.__post_init__()
        self.order_book = order_book

    def __post_init__(self):
        pass

    def _push_order(self, t: Trade, order_params: Dict = None):
        if order_params is None:
            order_type = "MARKET"
            sl_range = -1
            sl = -1
            target = -1
            movement_step_trail_sl = -1
            sl_step = -1
            anchor_price = -1
        else:
            sl_range = order_params.get("sl_range", -1)
            sl = order_params.get("sl", -1)
            target = order_params.get("target", -1)
            movement_step_trail_sl = order_params.get("trail_sl", -1)
            sl_step = order_params.get("trail_sl", -1)
            anchor_price = order_params.get("anchor_price", -1)
            if sl != -1 and target != -1:
                order_type = "BO"
            elif sl != -1:
                order_type = "CO"
            else:
                order_type = "MARKET"
        o = f'''{{
            "id": {t.order_id},
            "scrip": "{t.scrip}",
            "direction": "{t.direction}",
            "quantity": {t.quantity},
            "time": {t.time},
            "price": {t.price},
            "type": "{order_type}",
            "entry_limit": -1,
            "sl_range": {sl_range},
            "sl": {sl},
            "sl_step": {sl_step},
            "target": {target},
            "target_range": -1,
            "movement_step_trail_sl": {movement_step_trail_sl},
            "anchor_price": {anchor_price}
        }}'''
        self.order_book.enter_order(json.loads(o))

    def enter(self, t: Trade, pos_params: Dict = None):
        """

        Args:
            t: Trade
            pos_params: Trade Parameters
                sl: Stop Loss of for the trade
                target: Target Price for the trade
                sl_range: No. of points for stop loss from the current Open
                profit_range: No. of points for profit from the current Open

                trail_price: No. of points after which to change SL by trail_price

                Note: Either sl or sl_range can be specified, ditto for target and profit_range

        Returns:

        """
        self.trades.append(t)
        self._push_order(t, pos_params)
        return self.update_positions(t, pos_params)

    def exit(self, t: Trade):
        posn = self.get_open_position(t.order_id)
        assert len(posn) > 0, f"No open positions with Order Id: {t.order_id}"
        if t.direction == "EXIT":
            if posn[t.order_id].get(TRADE_DIR) == "SELL":
                t.direction = "BUY"
            else:
                t.direction = "SELL"
        self.trades.append(t)
        self.order_book.update_order(t.order_id, [t.event])
        return self.update_positions(t)

    def update_sl(self, order_id: int, row=None):
        self.order_book.update_order(order_id=order_id, updates=["update-sl"], row=row)
        for key, pos in self.pos.items():
            if key == order_id:
                updated_pos = pos
                updated_pos[SL_UPDATE_CNT] += 1
                self.pos[key] = updated_pos

    def update_stats(self, row):
        for order_id, posn in self.pos.items():
            curr_pnl = self.get_pos_pnl(order_id=order_id, include_open=True, ltp=row['close'])
            if curr_pnl < 0:
                if curr_pnl < posn.get('maxloss', 0):
                    posn['maxloss'] = curr_pnl
                    self.pos[order_id] = posn
            elif curr_pnl > 0:
                if curr_pnl > posn.get('maxprofit', 0):
                    posn['maxprofit'] = curr_pnl
                    self.pos[order_id] = posn

    def get_open_positions(self):
        return {k: v for k, v in self.pos.items() if (v[POS_QTY] != 0.0)}

    def get_open_position(self, order_id: int):
        return {k: v for k, v in self.get_open_positions().items() if (k == order_id)}

    def get_position(self, order_id: int):
        return {k: v for k, v in self.pos.items() if (k == order_id)}

    def get_trade(self, id: int):
        for trade in self.trades:
            if trade.id == id:
                return trade

    def update_positions(self, t: Trade, pos_params: Dict = None):

        qty = t.get_dir_qty()

        if self.pos.get(t.order_id):
            pos_dict = self.pos[t.order_id]
            pos_dict[POS_QTY] += qty
            pos_dict[TRADED_VAL] += -1 * qty * t.price
            pos_dict[TRADE_LIST] = pos_dict[TRADE_LIST] + [t]
            self.pos[t.order_id] = pos_dict
        else:
            if pos_params is not None:
                params = pos_params
            else:
                params = {}
            params.update({POS_QTY: qty})
            params.update({TRADED_VAL: -1 * qty * t.price})
            params.update({TRADE_LIST: [t]})
            params.update({TRADE_DIR: t.direction})
            params.update({'sl_update_count': 0})
            self.pos.update({t.order_id: params})
        return self.pos

    def get_pos_pnl(self, order_id, include_open: bool = False, ltp: float = None) -> float:
        pnl: float = 0.0

        posn = self.get_position(order_id)[order_id]
        if posn[POS_QTY] == 0:
            pnl += posn[TRADED_VAL]
        elif include_open and posn[POS_QTY] < 0:
            pnl += (posn[TRADED_VAL] + posn[POS_QTY] * ltp)
        elif include_open and posn[POS_QTY] > 0:
            pnl += (posn[POS_QTY] * ltp + posn[TRADED_VAL])
        return pnl

    def get_pnl(self, include_open: bool = False, ltp: float = None) -> float:
        pnl: float = 0.0
        for order_id, posn in self.pos.items():
            pnl += self.get_pos_pnl(order_id, include_open=include_open, ltp=ltp)
        return pnl

    def populate_trade_book(self):
        cum_pnl: float = 0.0
        for order_id, posn in self.pos.items():
            posn_trades = posn.get(TRADE_LIST)
            if len(posn_trades) == 1:
                res = {'ref': posn.get(TRADE_LIST)[0].time,
                       'scrip': posn_trades[0].scrip,
                       'dir': posn.get(TRADE_DIR),
                       'datein': datetime.fromtimestamp(posn.get(TRADE_LIST)[0].time, tz=IST),
                       'pricein': posn_trades[0].price,
                       'size': posn_trades[0].quantity,
                       'eventin': posn_trades[0].event,
                       'slupdcnt': posn.get(SL_UPDATE_CNT),
                       'maxprofit': posn.get('maxprofit', 0),
                       'maxloss': posn.get('maxloss', 0),
                       # 'dateout': datetime.fromtimestamp(posn.get(TRADE_LIST)[1].time, tz=IST),
                       # 'priceout': posn.get(TRADE_LIST)[1].price,
                       # 'chng%': round(pcntchange, 2), 'pnl': pnl, 'pnl%': round(pnlpcnt, 2),
                       # 'size': size, 'value': value, 'cumpnl': self.cumprofit,
                       # 'nbars': barlen, 'pnl/bar': round(pbar, 2),
                       # 'mfe%': round(mfe, 2), 'mae%': round(mae, 2)
                       }
            else:
                cum_pnl += posn[TRADED_VAL]
                res = {'ref': posn.get(TRADE_LIST)[0].time,
                       'scrip': posn_trades[0].scrip,
                       'dir': posn.get(TRADE_DIR),
                       'size': posn_trades[0].quantity,
                       'datein': datetime.fromtimestamp(posn.get(TRADE_LIST)[0].time, tz=IST),
                       'pricein': posn_trades[0].price,
                       'eventin': posn_trades[0].event,
                       'dateout': datetime.fromtimestamp(posn.get(TRADE_LIST)[1].time, tz=IST),
                       'priceout': posn.get(TRADE_LIST)[1].price,
                       'eventout': posn_trades[1].event,
                       'pnl': posn[TRADED_VAL],
                       'cumpnl': cum_pnl,
                       'result': 'P' if posn.get(TRADED_VAL, 0) > 0 else 'L',
                       'sl': posn['sl'],
                       'target': posn['target'],
                       'slupdcnt': posn.get(SL_UPDATE_CNT),
                       'maxprofit': posn.get('maxprofit', 0),
                       'maxloss': posn.get('maxloss', 0),
                       # 'chng%': round(pcntchange, 2), 'pnl': pnl, 'pnl%': round(pnlpcnt, 2),
                       # 'size': size, 'value': value,
                       # 'nbars': barlen, 'pnl/bar': round(pbar, 2),
                       # 'mfe%': round(mfe, 2), 'mae%': round(mae, 2)
                       }

            self.results.append(res)

        return self.results


if __name__ == "__main__":
    ob = OrderBook({})
    tb = TradeBook(ob)

    t1 = {
        "id": 1,
        "scrip": "ABC",
        "direction": "BUY",
        "quantity": 2.0,
        "price": 10.0,
        "order_id": 10,
        "time": 1000,
        "event": "entry-long"
    }

    x = tb.enter(Trade(t1), {"sl": 9.0, "target": 11})
    print(x)

    t2 = {
        "id": 2,
        "scrip": "ABC",
        "direction": "SELL",
        "quantity": 1.0,
        "price": 10.5,
        "order_id": 10,
        "time": 1000,
        "event": "entry-short"
    }

    x = tb.exit(Trade(t2))
    print(x)

    t3 = {
        "id": 3,
        "scrip": "ABC",
        "direction": "SELL",
        "quantity": 1.0,
        "price": 9,
        "order_id": 10,
        "time": 2000,
        "event": "exit=sl"
    }

    x = tb.exit(Trade(t3))
    print(x)

    t4 = {
        "id": 4,
        "scrip": "ABC",
        "direction": "SELL",
        "quantity": 1.0,
        "price": 9,
        "order_id": 20,
        "time": 4000,
        "event": "entry-short"
    }

    x = tb.enter(Trade(t4))
    print(x)

    x = tb.get_open_positions()
    print(x)

    x = tb.get_open_position(10)
    print("No open position #10: " + str(x))

    x = tb.get_open_position(20)
    print("Open position #20 :" + str(x))
