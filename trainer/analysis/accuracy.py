import logging

import pandas as pd
from commons.backtest.fastBT import FastBT
from commons.config.reader import cfg
from commons.consts.consts import *
from commons.dataprovider.database import DatabaseEngine

logger = logging.getLogger(__name__)


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

    bt_trades, bt_stats, bt_mtm = f.run_accuracy(params_)
    bt_stats.to_csv(ACCURACY_FILE, float_format='%.2f', index=False)
    bt_trades.to_csv(TRADES_FILE, float_format='%.2f', index=False)
    for key, mtm_df in bt_mtm.items():
        if len(mtm_df) > 0:
            logger.info(f"Processing {key}")
            scrip, strategy = key.split(":")
            file = os.path.join(cfg['generated'], scrip, f'trainer.strategies.{strategy}.{scrip}_Raw_Trades_MTM.csv')
            mtm_df.to_csv(file, float_format='%.2f', index=False)
    return bt_stats


def load_mtm(trader_db: DatabaseEngine):
    """
    Reads the TRADES_MTM_FILE file
    Deletes & inserts MTM records into Trades_MTM table in Database
    :param:
    :return: None
    """
    for scrip_ in cfg['steps']['scrips']:
        for strategy_ in cfg['steps']['strats']:
            logger.info(f"Processing Scrip:{scrip_} & Strategy:{strategy_}")
            file = os.path.join(cfg['generated'], scrip_,
                                f'trainer.strategies.{strategy_}.{scrip_}_Raw_Trades_MTM.csv')
            df = pd.read_csv(file)
            if len(df) == 0:
                logger.error("Empty Trades MTM File")
            else:
                predicate = (f"m.{TRADES_MTM_TABLE}.scrip == '{scrip_}',"
                             f"m.{TRADES_MTM_TABLE}.strategy == 'trainer.strategies.{strategy_}'")
                trader_db.delete_recs(table=TRADES_MTM_TABLE, predicate=predicate)
                trader_db.bulk_insert(table=TRADES_MTM_TABLE, data=df)
                logger.info(f"Added {len(df)} records into Trades MTM Table")


if __name__ == "__main__":
    from commons.loggers.setup_logger import setup_logging

    setup_logging("accuracy.log")
    db = DatabaseEngine()
    x = run_accuracy(db)
    x.to_clipboard()
    load_mtm(db)
    print("Done")
