import backtrader as bt
import pandas as pd
import pytz
from backtrader import feeds as btfeeds, Order

from trainer.backtest.nova import Nova


# adding lines for calculated fields
class CustomDataLoader(btfeeds.PandasData):
    lines = ('time', 'curr_signal', 'curr_target', 'next_cob_entry',)
    params = (('time', 0),
              ('next_cob_entry', 5),
              ('curr_target', 6),
              ('curr_signal', 7)
              )
    datafields = btfeeds.PandasData.datafields + (['time', 'curr_signal', 'curr_target', 'next_cob_entry'])


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Grab all attributes needed for processing
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_close = self.datas[0].close
        self.data_time = self.datas[0].time
        self.data_signal = self.datas[0].curr_signal
        self.data_target = self.datas[0].curr_target
        self.data_cob_entry = self.datas[0].next_cob_entry
        self.trade_id = 0
        self.params = pd.DataFrame()

        # To keep track of pending orders
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                self.params.loc[order.params.tradeid, 'buy_price'] = order.executed.price
                self.params.loc[order.params.tradeid, 'buy_time'] = self.datas[0].datetime.datetime(0)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
                self.params.loc[order.params.tradeid, 'sell_price'] = order.executed.price
                self.params.loc[order.params.tradeid, 'sell_time'] = self.datas[0].datetime.datetime(0)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # self.log(f"{self.data_signal[0]} for {self.data_target[1]} > {self.data_open[1]} ep: {self.data_time[1]}")

        # Check if we are in the market
        if not self.position:

            if self.data_signal[0] == 1:
                # self.log(f"Validating {self.data_target[1]} > {self.data_open[1]}")
                if self.data_target[1] > self.data_open[1]:
                    self.log(f"BUY CREATE, {self.data_open[1]}, Target {self.data_target[1]}")
                    self.trade_id += 1
                    self.order = self.buy_bracket(tradeid=self.trade_id, exectype=Order.Market,
                                                  limitprice=self.data_target[1], stopexec=None)
                else:
                    self.log(f"Invalid BUY Signal, {self.datas[0].datetime.datetime(1)}, Target {self.data_target[1]}")
            elif self.data_signal[0] == -1:
                # self.log(f"Validating {self.data_target[1]} < {self.data_open[1]}")
                if self.data_target[1] < self.data_open[1]:
                    self.log(f"SELL CREATE, {self.data_open[1]}, Target {self.data_target[1]}")
                    self.trade_id += 1
                    self.order = self.sell_bracket(tradeid=self.trade_id, exectype=Order.Market,
                                                   limitprice=self.data_target[1], stopexec=None)
                else:
                    self.log(f"Invalid SELL Signal, {self.datas[0].datetime.datetime(1)}, Target {self.data_target[1]}")

        else:
            # Target Handling - Not required due to bracket orders

            # Close of Business handling
            if self.data_cob_entry[0] == 1:
                self.order = self.close(tradeid=self.trade_id)


def run_strategy():
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Get a pandas dataframe
    base_path = '/Users/pralhad/Documents/99-src/98-trading/model-trainer/'
    tick_data_path = base_path + 'tv-data/low-tf-data/NSE_APOLLOHOSP, 1.csv'
    pred_file = base_path + 'generated/NSE_APOLLOHOSP/trainer.strategies.gspcV2.NSE_APOLLOHOSP_Raw_Pred.csv'
    tick_data = pd.read_csv(tick_data_path)
    pred_data = pd.read_csv(pred_file)
    pred_data['time'] = pred_data['time'].shift(-1)
    n = Nova(scrip="NSE_APOLLOHOSP", pred_df=pred_data, tick_df=tick_data)
    dataframe = n.data
    dataframe['next_cob_entry'] = dataframe['cob_entry'].shift(-1)
    dataframe['target'] = dataframe['target'].shift(-1)
    dataframe['curr_target'] = dataframe['target'].ffill()
    dataframe['curr_signal'] = dataframe['signal'].shift(-1)
    dataframe.dropna(subset=['curr_target'], inplace=True)
    dataframe.drop(columns=['target', 'signal', 'cob_entry'], axis=1, inplace=True)
    dataframe.set_index('date', inplace=True)

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = CustomDataLoader(dataname=dataframe, tz=pytz.timezone('Asia/Kolkata'))

    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    back = cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    trades = back[0].params
    for idx, row in trades.iterrows():
        trades.loc[idx, 'PNL'] = row.sell_price - row.buy_price
    print(trades)
    trades.to_clipboard()


if __name__ == '__main__':
    run_strategy()
