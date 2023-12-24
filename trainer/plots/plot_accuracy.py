# importing the required libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from commons.consts.consts import BASE_ACCURACY_FILE, RF_ACCURACY_FILE


def plot_accuracy():
    base_accu = pd.read_csv(BASE_ACCURACY_FILE)
    scrips = base_accu.scrip.unique()
    strategies = base_accu.strategy.unique()

    rf_accu = pd.read_csv(RF_ACCURACY_FILE)

    x = np.array(base_accu.loc[(base_accu.scrip == scrips[0]) &
                               (base_accu.strategy == strategies[0])].trade_date)
    x = np.asarray(x, dtype='datetime64[s]')

    y1 = np.array(base_accu.loc[(base_accu.scrip == scrips[0]) &
                               (base_accu.strategy == strategies[0])].l_pct_returns)

    y2 = np.array(rf_accu.loc[(rf_accu.scrip == scrips[0]) &
                              (rf_accu.strategy == strategies[0])].l_pct_returns)

    y3 = np.array(base_accu.loc[(base_accu.scrip == scrips[0]) &
                               (base_accu.strategy == strategies[0])].s_pct_returns)

    y4 = np.array(rf_accu.loc[(rf_accu.scrip == scrips[0]) &
                              (rf_accu.strategy == strategies[0])].s_pct_returns)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.tick_params(axis='x', labelrotation=90)
    ax.plot(x, y1, color='tab:blue')
    ax.plot(x, y2, color='tab:orange')
    ax.plot(x, y3, color='tab:green')
    ax.plot(x, y4, color='tab:red')
    plt.show()


if __name__ == '__main__':
    plot_accuracy()
