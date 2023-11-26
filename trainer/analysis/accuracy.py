import os

import pandas as pd
from commons.backtest.fastBT import FastBT
from commons.config.reader import cfg
from commons.dataprovider.database import DatabaseEngine
from commons.loggers.setup_logger import setup_logging

SUMMARY_PATH = os.path.join(cfg['generated'], 'summary')
ACCURACY_FILE = os.path.join(SUMMARY_PATH, 'Portfolio-Accuracy.csv')
TRADES_FILE = os.path.join(SUMMARY_PATH, 'Portfolio-Trades.csv')


def run_accuracy(trader_db: DatabaseEngine):
    if not os.path.exists(SUMMARY_PATH):
        os.makedirs(SUMMARY_PATH)
    f = FastBT(trader_db=trader_db)
    params_ = []
    for scrip_ in cfg['steps']['scrips']:
        for strategy_ in cfg['steps']['strats']:
            file = os.path.join(cfg['generated'], scrip_, f'trainer.strategies.{strategy_}.{scrip_}_Raw_Pred.csv')
            raw_pred_df_ = pd.read_csv(file)
            params_.append({"scrip": scrip_, "strategy": strategy_, "raw_pred_df": raw_pred_df_})

    bt_trades, bt_stats = f.run_accuracy(params_)
    bt_stats.to_csv(ACCURACY_FILE, float_format='%.2f', index=False)
    bt_trades.to_csv(TRADES_FILE, float_format='%.2f', index=False)
    return bt_stats


if __name__ == "__main__":
    setup_logging("accuracy.log")
    db = DatabaseEngine()
    x = run_accuracy(db)
    x.to_clipboard()
