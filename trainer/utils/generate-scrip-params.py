import os.path

import chevron
import pandas as pd

from commons.dataprovider.database import DatabaseEngine
from commons.config.reader import cfg

PATH = '../../resources/templates/scrip-trade-exec-params.yaml'
MODE = 'RANK'  # 'ACCURACY'
RANK_FILE_NAME = 'summary/Portfolio-Rank.csv'
ACCURACY_FILE_NAME = 'summary/Portfolio-Accuracy.csv'
MIN_PNL = 1
trader_db = DatabaseEngine()


def get_scrip_config(data: dict):
    with open(PATH, 'r') as file:
        return chevron.render(file, data=data)


def form_trade_params(mode: str, summary_data: pd.DataFrame = None):
    """
    res: summary_table
     --> scrip	model	dir	tot_pnl	avg_entry	pct_returns
    Returns:

    """
    results = ""
    if summary_data is None:
        summary_data = trader_db.run_query(cfg['postgres']['summary_table'])
    if len(summary_data) == 0:
        return results
    if mode == 'RANK':
        summary_data.sort_values(by=['scrip', 'dir', 'model'], inplace=True)
        filter_data = summary_data.loc[(summary_data.tot_pnl_pct >= MIN_PNL)]
        filter_data['strategy'] = filter_data['model'].apply(lambda model: model.split(".")[2])
    else:  # mode == 'ACCURACY'
        long_df = summary_data.loc[summary_data.l_cap_pct > (MIN_PNL / 100)]
        if len(long_df) > 0:
            long_df.insert(0, 'dir', 'BUY')
            filter_data = long_df
        else:
            filter_data = pd.DataFrame()
        short_df = summary_data.loc[summary_data.l_cap_pct > (MIN_PNL / 100)]
        if len(short_df) > 0:
            short_df.insert(0, 'dir', 'SELL')
            filter_data = pd.concat([filter_data, short_df])
    for index, row in filter_data.iterrows():
        params = {
            "scrip_name": row.scrip,
            "strategy": row.strategy,
            "direction": row.dir
        }
        results += get_scrip_config(params)
    return results


if __name__ == "__main__":
    # d = {
    #     "scrip_name": "NSE_BANDHANBNK",
    #     "strategy": "gspc",
    #     "direction": "SELL"
    # }
    # res = get_scrip_config(d)
    # print(res)
    # MODE = 'RANK'
    MODE = 'ACCURACY'

    if MODE == 'RANK':
        file = os.path.join(cfg['generated'], RANK_FILE_NAME)
    else:  # MODE == 'ACCURACY'
        file = os.path.join(cfg['generated'], ACCURACY_FILE_NAME)
    df = pd.read_csv(file)
    res = form_trade_params(mode=MODE, summary_data=df)
    print(res)
