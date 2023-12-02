import datetime
import logging
import os

import numpy as np
import pandas as pd
from commons.broker.Shoonya import Shoonya
from commons.config.reader import cfg
from commons.consts.consts import IST
from commons.dataprovider.database import DatabaseEngine
from commons.dataprovider.filereader import get_base_data
from commons.loggers.setup_logger import setup_logging
from commons.models import SlThresholds

from trainer.utils.EmailAlert import send_email

logger = logging.getLogger(__name__)

SYMBOL_MASTER = "https://api.shoonya.com/NSE_symbols.txt.zip"
SCRIP_MAP = {'BAJAJ_AUTO-EQ': 'BAJAJ-AUTO-EQ', 'M_M-EQ': 'M&M-EQ'}
TRADES_FILE = os.path.join(cfg['generated'], 'summary', 'Portfolio-Trades.csv')
PRED_FILE = os.path.join(cfg['generated'], 'summary', 'Portfolio-Pred.csv')
ACCURACY_FILE = os.path.join(cfg['generated'], 'summary', 'Portfolio-Accuracy.csv')
ACCURACY_COLS = ["scrip", "strategy", "l_entry_pct", "l_pct_success", "l_pct", "s_entry_pct", "s_pct_success", "s_pct"]
QUANTITY_COLS = ["scrip", "model", "date", "quantity"]
MODEL_PREFIX = 'trainer.strategies.'


def calc_weight(row):
    weights = cfg.get('steps').get('weights', {"entry_pct": 1, "pct_success": 1, "pct_ret": 1})
    wt_entry_pct = weights['entry_pct']
    wt_pct_success = weights['pct_success']
    wt_pct_ret = weights['pct_ret']
    return wt_entry_pct * row['entry_pct'] * wt_pct_success * row['pct_success'] * wt_pct_ret * row['pct_ret']


def get_direction_pct(row):
    if row['signal'] == 1:
        return row['l_pct_success'], row['l_entry_pct'], row['l_pct']
    else:
        return row['s_pct_success'], row['s_entry_pct'], row['s_pct']


ACCT = 'Trader-V2-Pralhad'


class Combiner:
    symbols: pd.DataFrame
    trader_db: DatabaseEngine
    shoonya: Shoonya

    def __init__(self, trader_db: DatabaseEngine = None, shoonya: Shoonya = None):
        if trader_db is None:
            self.trader_db = DatabaseEngine()
        else:
            self.trader_db = trader_db
        if shoonya is None:
            self.shoonya = Shoonya(ACCT)
        else:
            self.shoonya = shoonya
        self.thresholds = self.__get_sl_thresholds()
        self.pred = pd.DataFrame()

    def __get_sl_thresholds(self):
        """
        Read all data from stop_loss_thresholds
        Returns: Dict { K: scrip + direction, V : sl, trail_sl}

        """
        result = {}
        recs = self.trader_db.query("SlThresholds", "1==1")
        for item in recs:
            result[":".join([item.scrip, str(item.direction), item.strategy])] = item
        return result

    def __get_threshold(self, df) -> SlThresholds:
        logger.debug(f"Getting threshold for\n{df}")
        row = df.iloc[0]
        key = ":".join([row.scrip, str(row.signal), row.model])
        return self.thresholds.get(key)

    @staticmethod
    def __get_quantity(df: pd.DataFrame, capital: float, cap_loading: float = 1.0):
        """

        Args:
            df: Following attributes
                type: Fixed or Risk_Per_Trade
                quantity: For "Fixed" --> return quantity
                risk: How much is at stake --> e.g. 5 (Rs. 5)
                sl_pct: SL Price --> e.g. 1.0 ( => 1%)
                close: Approx Entry level --> e.g. (Rs. 100)
                quantity: For "Risk_Per_Trade" -->
                    100 * 1% = 1 => SL Range
                    floor(5 / 1) = 5 => quantity

        Returns:
            {"quantity": quantity}
        """
        if len(df) == 0:
            return pd.DataFrame()

        if cap_loading is None:
            weights = cfg.get('steps').get('weights', {"cap_loading": 1.0})
            cap_loading = weights['cap_loading']
        eff_capital = capital * cap_loading
        df = df.assign(weight=calc_weight)
        df = df.assign(pct_weight=(df['weight'] / df['weight'].sum()) * 100)
        df = df.assign(alloc=df['pct_weight'].mul(eff_capital / 100))
        df = df.assign(type="Fixed", risk=0, quantity=lambda row: (row.alloc / row.close))
        df = df.assign(quantity=round(df.quantity, 0))
        df['quantity'] = df['quantity'].astype(int)
        return df

    @staticmethod
    def __validate():
        df = []
        # Get the latest record from Low TF Data
        for scrip in cfg['steps']['scrips']:
            scrip_data = get_base_data(scrip)
            scrip_data.loc[:, 'scrip'] = scrip
            last_row = scrip_data.iloc[[-1]]
            last_row.reset_index(inplace=True)
            df.append(last_row)
        row_data = pd.concat(df)
        row_data.drop_duplicates(inplace=True)
        epoch = row_data['time'].drop_duplicates()[0]
        row_date = datetime.datetime.utcfromtimestamp(epoch).replace(tzinfo=datetime.timezone.utc)
        if row_date.date() < datetime.datetime.today().date():
            return f"Base Data is as of {row_date}"
        else:
            return None

    def combine_predictions(self):
        """
        1. For each scrip & strategy
        2. Read the predictions from the Next Close file
        3. Combine with SL & Accuracy Thresholds
        4. Remove records below accuracy cutoff
        5. For each account
            a. Get Capital
            b. Get Allocation percent --> todo: Use a sophisticated mechanism
            c. Calculate Quantity
            d. Create final Entries file
        :return:
        """
        dfs = []
        for scrip_name in cfg['steps']['scrips']:
            logger.info(f"Processing {scrip_name}")
            for key in cfg['steps']['strats']:
                model = MODEL_PREFIX + key
                exchange = scrip_name.split("_")[0]
                symbol = scrip_name.replace(exchange + "_", "") + "-EQ"
                file = os.path.join(cfg['generated'], scrip_name, f'{model}.{scrip_name}_Next_Close.csv')
                curr_df = pd.read_csv(file)
                if len(curr_df) == 0:
                    logger.info(f"No records for {scrip_name} & {model} combination")
                    return
                curr_df = curr_df[['close', 'signal', 'target']]
                curr_df[['scrip', 'model']] = [[scrip_name, model]]
                curr_df[['exchange', 'symbol']] = [[exchange, symbol]]
                curr_df['token'] = self.shoonya.get_token(symbol)
                threshold = self.__get_threshold(curr_df)
                if threshold is not None:
                    curr_df[['target_pct', 'sl_pct', 'trail_sl_pct', 'tick']] = [
                        [threshold.target, threshold.sl, threshold.trail_sl, threshold.tick]]
                else:
                    curr_df[['target_pct', 'sl_pct', 'trail_sl_pct', 'tick']] = np.NaN
                dfs.append(curr_df)
        self.pred = pd.concat(dfs)
        self.pred.to_csv(PRED_FILE, float_format='%.2f', index=False)
        self.__get_pred_with_accuracy()
        for acct in cfg['steps']['accounts']:
            key = acct['name']
            cap = acct['capital']
            cap_loading = acct.get('cap_loading', None)
            threshold = acct.get('threshold', cfg['steps']['threshold'])
            filter_pred = self.__apply_filter(threshold['min_pct_ret'], threshold['min_pct_success'])
            val = self.__get_quantity(filter_pred, cap, cap_loading)
            val = val.loc[val.quantity > 0]
            val.drop(columns=["strategy", "entry_pct", "pct_success", "pct_ret", "weight", "pct_weight", "alloc"],
                     axis=1, inplace=True)
            val.to_csv(os.path.join(cfg['generated'], 'summary', key + '-Entries.csv'), index=False)

        val_res = self.__validate()
        if val_res is not None:
            send_email(body=f"Model Training Incomplete: {val_res}", subject="ERROR: Model Training")
        else:
            send_email(body="Model Training complete")
        return dfs

    def __apply_filter(self, min_pct_ret, min_pct_success):
        """
        1. Read Portfolio Accuracy file
        2. Join with today's Trade Entries
        3. Remove below threshold
        4. For each account
            a. Get Capital
            b. Get Allocation percent --> todo: Use a sophisticated mechanism
            c. Calculate Quantity
            d. Create final Entries file
        :return:
        """
        return self.pred.loc[(self.pred.pct_ret > min_pct_ret) & (self.pred.pct_success > min_pct_success)]

    def __get_pred_with_accuracy(self, pred: pd.DataFrame = None, accuracy: pd.DataFrame = None):
        if pred is None:
            pred = pd.read_csv(PRED_FILE)
        if accuracy is None:
            accuracy = pd.read_csv(ACCURACY_FILE)
        df = pd.merge(pred, accuracy[ACCURACY_COLS], how="inner", left_on=["scrip", "model"],
                      right_on=["scrip", "strategy"])
        df[["pct_success", "entry_pct", "pct_ret"]] = df.apply(get_direction_pct, axis=1, result_type='expand')
        df.drop(columns=['l_entry_pct', 'l_pct_success', 'l_pct', 's_entry_pct', 's_pct_success', 's_pct'], axis=1,
                inplace=True)
        self.pred = df

    @staticmethod
    def __prep_pred_data():
        res = []
        for scrip in cfg['steps']['scrips']:
            for strategy in cfg['steps']['strats']:
                file = os.path.join(cfg['generated'], scrip, f'trainer.strategies.{strategy}.{scrip}_Raw_Pred.csv')
                results = pd.read_csv(file)
                results = results[['target', 'signal', 'time']]
                results['time'] = results['time'].shift(-1)
                results['date'] = pd.to_datetime(results['time'], unit='s', utc=True)
                results['date'] = results['date'].dt.tz_convert(IST)
                results['date'] = results['date'].dt.date
                results['date'] = results['date'].astype(str)
                # Remove last row after offset of time
                results.dropna(subset=['date'], inplace=True)
                results = results.assign(scrip=scrip)
                results = results.assign(model=MODEL_PREFIX + strategy)
                res.append(results)
        return pd.concat(res)

    def weighted_backtest(self):
        """
        1. Read Portfolio Accuracy & Raw Predictions
        2. Filter for % success & % return thresholds
        3. For each day & account:
            a. Filter for % success & % return thresholds
            b. For the day's predictions - calculate weights & capital allocation
            c. Calculate quantities based on capital allocation
            d. Plug in quantities to trades [observe capital is idle since some trades are invalid at BOD]
            e. Get Acct BT Results
        :return:
        """
        trades = pd.read_csv(TRADES_FILE)
        trades.rename(columns={"strategy": "model", "open": "close"}, inplace=True)
        raw_pred_df = self.__prep_pred_data()
        raw_pred_df.rename(columns={"strategy": "model", "target": "close"}, inplace=True)
        self.__get_pred_with_accuracy(pred=raw_pred_df)

        for acct in cfg['steps']['accounts']:
            acct_trades = pd.DataFrame()
            key = acct['name']
            cap = acct['capital']
            cap_loading = acct.get('cap_loading', None)
            threshold = acct.get('threshold', cfg['steps']['threshold'])
            # Remove predictions not meeting threshold
            filter_pred_df = self.__apply_filter(threshold['min_pct_ret'], threshold['min_pct_success'])

            # Iterate through Trade Dates from filtered Predictions
            for trade_dt in filter_pred_df.date.unique():
                # Get Quantities
                qty_df = self.__get_quantity(filter_pred_df.loc[filter_pred_df.date == trade_dt], cap, cap_loading)
                curr_trades = trades.loc[trades.date == trade_dt]

                # Combine with trades
                val = pd.merge(curr_trades, qty_df[QUANTITY_COLS], how="inner",
                               left_on=["scrip", "model", "date"], right_on=["scrip", "model", "date"])
                val = val.loc[val.quantity > 0]
                val['margin'] = val['entry_price'] * val['quantity']
                val['pnl'] = val['target_pnl'] * val['quantity']

                # Append to results
                acct_trades = pd.concat([acct_trades, val])

            if len(acct_trades) > 0:
                # Prepare & Dump results
                acct_trades.sort_values(by=['date', 'scrip'], inplace=True)
                acct_trades.to_csv(os.path.join(cfg['generated'], 'summary', key + '-BT-Trades.csv'),
                                   float_format='%.2f', index=False)
                grouped = acct_trades[['date', 'pnl', 'margin']].groupby(['date'])
                pnl = grouped['pnl'].sum()
                margin = grouped['margin'].sum()
                peak_margin = margin.loc[margin > cap]
                print(
                    f"Account:{acct};\nResults: PNL: {format(pnl.sum(), '.2f')} "
                    f"Margin: {format(margin.mean(), '.2f')} "
                    f"Max Margin: {format(margin.max(), '.2f')}\n"
                    f"Peak Margin:\n{peak_margin}")
        return "Done"


if __name__ == "__main__":
    setup_logging("combiner.log")

    c = Combiner()
    res1 = c.combine_predictions()
    print("Done - Combine")
    res2 = c.weighted_backtest()
