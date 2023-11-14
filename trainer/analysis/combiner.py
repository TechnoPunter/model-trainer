import datetime
import logging
import math
import os
import shutil
import subprocess
from urllib.request import urlopen

import numpy as np
import pandas as pd
from commons.models import SlThresholds

from commons.config.reader import cfg
from commons.dataprovider.database import DatabaseEngine
from commons.dataprovider.filereader import get_base_data
from trainer.utils.EmailAlert import send_email

logger = logging.getLogger(__name__)

SYMBOL_MASTER = "https://api.shoonya.com/NSE_symbols.txt.zip"
SCRIP_MAP = {'BAJAJ_AUTO-EQ': 'BAJAJ-AUTO-EQ', 'M_M-EQ': 'M&M-EQ'}


class Combiner:
    symbols = pd.DataFrame
    trader_db = DatabaseEngine

    def __init__(self):
        self.trader_db = DatabaseEngine()
        self.thresholds = self.__get_sl_thresholds()
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
    def __get_quantity(df: pd.DataFrame):
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
        row = df.iloc[0]
        if row.type == "Fixed":
            return row.quantity
        elif row.type == "Risk_Per_Trade":
            sl_range = row.close * float(row.sl_pct / 100)
            return math.floor(row.risk / sl_range)

    @staticmethod
    def __validate():
        df = []
        # Get the latest record from Low TF Data
        for scrip in cfg['trade-exec-params']['scrips']:
            scrip_data = get_base_data(scrip['scripName'])
            scrip_data.loc[:, 'scrip'] = scrip['scripName']
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
        dfs = {}
        for scrip in cfg['trade-exec-params']['scrips']:
            scrip_name = scrip['scripName']
            logger.info(f"Processing {scrip_name}")
            model = scrip['models'][0]['name']
            exchange = scrip_name.split("_")[0]
            symbol = scrip_name.replace(exchange + "_", "") + "-EQ"
            file = os.path.join(cfg['generated'], scrip_name, f'{model}.{scrip_name}_Next_Close.csv')
            curr_df = pd.read_csv(file)
            if len(curr_df) == 0:
                logger.info(f"No records for {scrip_name} & {model} combination")
                return
            if curr_df['signal'].iloc[0] == (1 if scrip['models'][0]['direction'] == 'BUY' else -1):
                logger.debug(f"Valid record for {scrip_name} & {model} combination in {curr_df['signal']} direction")
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
                for acct in scrip['accounts']:
                    name = acct['name']
                    acct_df = curr_df.join(pd.DataFrame([acct['quantity-params']]))
                    qty = self.__get_quantity(acct_df)
                    if qty > 0:
                        acct_df['quantity'] = qty
                        dfs[name] = pd.concat([dfs.get(name, pd.DataFrame()), acct_df])
        for key, val in dfs.items():
            val.to_csv(os.path.join(cfg['generated'], 'summary', key + '-Entries.csv'), index=False)

        val_res = self.__validate()
        if val_res is not None:
            send_email(body=f"Model Training Incomplete: {val_res}", subject="ERROR: Model Training")
        else:
            send_email(body="Model Training complete")
        return dfs


if __name__ == "__main__":
    import predict.loggers.setup_logger

    c = Combiner()
    res = c.combine_predictions()
    print(res)
