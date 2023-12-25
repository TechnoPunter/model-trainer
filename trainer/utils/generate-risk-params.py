import chevron
import pandas as pd
from commons.consts.consts import RF_ACCURACY_FILE

PATH = '../../resources/templates/risk-params.yaml'
MIN_PCT_RETURNS = 2.0


def get_scrip_config(data: dict):
    with open(PATH, 'r') as file:
        return chevron.render(file, data=data)


def form_trade_params(accuracy_data: pd.DataFrame = None):
    """
    :param accuracy_data - Portfolio-Reward-Factor-Accuracy.csv

    """
    l_count = 0
    s_count = 0
    results = ""
    curr_accuracy = accuracy_data.loc[
        accuracy_data.groupby(['scrip', 'strategy'])['trade_date'].transform(max) == accuracy_data['trade_date']]
    l_filter_data = curr_accuracy.loc[(curr_accuracy.l_pct_returns >= MIN_PCT_RETURNS)]
    for index, row in l_filter_data.iterrows():
        curr_dir = '1'
        params = {
            "scrip_name": row.scrip,
            "strategy": row.strategy,
            "direction": curr_dir,
            "reward_factor": round(row.l_reward_factor, 2)
        }
        l_count += 1
        results += get_scrip_config(params)
    s_filter_data = curr_accuracy.loc[(curr_accuracy.s_pct_returns >= MIN_PCT_RETURNS)]
    for index, row in s_filter_data.iterrows():
        curr_dir = '-1'
        params = {
            "scrip_name": row.scrip,
            "strategy": row.strategy,
            "direction": curr_dir,
            "reward_factor": round(row.s_reward_factor, 2)
        }
        s_count += 1
        results += get_scrip_config(params)
    return results, l_count, s_count


if __name__ == "__main__":
    rf_accu_df = pd.read_csv(RF_ACCURACY_FILE)
    res, l_cnt, s_cnt = form_trade_params(accuracy_data=rf_accu_df)
    print(res)
    print(f"Long: {l_cnt}")
    print(f"Short: {s_cnt}")
