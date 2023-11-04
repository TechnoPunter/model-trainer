"""
Trade:
    Scrip
    Date
    Direction
    Qty
    Price
    Order ID
Trade Management:
    Buy
    Sell
    Get Position
Event Management:
    Hit SL
    Hit T1 #todo
    EOD
    Reversal #todo
    Trailng SL #todo

PML Calc:
    Get PNL
"""
import json
from typing import Dict

import pandas as pd
from tabulate import tabulate

from trainer.backtest.nova_event import EventManager, EventCondition
from trainer.backtest.nova_order import OrderBook
from trainer.backtest.nova_trades import TradeBook, Trade
from trainer.config.reader import cfg
from trainer.consts.consts import IST, GENERATED_DATA_PATH
import logging

logger = logging.getLogger(__name__)

TARGET_FACTOR = 1.5


class Nova:
    data: pd.DataFrame
    em: EventManager
    ec: Dict[int, list[EventCondition]]
    tb: TradeBook
    ob: OrderBook
    trade_id: int
    order_id: int
    quantity: int = 1
    scrip: str

    def __init__(self, scrip: str, pred_df: pd.DataFrame, tick_df: pd.DataFrame):
        """
        Read pred_data,
        Merge tick_data (if available)
        Create cob_entry column to indicate last bar of the day (could be the 1st bar for daily TF)

        Args:
            pred_df: Dataframe containing data with predictions.
                Needs to have Time(Epoch), OHLC, Signal, SL, T1, T2 columns
            tick_df: Dataframe containing symbol tick data (or any lower TF)
                Needs to have Time(Epoch), OHLC
        """
        logger.info(f"Initializing Nova for {scrip}")
        pred_cols = ["time", "signal", "target"]
        tick_cols = ["time", "open", "high", "low", "close"]

        self.cfg = cfg
        self.ob = OrderBook({})
        self.tb = TradeBook(self.ob)
        self.scrip = scrip

        self.trade_id = 0
        self.order_id = 0

        self.em = EventManager()
        self.ec = self.cfg['event-conditions']

        self.data = pd.merge(tick_df[tick_cols], pred_df[pred_cols], how="outer", left_on="time", right_on="time")
        self.data = self.data.set_index('time')
        self.data.sort_index(inplace=True)
        self.data.dropna(subset=['open'], inplace=True)
        self.data.reset_index(inplace=True)

        ############################################
        # Convert epoch values to datetime objects
        self.data['date'] = pd.to_datetime(self.data['time'], unit='s', utc=True)
        self.data['date'] = self.data['date'].dt.tz_convert(IST)

        # Set 'time' column as the index
        self.data.set_index('date', inplace=True)

        # Group by day
        grouped = self.data.groupby(pd.Grouper(freq='D'))

        # Determine the last row for each day
        last_rows = grouped.tail(1)

        # Create 'cob_entry' column and set value to 1 for the last row of each day
        self.data['cob_entry'] = 0
        self.data.loc[last_rows.index, 'cob_entry'] = 1

        self.data.reset_index(inplace=True)
        self.data.sort_values(by='time', inplace=True)

    def process_events(self, result_file_path: str = None, params: dict = None):
        """
        Logic:
            0. (__init__) : Load base + tick data
            1. For every row of data
                1. Get list of open orders (for event calc)
                2. Evaluate events --> EventManager.eval --> Returns Dict of events in priority order
                    Independent events: Do not depend on open orders e.g. Entry, Exit-COB, Update Maxes
                    Dependent events: Are in conjunction with other orders e.g. Hit-SL**, Hit-Target, Trail-SL
                            ** - SL is handled before target in case
                3. Handle events --> For each of the events form trade payload and call TradeBook.<m>
                    <m> --> Enter, Exit, Trail_SL
                    This internally also maintains the positions --> Open & Closed
                4. Extract the trades list from TradeBook.populate_trade_book & write to csv

        Args:
            result_file_path: Location to store the "Result" csv (Contains predictions, SL & Targets)
            params: Dict of other parameters for trailing SL etc.

        Returns: Dict - Trade List

        """
        tot = len(self.data)
        logger.info(f"Starting Nova for {self.scrip}: Total Recs: {tot}")
        rec = 0
        for key, row in self.data.iterrows():
            if (rec % 100) == 0:
                print(f"Percent: {round(rec * 100 / tot)} complete", end="\r")
            rec += 1

            for event_priority in self.ec:
                for key, event_conf_list in event_priority.items():
                    open_orders = self.ob.get_open_orders()
                    events = self.em.eval(event_conf_list, row, open_orders)
                    self.handle_events(events, row, params)
            self.tb.update_stats(row=row)

        trade_list = self.tb.populate_trade_book()
        if result_file_path is not None:
            pd.DataFrame(trade_list).to_csv(result_file_path, index=False, float_format='%.2f')
        logger.info(f"Results\n" + tabulate(trade_list, tablefmt="orgtbl", headers="keys", floatfmt=".2f"))
        logger.info(self.tb.get_pnl())
        return trade_list

    def handle_events(self, events: dict, row, params):
        for event, orders in events.items():
            if event == "entry-long":
                trade = f'''{{
                        "id": {self.trade_id},
                        "scrip": "{self.scrip}",
                        "direction": "BUY",
                        "quantity": {self.quantity},
                        "price": {row['open']},
                        "order_id": {self.order_id},
                        "time": {row['time']},
                        "event": "{event}"
                    }}'''
                entry_price = row['open']
                sl_range = float(params['sl']) * entry_price / 100
                sl_price = entry_price - sl_range
                if params.get('target', None) is None:
                    target_price = row['target']
                else:
                    target_range = float(params['target']) * entry_price / 100
                    target_price = entry_price + target_range
                trail_sl_price = entry_price * float(params['trail_sl']) / 100
                other_param_str = f'''{{
                        "sl_range": {sl_range},
                        "sl": {sl_price},
                        "trail_sl": {trail_sl_price},
                        "target": {target_price},
                        "anchor_price":  {entry_price}
                    }}'''
                other_params = json.loads(other_param_str)
                self.tb.enter(Trade(json.loads(trade)), other_params)
                self.trade_id += 1
                self.order_id += 1
            elif event == "entry-short":
                trade = f'''{{
                    "id": {self.trade_id},
                    "scrip": "{self.scrip}",
                    "direction": "SELL",
                    "quantity": {self.quantity},
                    "price": {row['open']},
                    "order_id": {self.order_id},
                    "time": {row['time']},
                    "event": "{event}"
                }}'''
                entry_price = row['open']
                sl_range = float(params['sl']) * entry_price / 100
                sl_price = entry_price + sl_range
                if params['target'] is None:
                    target_price = row['target']
                else:
                    target_range = float(params['target']) * entry_price / 100
                    target_price = entry_price - target_range
                trail_sl_price = entry_price * float(params['trail_sl']) / 100
                other_param_str = f'''{{
                        "sl_range": {sl_range},
                        "sl": {sl_price},
                        "trail_sl": {trail_sl_price},
                        "target": {target_price},
                        "anchor_price":  {entry_price}
                    }}'''
                other_params = json.loads(other_param_str)
                self.tb.enter(Trade(json.loads(trade)), other_params)
                self.trade_id += 1
                self.order_id += 1
            elif event == "exit-cob":
                for order_id, pos in self.tb.get_open_positions().items():
                    trade = f'''{{
                        "id": {self.trade_id},
                        "scrip": "{self.scrip}",
                        "direction": "EXIT",
                        "quantity": {abs(pos['pos_quantity'])},
                        "price": {row['close']},
                        "order_id": {order_id},
                        "time": {row['time']},
                        "event": "{event}"
                    }}'''
                    self.tb.exit(Trade(json.loads(trade)))
                    self.trade_id += 1
            elif event in ("exit-sl", "exit-target"):
                for order_id in orders:
                    order_list = self.ob.get_open_orders(order_id)
                    order = order_list[0]
                    trade = f'''{{
                                    "id": {self.trade_id},
                                    "scrip": "{order.scrip}",
                                    "direction": "EXIT",
                                    "quantity": {abs(order.quantity)},
                                    "price": {row['close']},
                                    "order_id": {order_id},
                                    "time": {row['time']},
                                    "event": "{event}"
                                }}'''
                    self.tb.exit(Trade(json.loads(trade)))
                    self.trade_id += 1
            elif event == "trail-sl":
                for order_id in orders:
                    self.tb.update_sl(order_id, row=row)


if __name__ == "__main__":
    from trainer.dataprovider.filereader import get_tick_data

    path = '../../generated/'
    pred_file = path + "trainer.strategies.gspcV2.NSE_RELIANCE_Result.csv"
    pred_data = pd.read_csv(pred_file)
    tick_data = get_tick_data("NSE_RELIANCE")
    result_file = "reliance_output.csv"

    n2 = Nova(scrip="NSE_RELIANCE", pred_df=pred_data, tick_df=tick_data)
    # print(n2.data)

    n = Nova(scrip="NSE_RELIANCE", pred_df=pred_data, tick_df=tick_data)
    # print(n.data)

    p = {
        "trail_sl": 0.1,
        "sl": 0.5,
        "target": 0.6
    }
    x = n.process_events(path + result_file, params=p)
    print(x)
