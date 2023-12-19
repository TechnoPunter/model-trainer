from datetime import datetime, timezone, timedelta

import pandas as pd


def get_filtered_df(df: pd.DataFrame, cfg, type: str) -> (int, int):

    filter_cfg = cfg['training'][type]

    if filter_cfg.get('split-type') == "fixed_date":
        low_dt = filter_cfg['low-dt']

        # Convert the date string to a datetime object
        date_obj = datetime.strptime(low_dt, "%Y-%m-%d")

        # Convert the datetime object to an epoch timestamp
        epoch_timestamp = int(date_obj.replace(tzinfo=timezone.utc).timestamp())
        filtered_df = df[df['time'] > epoch_timestamp]
    elif filter_cfg.get('split-type') == "fixed_days":
        num_days = filter_cfg['num-days']
        start_date = datetime.today() - timedelta(days=num_days)
        epoch_timestamp = int(start_date.replace(tzinfo=timezone.utc).timestamp())
        filtered_df = df[df['time'] >= epoch_timestamp]
    else:
        total = len(df)
        runs = round(total * filter_cfg['split-pct'])
        filtered_df = df.iloc[runs:]

    return filtered_df


def get_runs_count(df, cfg) -> (int, int):
    f_df = get_filtered_df(df, cfg, type="test")
    return len(df), len(f_df)



