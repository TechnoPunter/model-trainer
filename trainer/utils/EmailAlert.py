import pandas as pd
import requests

from commons.config.reader import cfg

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}


def send_email(body: str, subject: str = '', acct: str = ''):
    subject = f'[Trader V3 Alert]' if subject == '' else '[Trader V3 Alert]: ' + subject
    if acct == '':
        recipients = cfg['email']['recipients']
    else:
        recipients = cfg['email']['acct-recipient'].get(acct, 'pro.kamath%40gmail.com')
    data = f"email={recipients}&subject={subject}&body={body}"
    response = requests.request("POST", cfg['email']['url'], headers=headers, data=data)
    return response


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
