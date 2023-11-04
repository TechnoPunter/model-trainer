import json
from typing import Literal, Dict

import numpy as np
import pandas as pd

from trainer.backtest.nova_order import Order
import logging

logger = logging.getLogger(__name__)

Events = Literal["entry-short", "entry-long", "exit-sl", "exit-tgt", "exit-cob", "exit-reversal", "trail-sl"]


def get_entry_condition(direction: int, row):
    if np.isnan(row['signal']):
        return False
    if row['signal'] != direction:
        return False
    logger.debug(f"Dir: {direction}")
    if direction == -1 and row['open'] > row['target']:
        logger.debug(f"Short on Row: {row} ")
        return True
    elif direction == 1 and row['open'] < row['target']:
        logger.debug(f"Long on Row: {row} ")
        return True
    else:
        logger.debug(f"Hold on Row: {row} ")
        return False


def get_sl_condition(row, order: Order):
    if order is None:
        return False

    if order.direction == "BUY":
        return row['low'] <= order.sl
    else:
        return row['high'] >= order.sl


def get_target_condition(row, order: Order):
    if order is None:
        return False

    if order.direction == "BUY":
        return row['high'] >= order.target
    else:
        return row['low'] <= order.target


def get_trail_sl_condition(row, order: Order):
    if order is None:
        return False

    logger.debug(
        f"Get trail @ {row['date']}, diff: {abs(row['close'] - order.anchor_price)} & anchor: {order.anchor_price}")
    if order.direction == "BUY":
        return row['close'] - order.anchor_price >= order.movement_step_trail_sl
    else:
        return order.anchor_price - row['close'] >= order.movement_step_trail_sl


class Condition:
    column: str
    predicate: str
    column_function: str

    def __init__(self, d: Dict):
        for key, value in d.items():
            setattr(self, key, value)

        if getattr(self, 'column_function', None) is None:
            self.column_function = None


class EventCondition:
    event: Events
    conditions: [Condition]

    def __init__(self, d: Dict):
        l = []
        for key, value in d.items():
            if key == "conditions":

                for condition in value:
                    l.append(Condition(condition))
            else:
                setattr(self, key, value)
        setattr(self, "conditions", l)


class EventManager:
    def eval(self, event_conditions: [EventCondition], row: pd.Series, orders: list[Order] = None):
        """

        Args:
            event_conditions: Single Event Conditions
            row: Dataframe row to evaluate the conditions against
            orders: Orders to be used for evaluation of events (SL, Target etc.)

        Returns:
            {
                "event_name": [ Order Ids (-1 if non-order linked)],
                ...
                "entry-long": [-1],
                "exit-cob": [-1],
                "exit-target": [1, 5]
            }
        """

        event_dict = {}
        for ec in event_conditions:
            events = []
            if ec['type'] == "independent":
                for cond in ec.get('conditions'):
                    if cond.get('column') == 'None':
                        col = str(None)
                    elif np.isnan(row[cond.get('column')]):
                        col = str(None)
                    else:
                        col = str(row[cond.get('column')])

                    if cond.get('function') is not None:
                        val = col
                        col = str(eval(cond.get('function')))
                    # Actual Evaluation
                    if eval(col + cond.get('predicate')):
                        events.append(-1)

            elif ec['type'] == "order-based":
                for order in orders:
                    for cond in ec.get('conditions'):
                        if cond.get('column') == 'None':
                            col = str(None)
                        elif np.isnan(row[cond.get('column')]):
                            col = str(None)
                        else:
                            col = str(row[cond.get('column')])

                        if cond.get('function') is not None:
                            val = col
                            col = str(eval(cond.get('function')))

                        # Actual Evaluation
                        if eval(col + cond.get('predicate')):
                            events.append(order.id)

            if len(events) > 0:
                event_dict[ec.get('event')] = list(set(events))

        return event_dict


if __name__ == "__main__":
    e = EventManager()
    c = [
        EventCondition({
            "event": "entry-long",
            "conditions": [
                {
                    "column": "signal",
                    "predicate": " == 1.0"
                }
            ]
        }),
        EventCondition({
            "event": "entry-short",
            "conditions": [
                {
                    "column": "signal",
                    "predicate": " == -1.0"
                }
            ]
        }),
        EventCondition({
            "event": "exit-cob",
            "conditions": [
                {
                    "column": "time",
                    "predicate": " >= 20.0",
                    "column_function": 'f"{val} * 10"'
                }
            ]
        }),
        EventCondition({
            "event": "exit-sl",
            "conditions": [
                {
                    "column": "signal",
                    "predicate": " == True",
                    "column_function": "get_sl_condition(row, posn)"
                }
            ]
        }),
        EventCondition({
            "event": "exit-target",
            "conditions": [
                {
                    "column": "signal",
                    "predicate": " == True",
                    "column_function": "get_sl_condition(row, posn)"
                }
            ]
        }),
    ]
    data = [{
        'time': 1.0,
        'open': 100.0,
        'high': 110.0,
        'low': 90.0,
        'close': 105.0,
        'signal': 0.0,
    }, {
        'time': 2.0,
        'open': 105.0,
        'high': 105.0,
        'low': 90.0,
        'close': 95.0,
        'signal': 1.0,
    }
    ]

    posn_data = '''{
        "0": {
            "sl": 110,
            "target": 95,
            "pos_quantity": 0,
            "traded_value": 0.75,
            "trade_list": [
                "Trade ID: 0, Order ID: 0, scrip: ABC, direction: SELL, quantity: 1 @ 283.0 on 2021-12-13 09:15:00+05:30",
                "Trade ID: 1, Order ID: 0, scrip: ABC, direction: SELL, quantity: -1 @ 282.25 on 2021-12-13 09:15:00+05:30"
            ],
            "trade_direction": "SELL"
        },
        "1": {
            "sl": 95,
            "target": 100,
            "pos_quantity": 0,
            "traded_value": -0.6000000000000227,
            "trade_list": [
                "Trade ID: 2, Order ID: 1, scrip: ABC, direction: BUY, quantity: 1 @ 280.95001 on 2021-12-14 09:15:00+05:30",
                "Trade ID: 3, Order ID: 1, scrip: ABC, direction: SELL, quantity: 1 @ 280.35001 on 2021-12-14 09:15:00+05:30"
            ],
            "trade_direction": "BUY"
        }
    }'''
    df = pd.DataFrame(data)
    df['index'] = df['time']
    df.set_index('index', inplace=True)
    for key, r in df.iterrows():
        x = e.eval(c, r, json.loads(posn_data))
        print(x)
