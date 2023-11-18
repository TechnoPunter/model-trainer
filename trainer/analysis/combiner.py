import datetime
import logging
import os
import shutil
import subprocess
from urllib.request import urlopen

import numpy as np
import pandas as pd
from commons.config.reader import cfg
from commons.dataprovider.database import DatabaseEngine
from commons.dataprovider.filereader import get_base_data
from commons.models import SlThresholds

from trainer.utils.EmailAlert import send_email

logger = logging.getLogger(__name__)

SYMBOL_MASTER = "https://api.shoonya.com/NSE_symbols.txt.zip"
SCRIP_MAP = {'BAJAJ_AUTO-EQ': 'BAJAJ-AUTO-EQ', 'M_M-EQ': 'M&M-EQ'}
TRADES_FILE = os.path.join(cfg['generated'], 'summary', 'Portfolio-Trades.csv')
PRED_FILE = os.path.join(cfg['generated'], 'summary', 'Portfolio-Pred.csv')
ACCURACY_FILE = os.path.join(cfg['generated'], 'summary', 'Portfolio-Accuracy.csv')
ACCURACY_COLS = ["scrip", "strategy", "entry_pct", "l_pct_success", "l_pct", "s_pct_success", "s_pct"]
MODEL_PREFIX = 'trainer.strategies.'


def calc_weight(row):
    return row['entry_pct'] * row['pct_success'] * row['pct_ret']


class Combiner:
    symbols = pd.DataFrame
    trader_db = DatabaseEngine

    def __init__(self):
        self.trader_db = DatabaseEngine()
        self.thresholds = self.__get_sl_thresholds()
        self.pred = pd.DataFrame()
        zip_file_name = 'NSE_symbols.zip'
        token_file_name = 'NSE_symbols.txt'

        # extracting zipfile from URL
        with urlopen(SYMBOL_MASTER) as response, open(zip_file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

            # extracting required file from zipfile
            command = 'unzip -o ' + zip_file_name
            subprocess.call(command, shell=True)

        # deleting the zipfile from the directory
        os.remove(zip_file_name)

        # loading data from the file
        self.symbols = pd.read_csv(token_file_name)
        os.remove(token_file_name)

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

    def __get_token(self, scrip):
        logger.debug(f"Getting token for {scrip}")
        scrip = SCRIP_MAP.get(scrip, scrip)
        return self.symbols.loc[self.symbols.TradingSymbol == scrip]['Token'].iloc[0]

    def __get_threshold(self, df) -> SlThresholds:
        logger.debug(f"Getting threshold for\n{df}")
        row = df.iloc[0]
        key = ":".join([row.scrip, str(row.signal), row.model])
        return self.thresholds.get(key)

    @staticmethod
    def __get_quantity(df: pd.DataFrame, capital: float):
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
        df = df.assign(weight=calc_weight)
        df = df.assign(pct_weight=(df['weight'] / df['weight'].sum()) * 100)
        df = df.assign(alloc=df['pct_weight'].mul(capital / 100))
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
                curr_df['token'] = self.__get_token(symbol)
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
            threshold = acct.get('threshold', cfg['steps']['threshold'])
            filter_pred = self.__apply_filter(threshold['min_pct_ret'], threshold['min_pct_success'])
            val = self.__get_quantity(filter_pred, cap)
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

    def __get_pred_with_accuracy(self, pred=pd.read_csv(PRED_FILE), accuracy=pd.read_csv(ACCURACY_FILE)):
        # if pred is None:
        #     pred = pd.read_csv(PRED_FILE)
        # if accuracy is None:
        #     accuracy = pd.read_csv(ACCURACY_FILE)
        df = pd.merge(pred, accuracy[ACCURACY_COLS], how="inner", left_on=["scrip", "model"],
                      right_on=["scrip", "strategy"])
        df["pct_success"] = df.apply(lambda row: row['l_pct_success'] if row['signal'] == 1 else row['s_pct_success'],
                                     axis=1)
        df["pct_ret"] = df.apply(lambda row: row['l_pct'] if row['signal'] == 1 else row['s_pct'], axis=1)
        df.drop(columns=['l_pct_success', 'l_pct', 's_pct_success', 's_pct'], axis=1, inplace=True)
        self.pred = df

    def weighted_backtest(self):
        """
        1. Read portfolio accuracy & trades
        2. Filter for % success & % return thresholds
        3. For trade day:
            a. Get weights
            b. Get quantities
            c. Plug in quantities to filtered trades
        4. Get Acct BT Results
        :return:
        """
        trades = pd.read_csv(TRADES_FILE)
        trades.rename(columns={"strategy": "model", "open": "close"}, inplace=True)
        # accuracy = pd.read_csv(ACCURACY_FILE)
        self.__get_pred_with_accuracy(pred=trades)
        for acct in cfg['steps']['accounts']:
            acct_trades = pd.DataFrame()
            key = acct['name']
            cap = acct['capital']
            threshold = acct.get('threshold', cfg['steps']['threshold'])
            filter_trades = self.__apply_filter(threshold['min_pct_ret'], threshold['min_pct_success'])
            for trade_dt in filter_trades.date.unique():
                val = self.__get_quantity(filter_trades.loc[filter_trades.date == trade_dt], cap)
                val = val.loc[val.quantity > 0]
                val.drop(columns=['model', 'trade_enabled', 'qty', 'margin', 'entry_pct', 'pct_success',
                                  'is_valid', 'pct_ret', 'weight', 'pct_weight', 'alloc', 'type', 'risk', ],
                         inplace=True)
                val['margin'] = val['entry_price'] * val['quantity']
                val['pnl'] = val['final_pnl'] * val['quantity']
                acct_trades = pd.concat([acct_trades, val])
            acct_trades.sort_values(by=['date', 'scrip'], inplace=True)
            acct_trades.to_csv(os.path.join(cfg['generated'], 'summary', key + '-BT-Trades.csv'), float_format='%.2f',
                               index=False)
        return "Done"


if __name__ == "__main__":
    c = Combiner()
    # res = c.combine_predictions()
    res = c.weighted_backtest()
    print(res)
