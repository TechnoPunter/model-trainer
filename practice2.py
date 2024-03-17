#%% imports
import numpy as np
import pandas as pd
import pytz
from backtesting.lib import plot_heatmaps
from ta.trend import ema_indicator
from ta.volatility import AverageTrueRange, bollinger_hband, bollinger_lband, bollinger_mavg, bollinger_hband_indicator, bollinger_lband_indicator
from backtesting import Strategy
from backtesting import Backtest
from tqdm import tqdm

#%%
IST = pytz.timezone('Asia/Kolkata')
tqdm.pandas()
df = pd.read_csv("1min_Bandhan_1Nov12Dec.csv")
# %% resample 1 min OHLC to 5 min OHLC
df['time'] = pd.to_datetime(df['time'], unit='s', utc=True).dt.tz_convert(IST)
df.set_index('time', inplace=True)
#%%
df = df.resample('5min').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last'
}).dropna()
#%%
df.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close'
}, inplace=True)
#%%
df.to_csv('final_1min_Bandhan_1Nov12Dec')
#%%
df = pd.read_csv('final_bc1_sd2')
# %% Backtesting
def ema_signal(ema_slow, ema_fast):
    ema_diff = ema_fast - ema_slow
    trend = np.where(ema_diff > 0, 2, 0)
    trend = np.where(ema_diff < 0, 1, trend)

    return trend.astype(int)
def total_signal(ema_signal, BBLI, BBHI):
    buy_signal = np.logical_and(ema_signal == 2, BBLI == 1)
    sell_signal = np.logical_and(ema_signal == 1, BBHI == 1)
    final_signal = np.where(buy_signal, 2, 0)
    final_signal = np.where(sell_signal, 1, final_signal)

    return final_signal.astype(int)
class MyStrat(Strategy):
    slow_window = 65
    fast_window = 25
    ATR_window = 1
    BB_window = 16
    SD = 2
    slcoef = 4.2
    TPSLRatio = 1.5
    # rsi_length = 16
    def init(self):
        # self.signal = self.I(SIGNAL)
        self.ema_slow = self.I(ema_indicator, self.data.Close.s, self.slow_window).round(2)
        self.ema_fast = self.I(ema_indicator, self.data.Close.s, self.fast_window).round(2)
        self.ema_signal = self.I(ema_signal, self.ema_slow, self.ema_fast)
        self.ATR = AverageTrueRange(high=self.data.High.s, low=self.data.Low.s, close=self.data.Close.s,
                                    window=self.ATR_window).average_true_range().round(2)
        self.BBU = self.I(bollinger_hband, self.data.Close.s, self.BB_window, self.SD).round(2)
        self.BBM = self.I(bollinger_mavg, self.data.Close.s, self.BB_window, self.SD).round(2)
        self.BBL = self.I(bollinger_lband, self.data.Close.s, self.BB_window, self.SD).round(2)
        self.BBLI = self.I(bollinger_lband_indicator, self.data.Close.s, self.BB_window, self.SD, plot=False)
        self.BBHI = self.I(bollinger_hband_indicator, self.data.Close.s, self.BB_window, self.SD, plot=False)
        self.total_signal = self.I(total_signal, self.ema_signal, self.BBLI, self.BBHI)
        # df['RSI']=ta.rsi(df.Close, length=self.rsi_length)
    def next(self):
        slatr = self.slcoef * self.ATR[-1]
        if self.total_signal == 2:
            stop_loss = self.data.Close[-1] - slatr
            target = self.data.Close[-1] + (slatr * self.TPSLRatio)
            self.buy(sl=stop_loss, tp=target)
        elif self.total_signal == 1:
            stop_loss = self.data.Close[-1] + slatr
            target = self.data.Close[-1] - (slatr * self.TPSLRatio)
            self.sell(sl=stop_loss, tp=target)
bt = Backtest(df, MyStrat, cash=10000, margin=1 / 3.12, exclusive_orders=True)
stats = bt.run()
print(stats)
bt.plot()

#%%
stats['_trades'].to_csv('trades_1min_Bandhan_1Nov12Dec')

#%% Optimize ATR
stats = bt.optimize(ATR_window=range(1, 20, 1), maximize='Equity Final [$]')
print(stats._strategy)
#%% Optimize EMA
stats = bt.optimize(fast_window=range(5, 30, 5),
                    slow_window=range(10, 70, 5),
                    maximize='Equity Final [$]',
                    constraint=lambda param: param.fast_window < param.slow_window)
print(stats._strategy)
#%% Optimize BB window
stats = bt.optimize(BB_window=range(1, 50, 1), maximize='Equity Final [$]')
print(stats._strategy)
#%% Optimize SD
stats = bt.optimize(SD=range(0, 10, 1), maximize='Equity Final [$]')
print(stats._strategy)

#%% Optimize slcoef
stats = bt.optimize(slcoef=np.arange(0.1, 10.0, 0.1).tolist(), maximize='Equity Final [$]', return_heatmap=True)
plot_heatmaps(stats[1])
print(stats._strategy)

#%% Optimize TPSLRatio
stats = bt.optimize(TPSLRatio=np.arange(0.1, 10.0, 0.1).tolist(), maximize='Equity Final [$]')
print(stats._strategy)