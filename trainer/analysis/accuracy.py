import glob
import os

import numpy as np
import pandas as pd
from commons.config.reader import cfg
from commons.consts.consts import IST
from commons.dataprovider.filereader import get_tick_data, get_base_data


def get_target_pnl(row):
    if pd.isnull(row['target_candle']):
        return 0
    else:
        return abs(row['open'] - row['target'])


def get_final_pnl(row):
    return row['target_pnl'] * row['qty']


def get_eod_pnl(row):
    if row['target_pnl'] != 0:
        return row['target_pnl']
    elif row['signal'] == 1:
        return row['day_close'] - row['open']
    else:
        return row['open'] - row['day_close']


def is_valid(row):
    if (row['signal'] == 1 and row['target'] > row['open']) or \
            (row['signal'] == -1 and row['target'] < row['open']):
        return True
    else:
        return False


def target_met(row):
    if (row['curr_signal'] == 1 and row['curr_target'] <= row['high']) or \
            (row['curr_signal'] == -1 and row['curr_target'] >= row['low']):
        return True
    else:
        return False


def calc_mtm(row):
    if row['curr_signal'] == 1:
        return row['high'] - row['entry_price']
    elif row['curr_signal'] == -1:
        return row['entry_price'] - row['low']


def get_accuracy(strategy: str, scrip: str, trade_exec_params: list):
    l_trade = False
    s_trade = False
    l_qty = 1
    s_qty = 1
    for param in trade_exec_params:
        if param.get('models')[0].get('name').split('.')[2] == strategy:
            if param.get('models')[0].get('direction') == 'BUY':
                l_trade = True
                qty_params = param.get('accounts')[0].get('quantity-params')
                if qty_params.get('type') == 'Fixed':
                    l_qty = qty_params.get('quantity')
                else:
                    l_qty = 1
            elif param.get('models')[0].get('direction') == 'SELL':
                s_trade = True
                qty_params = param.get('accounts')[0].get('quantity-params')
                if qty_params.get('type') == 'Fixed':
                    s_qty = qty_params.get('quantity')
                else:
                    s_qty = 1

    file = os.path.join(cfg['generated'], scrip, f'trainer.strategies.{strategy}.{scrip}_Raw_Pred.csv')
    results = pd.read_csv(file)

    results = results[['target', 'signal', 'time']]
    results['time'] = results['time'].shift(-1)
    results['date'] = pd.to_datetime(results['time'], unit='s', utc=True)
    results['date'] = results['date'].dt.tz_convert(IST)
    results['date'] = results['date'].dt.date
    # Remove last row after offset of time
    results.dropna(subset=['date'], inplace=True)

    tick_data = get_tick_data(scrip)
    base_data = get_base_data(scrip)
    base_data = base_data[['time', 'close']]
    base_data.rename(columns={"close": "day_close"}, inplace=True)
    merged_df = pd.merge(tick_data, results, how='left', left_on='time', right_on='time')
    merged_df['datetime'] = pd.to_datetime(merged_df['time'], unit='s', utc=True)
    merged_df['datetime'] = merged_df['datetime'].dt.tz_convert(IST)
    merged_df['date'] = merged_df['datetime'].dt.date
    merged_df.set_index('datetime', inplace=True)
    merged_df = pd.merge(merged_df, base_data, how='left', left_on='time', right_on='time')

    # Remove 1st Row since we don't have closing from T-1
    merged_df = merged_df.iloc[1:]

    merged_df['is_valid'] = merged_df.apply(is_valid, axis=1)
    merged_df['entry_price'] = merged_df['open'][merged_df['is_valid']]
    merged_df['entry_price'] = merged_df['entry_price'].ffill()

    # Check if signal is valid i.e. Direction has travel at SOD
    valid_df = merged_df.loc[merged_df.is_valid]
    valid_df.set_index('date', inplace=True)

    # Remove invalid day rows
    merged_df = merged_df[merged_df.date.isin(valid_df.index)]

    merged_df['curr_target'] = merged_df['target'].ffill()
    merged_df['curr_signal'] = merged_df['signal'].ffill()

    merged_df['mtm'] = merged_df.apply(calc_mtm, axis=1)
    merged_df['target_met'] = merged_df.apply(target_met, axis=1)

    target_met_df = merged_df[merged_df['target_met']].groupby('date').apply(lambda x: x['target_met'].idxmin())
    mtm_max_df = merged_df.groupby('date').apply(lambda x: x['mtm'].max())

    final_df = pd.merge(valid_df, pd.DataFrame(target_met_df), how='left', left_index=True, right_index=True)
    final_df.rename({0: 'target_candle'}, axis=1, inplace=True)
    final_df = pd.merge(final_df, pd.DataFrame(mtm_max_df), how='left', left_index=True, right_index=True)
    final_df.rename({0: 'max_mtm'}, axis=1, inplace=True)

    final_df['target_pnl'] = final_df.apply(get_target_pnl, axis=1)
    final_df['target_pnl'] = final_df.apply(get_eod_pnl, axis=1)
    final_df['strategy'] = strategy
    final_df = final_df.assign(trade_enabled=False)
    final_df.loc[final_df.signal == 1, 'trade_enabled'] = l_trade
    final_df.loc[final_df.signal == 1, 'qty'] = l_qty
    final_df.loc[final_df.signal == -1, 'trade_enabled'] = s_trade
    final_df.loc[final_df.signal == -1, 'qty'] = s_qty
    final_df['final_pnl'] = final_df.apply(get_final_pnl, axis=1)
    final_df.drop(columns=['high', 'low', 'close'], axis=1, inplace=True)

    pct_success = 0
    tot_pnl = 0
    tot_avg_cost = 0.01
    l_trades = 0
    l_pct_success = 0
    l_pnl = 0
    l_avg_cost = 0.01
    s_trades = 0
    s_pct_success = 0
    s_pnl = 0
    s_avg_cost = 0.01

    if len(final_df) > 0:
        pct_success = (final_df['target_candle'].notna().sum() / len(final_df)) * 100
        tot_pnl = final_df['final_pnl'].sum()
        tot_avg_cost = final_df['entry_price'].mean()
        print(f"For {scrip} using {strategy}: No. of trades: {len(final_df)} "
              f"with {format(pct_success, '.2f')}% Accuracy "
              f"& PNL {format(tot_pnl, '.2f')}")
        l_trades = final_df.loc[final_df.signal == 1]
        if len(l_trades) > 0:
            l_pct_success = (l_trades['target_candle'].notna().sum() / len(l_trades)) * 100
            l_avg_cost = l_trades['entry_price'].mean()
            l_pnl = l_trades['final_pnl'].sum()
            print(f"For {scrip} using {strategy}: Long: No. of trades: {len(l_trades)} "
                  f"with {format(l_pct_success, '.2f')}% Accuracy "
                  f"& PNL {format(l_pnl, '.2f')}")
        s_trades = final_df.loc[final_df.signal == -1]
        if len(s_trades) > 0:
            s_pct_success = (s_trades['target_candle'].notna().sum() / len(s_trades)) * 100
            s_pnl = s_trades['final_pnl'].sum()
            s_avg_cost = s_trades['entry_price'].mean()
            print(f"For {scrip} using {strategy}: Short: No. of trades: {len(s_trades)} "
                  f"with {format(s_pct_success, '.2f')}% Accuracy "
                  f"& PNL {format(s_pnl, '.2f')}")
        cols = ["open", "day_close", "target", "entry_price", "max_mtm", "target_pnl", "final_pnl"]
        final_df[cols] = final_df[cols].astype(float).apply(lambda x: np.round(x, decimals=2))
        final_df.to_csv(os.path.join(cfg['generated'], scrip, f'trainer.strategies.{strategy}.{scrip}_Raw_Trades.csv'))

    return {
        "scrip": scrip, "strategy": strategy, "trades": len(final_df),
        "pct_success": pct_success, "tot_pnl": tot_pnl, "tot_avg_cost": tot_avg_cost,
        "l_trades": len(l_trades), "l_pct_success": l_pct_success, "l_pnl": l_pnl, "l_avg_cost": l_avg_cost,
        "l_cap_pct": l_pnl / (l_avg_cost * 0.2), "l_qty": l_qty,
        "s_trades": len(s_trades), "s_pct_success": s_pct_success, "s_pnl": s_pnl, "s_avg_cost": s_avg_cost,
        "s_cap_pct": s_pnl / (s_avg_cost * 0.2), "s_qty": s_qty,
    }


def combine_results(scrip: str):
    dfs = []
    files = glob.glob(os.path.join(cfg['generated'], scrip, f'trainer.strategies.*.{scrip}_Raw_Trades.csv'))
    for file in files:
        dfs.append(pd.read_csv(file))

    result_set = pd.concat(dfs)
    result_set.sort_values(by="date", inplace=True)
    result_set.to_csv(os.path.join(cfg['generated'], scrip, f'Combined.{scrip}_Raw_Trades.csv'))
    result_set.insert(0, 'scrip', scrip)
    return result_set


def run_accuracy():
    res = []
    scrip_trades = []
    params = cfg['trade-exec-params']['scrips']
    for scrip in cfg['steps']['scrips']:
        trade_params = []
        for trade_param in params:
            if trade_param.get('scripName') == scrip:
                trade_params.append(trade_param)
        for strategy in cfg['steps']['strats']:
            res.append(get_accuracy(strategy=strategy, scrip=scrip, trade_exec_params=trade_params))
        scrip_trades.append(combine_results(scrip))
    result = pd.DataFrame(res)
    result_trades = pd.concat(scrip_trades)
    result_path = os.path.join(cfg['generated'], 'summary', "Portfolio-Accuracy.csv")
    result_trades_path = os.path.join(cfg['generated'], 'summary', "Portfolio-Trades.csv")
    result.to_csv(result_path, float_format='%.2f', index=False)
    result_trades.sort_values(by=['date', 'scrip'], inplace=True)
    result_trades.to_csv(result_trades_path, float_format='%.2f', index=False)
    return result


if __name__ == "__main__":
    x = run_accuracy()
    x.to_clipboard()
