import pandas as pd

from commons.consts.consts import IST


def get_target(row):
    if row['close'] < row['next_close']:
        return 1
    else:
        return -1


def standard_prep(base_data: pd.DataFrame) -> pd.DataFrame:
    """
        Adding target Columns i.e. --> Move in next candle (Limiting to Intraday only)
        Columns
        Date Time
        Date
        Day Row No
        Next Close
    """

    df = base_data.copy()

    # Date Time
    df['datetime'] = pd.to_datetime(df['time'], unit='s', utc=True)
    df['datetime'] = df['datetime'].dt.tz_convert(IST)
    df.set_index('datetime', inplace=True)

    # Date
    df['date'] = df.index.date
    df['date'] = pd.to_datetime(df['date'])

    # Day Row No
    df['day_row_number'] = df.groupby(df.index.date).cumcount()

    # Row-over-row
    # Next Close
    df['next_close'] = df['close'].shift(-1)
    df['target'] = df.apply(get_target, axis=1, result_type='expand')

    return df
