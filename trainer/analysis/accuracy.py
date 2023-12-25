import logging

import pandas as pd
from commons.backtest.fastBT import FastBT
from commons.config.reader import cfg
from commons.consts.consts import *
from commons.dataprovider.ScripData import ScripData
from commons.dataprovider.database import DatabaseEngine

logger = logging.getLogger(__name__)


def run_prep_data(scrip_data: ScripData = None, exec_mode: str = "SERVER"):
    f = FastBT(risk_mode="DEFAULT", scrip_data=scrip_data, exec_mode=exec_mode)
    params = []
    for scrip_ in cfg['steps']['scrips']:
        for strategy_ in cfg['steps']['strats']:
            file = str(os.path.join(cfg['generated'], scrip_, f'trainer.strategies.{strategy_}.{scrip_}_Raw_Pred.csv'))
            raw_pred_df_ = pd.read_csv(file)
            merged_df = f.prep_data(scrip=scrip_, strategy=MODEL_PREFIX + strategy_, raw_pred_df=raw_pred_df_,
                                    sd=scrip_data)
            params.append({"scrip": scrip_, "strategy": MODEL_PREFIX + strategy_, "merged_df": merged_df})
    return params


def run_base_accuracy(params: list[dict], scrip_data: ScripData = None, exec_mode: str = "SERVER"):
    if not os.path.exists(SUMMARY_PATH):
        os.makedirs(SUMMARY_PATH)

    f = FastBT(risk_mode="DEFAULT", scrip_data=scrip_data, exec_mode=exec_mode)
    bt_trades, bt_stats, bt_mtm = f.run_accuracy(params)

    bt_stats.to_csv(BASE_ACCURACY_FILE, float_format='%.2f', index=False)
    bt_trades.to_csv(BASE_TRADES_FILE, float_format='%.2f', index=False)

    for key, mtm_df in bt_mtm.items():
        if len(mtm_df) > 0:
            logger.info(f"Processing {key}")
            scrip, strategy = key.split(":")
            file = os.path.join(cfg['generated'], scrip, f'{strategy}.{scrip}_Base_Raw_Trades_MTM.csv')
            mtm_df.to_csv(file, float_format='%.2f', index=False)
    return bt_stats


def run_rf_accuracy(params: list[dict], scrip_data: ScripData = None, exec_mode: str = "SERVER"):
    if not os.path.exists(SUMMARY_PATH):
        os.makedirs(SUMMARY_PATH)
    accu_df = pd.read_csv(BASE_ACCURACY_FILE)

    f = FastBT(accuracy_df=accu_df, scrip_data=scrip_data, exec_mode=exec_mode)
    bt_trades, bt_stats, bt_mtm = f.run_accuracy(params)

    bt_stats.to_csv(RF_ACCURACY_FILE, float_format='%.2f', index=False)
    bt_trades.to_csv(RF_TRADES_FILE, float_format='%.2f', index=False)

    for key, mtm_df in bt_mtm.items():
        if len(mtm_df) > 0:
            logger.info(f"Processing {key}")
            scrip, strategy = key.split(":")
            file = os.path.join(cfg['generated'], scrip, f'{strategy}.{scrip}_RF_Raw_Trades_MTM.csv')
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
            file = str(os.path.join(cfg['generated'], scrip_,
                                    f'trainer.strategies.{strategy_}.{scrip_}_RF_Raw_Trades_MTM.csv'))
            df = pd.read_csv(file)
            if len(df) == 0:
                logger.error("Empty Trades MTM File")
            else:
                predicate = (f"m.{TRADES_MTM_TABLE}.scrip == '{scrip_}',"
                             f"m.{TRADES_MTM_TABLE}.strategy == 'trainer.strategies.{strategy_}',"
                             f"m.{TRADES_MTM_TABLE}.acct == 'Backtesting'")
                trader_db.delete_recs(table=TRADES_MTM_TABLE, predicate=predicate)
                df = df.assign(acct='Backtesting')
                df.fillna(0, inplace=True)
                trader_db.bulk_insert(table=TRADES_MTM_TABLE, data=df)
                logger.info(f"Added {len(df)} records into Trades MTM Table")


if __name__ == "__main__":
    from commons.loggers.setup_logger import setup_logging

    setup_logging("accuracy.log")
    db = DatabaseEngine()
    # x = run_accuracy(db)
    # x.to_clipboard()
    load_mtm(db)
    print("Done")
