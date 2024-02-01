import pandas as pd

from commons.utils.EmailAlert import send_email

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}


def send_df_email(df: pd.DataFrame, subject: str = '', acct: str = ''):
    return send_email(body=df.to_html(), subject=subject, acct=acct)


if __name__ == "__main__":
    x = send_email("Test Email")
    print(x)
    x = send_email("Test Email", subject="Test Subject", acct='Trader-V2-Pralhad')
    print(x)
    _data = {"a": ["a1", "a2"], "b": ["b1", "b2"]}
    data_df = pd.DataFrame(_data)
    x = send_df_email(data_df)
    print(x)
