import csv
import fnmatch
import logging
import os
from itertools import repeat
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandasql import sqldf

from trainer.config.reader import cfg
from trainer.trainer.results import Result

BASE_PATH = cfg['generated']
logger = logging.getLogger(__name__)
pd.options.mode.chained_assignment = None

TOT_PNL_PCT_CUTOFF = 1.0


def get_base_data(base_path: str, scrip: str, strats: [str], calc_base: bool = True) -> str:
    logger.info(f"About to process {scrip}")
    op_path = os.path.join(base_path, scrip, f'{scrip}-Summary.csv')
    if calc_base:
        r = Result()
        dfs = []
        for strat in strats:
            dfs.append(r.combine_results(path=os.path.join(base_path, scrip, "results", "predict.strategies." + strat),
                                         reg='*_PNL.csv'))
        df = pd.concat(dfs)
        logger.info(f"Combine Results: {len(df)}")
        if len(df) == 0:
            return ""

        query = """
        select
        scrip,
        model,
        strategy,
        dir,
        target_pct,
        sl_pct,
        trail_sl_pct,
        count(1) as cnt,
        sum(case when result = 'P' then 1 else 0 end) as p_cnt,
        avg(pricein) as avg_cost,
        sum(pnl) as tot_pnl,
        sum(case when outlier = True and pnl < 0 then abs(pnl) else 0 end) as outlier_l,
        sum(case when outlier = True and pnl > 0 then abs(pnl) else 0 end) as outlier_p
        from df
        group by
        scrip,
        model,
        strategy,
        dir,
        target_pct,
        sl_pct,
        trail_sl_pct
        """

        result_df = sqldf(query)
        cols = ['target_pct', 'sl_pct', 'trail_sl_pct', 'avg_cost', 'tot_pnl', 'outlier_l', 'outlier_p']
        result_df[cols] = result_df[cols].astype(float).apply(lambda x: np.round(x, decimals=2))
        result_df.to_csv(op_path)
    return op_path


def get_rank_data(base_path, base_df: pd.DataFrame, scrip: str) -> str:
    logger.info(f"Base DF: {len(base_df)}")
    rank_query = """
    select
    scrip,
    model,
    strategy,
    dir,
    target_pct,
    sl_pct,
    trail_sl_pct,
    cnt,
    p_cnt,
    p_cnt * 100 / cnt as p_ratio,
    tot_pnl,
    avg_cost,
    (tot_pnl * 100 / avg_cost) tot_pnl_pct,
    outlier_l,
    outlier_p,
    rank() over(partition by strategy, dir order by tot_pnl desc, target_pct asc, sl_pct asc, trail_sl_pct asc ) as rnk
    from base_df
    """

    result_df = sqldf(rank_query)

    min_value = result_df.groupby('dir')['tot_pnl'].min()
    max_value = result_df.groupby('dir')['tot_pnl'].max()
    range_value = max_value - min_value

    items = []
    for direction, _ in range_value.items():
        curr_df = result_df.loc[result_df.dir == direction]
        curr_df['normalized_tot_pnl'] = (curr_df['tot_pnl'] - min_value[direction]) / range_value[direction]
        items.append(curr_df)

    ranked_df = pd.concat(items)

    ranked_path = os.path.join(base_path, scrip, f'{scrip}-Rank.csv')
    cols = ['target_pct', 'sl_pct', 'trail_sl_pct', 'avg_cost', 'tot_pnl', 'tot_pnl_pct', 'outlier_l', 'outlier_p']
    ranked_df[cols] = ranked_df[cols].astype(float).apply(lambda x: np.round(x, decimals=2))
    ranked_df.to_csv(ranked_path)
    return ranked_path


def plot_image(rank_df: pd.DataFrame, dir: str = 'SELL'):
    df = rank_df.loc[(rank_df['dir'] == dir)]

    plot_df = sqldf("select sl_pct, trail_sl_pct, max(normalized_tot_pnl) as val from df group by trail_sl_pct, sl_pct")

    plot_df.to_clipboard()

    x = plot_df.sl_pct.unique()
    y = plot_df.trail_sl_pct.unique()

    X, Y = np.meshgrid(x, y)
    Z = plot_df.pivot(index='trail_sl_pct', columns='sl_pct', values='val')

    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection='3d')
    ax.grid()
    ax = plt.axes(projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
    ax.set_xlabel('sl_pct')
    ax.set_ylabel('trail_sl_pct')
    ax.set_zlabel('norm_pnl')

    plt.show()


def analyse_scrip(base_path, scrip_name, strats, render: bool = False, calc_base: bool = True):
    logger.info(f"Starting to analyse {scrip_name} for strats: {strats}")
    result_path = get_base_data(base_path, scrip_name, strats, calc_base)
    if result_path != "":
        result_df = pd.read_csv(result_path)
        rank_path = get_rank_data(base_path, result_df, scrip_name)
        if render:
            rank_df = pd.read_csv(rank_path)
            plot_image(rank_df)


def rank_results(base_path: str = BASE_PATH, opts: [str] = None):
    if opts is None:
        opts = ['run-ranking', 'run-summary']
    logger.info("Starting rank_results")
    scrips = cfg['steps']['scrips']
    strategies = cfg['steps']['strats']
    if 'run-ranking' in opts:
        with Pool(processes=2) as pool:
            for result in pool.starmap(analyse_scrip, zip(repeat(base_path), scrips, repeat(strategies))):
                # print(f'Got result: {result}', flush=True)
                pass
    if 'run-summary' in opts:
        dfs = []
        for scrip in scrips:
            dfs.append(pd.read_csv(os.path.join(cfg['generated'], scrip, scrip + '-Rank.csv')))

        df = pd.concat(dfs)
        rnk_df = df.loc[(df.rnk == 1) & (df.tot_pnl_pct > TOT_PNL_PCT_CUTOFF)]
        rnk_df.to_csv(os.path.join(cfg['generated'], 'summary', 'Portfolio-Rank.csv'), index=False, float_format='%.2f')
        sqls = ["DELETE FROM sl_thresholds;"]
        for _, row in rnk_df.iterrows():
            signal = 1 if row.dir == 'BUY' else -1
            strategy = row.strategy
            sqls.append(f"INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) "
                        f"VALUES ('{row.scrip}',{row.sl_pct},{signal},{row.trail_sl_pct},0.05,NULL,'{strategy}');")

        sql_df = pd.DataFrame(sqls)
        sql_df.to_csv(os.path.join(cfg['generated'], 'summary', 'Portfolio-Rank.sql'), index=False, header=False,
                      quoting=csv.QUOTE_MINIMAL)
        post_proc()


def post_proc():
    path = cfg['generated']
    reg = '*_PNL.csv'
    files = []
    for root, dirs, files_ in os.walk(path):
        for filename in fnmatch.filter(files_, reg):
            files.append(os.path.join(root, filename))
    df = pd.read_csv(os.path.join(cfg['generated'], 'summary', 'Portfolio-Rank.csv'))
    trades = []
    for _, row in df.iterrows():
        curr_df = pd.read_csv(fnmatch.filter(files, "*" + row.model)[0])
        curr_df = curr_df.loc[(curr_df.dir == row.dir)]
        curr_df[['model', 'target_pct', 'sl_pct', 'trail_sl_pct']] = row[
            ['model', 'target_pct', 'sl_pct', 'trail_sl_pct']]
        curr_df['trade_dttm'] = pd.to_datetime(curr_df['datein'])
        curr_df['trade_dt'] = curr_df['trade_dttm'].dt.date
        curr_df.drop(columns=['trade_dttm'], axis=1, inplace=True)
        trades.append(curr_df)

    final_trades = pd.concat(trades)
    final_trades.to_csv(os.path.join(cfg['generated'], 'summary', 'Portfolio-Trades.csv'), index=False,
                        float_format='%.2f')

    pivot_final_trades = """
    select 
    
    from final_trades
    """


if __name__ == "__main__":
    loc_base_path = BASE_PATH
    loc_opts = []
    loc_opts.append('run-ranking')
    loc_opts.append('run-summary')
    rank_results(loc_base_path, loc_opts)
    # scrip = 'NSE_APOLLOHOSP'
    # rank_results(base_path=loc_base_path, scrip_name=scrip, strats=['gspcV2'], calc_base=True, render=False)
    # rank_csv = os.path.join(loc_base_path, scrip, f'{scrip}-Rank.csv')
    # rank_df = pd.read_csv(rank_csv)
    # plot_image(rank_df, 'BUY')
