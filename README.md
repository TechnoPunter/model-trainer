# Model Training App

This app will

1. Download OHLC data from Source (TV, Broker)
2. Run Models from strategies
3. Analyse the results
    1. To get Next Close
    2. To get backtest Trades
4. Summarise the results
    1. Combine for execution by the Trade Execution Engine
    2. For Portfolio Level analysis to generate Trade Execution Params file

Follow instructions in

```commandline
sh scripts/dev-setup.sh
```

OR

```commandline
sh scripts/prod-setup.sh
```

## Modes of Trainer

### Mode & Description

| Mode                | Description                                                                                                                                                                                                                                                                  |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| run-tpot            |                                                                                                                                                                                                                                                                              |
| tv-download         |                                                                                                                                                                                                                                                                              |
| run-backtest        | Using the scrip's historical data will train the model & then come up with Predictions for last X number of days                                                                                                                                                             |
| run-next-close      | Using the OHLC data up-to T, predicts direction & target for T+1                                                                                                                                                                                                             |
| combine-predictions | 2-Step process <br/>Combines Predictions from Next Close into single file<br/>Applies portfolio weightages from portfolio accuracy step to determine quantity                                                                                                                |
| run-analysis        | Uses the Raw Predictions from run-backtest to run detailed predictions using Nova (*todo* to FastBT with SL)<br/>In the Goal-Seek Mode can be used to arrive at an optimal Target, SL & Trail SL percentages.<br/>Also ranks the results by profitability excluding outliers |
| run-accuracy        | Uses the Raw Predictions from run-backtest to get Portfolio Level: Accuracy, trades and minute-by-minute MTM file using the FastBT framework *todo* implement Target, SL, Trailing SL                                                                                        |
| run-weighted-bt     | Uses Portfolio-Trades & Accuracy to <br/>Select scrip & strategy combinations for execution <br/>Distributes capital into weighted quantities on a backtesting basis<br/>Derives expected PNL with weighted quantity                                                         |
| load-results        | Combines PNL data from run-analysis at portfolio level and stores the trades                                                                                                                                                                                                 |
| load-trade-mtm      |                                                                                                                                                                                                                                                                              |

### Mode - Inputs & Outputs

| Mode                | Setup                                                                                                | Pre-requisites                  | Inputs                                                               | Outputs                                                                                                                                             |
|---------------------|------------------------------------------------------------------------------------------------------|---------------------------------|----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| run-tpot            |                                                                                                      |                                 |                                                                      |                                                                                                                                                     |
| tv-download         |                                                                                                      |                                 |                                                                      |                                                                                                                                                     |
| run-backtest        | steps.scrips<br/>training.test.low-dt                                                                | ScripData.get_base_data         | N/A                                                                  | File: {scrip}/{strategy}.{scrip}.Raw_Pred                                                                                                           |
| run-next-close      | steps.scrips                                                                                         | ScripData.get_base_data         | N/A                                                                  | File: {scrip}/{strategy}.{scrip}.Next_Close                                                                                                         |
| combine-predictions | steps.scrips<br/>steps.threshold.*<br/>steps.weights<br/>steps.accounts.capital                      | run-next-close<br/>run-accuracy | {scrip}/{strategy}.{scrip}.Next_Close<br/>summary/Portfolio-Accuracy | #todo                                                                                                                                               |
| run-analysis        | steps.analysis.*                                                                                     | run-backtest                    | {scrip}/{strategy}.{scrip}.Raw_Pred                                  | Variable: ra_list (Dict)                                                                                                                            |
| run-ranking         | N/A                                                                                                  | run-backtest                    | {scrip}/{strategy}.{scrip}.Raw_Pred                                  | Files: <br/>{scrip}/{scrip}.Rank<br/>{scrip}/{scrip}.Summary<br/>summary/Portfolio-Rank<br/>summary/Portfolio-Rank.sql<br/>summary/Portfolio-Trades |
| run-accuracy        | N/A                                                                                                  | run-backtest                    | {scrip}/{strategy}.{scrip}.Raw_Pred                                  | Files:<br/>summary/Portfolio-Accuracy<br/>summary/Portfolio-Trades<br/>summary/Portfolio-Trades-MTM                                                 |
| run-weighted-bt     | steps.account.capital<br/>steps.accounts.threshold<br/>steps.weights<br/> steps.threshold (Fallback) | run-accuracy                    | summary/Portfolio-Accuracy                                           | File: summary/{acct}-BT-Trades                                                                                                                      |
| load-results        | N/A                                                                                                  | run-analysis                    | Variable: ra_list (Dict)                                             | File: summary/{scrip}<br/>Table: TrainingResult                                                                                                     |
| load-trade-mtm      | N/A                                                                                                  | run-accuracy                    | File:summary/Portfolio-Trades-MTM                                    | Table: TradesMTM                                                                                                                                    |

### Mode - Generated File Layouts

| File Name                     | Description                                                      | Columns                                                                                                                                                                                                         |
|-------------------------------|------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| {strategy}.{scrip}.Raw_Pred   | Raw Predictions for each period from training start date         | time<br/>target<br/>signal                                                                                                                                                                                      |
| {strategy}.{scrip}.Next_Close | Predicted direction & target                                     | close<br/>target<br/>signal                                                                                                                                                                                     |
| Portfolio-Accuracy            | Accuracy for scrip & strategy combination broken up by direction | scrip<br/>strategy<br/>trades<br/>entry_pct<br/>l_trades<br/>l_pct_success<br/>l_pnl<br/>l_avg_cost<br/>l_pct<br/>l_entry_pct<br/>s_trades<br/>s_pct_success<br/>s_pnl<br/>s_avg_cost<br/>s_pct<br/>s_entry_pct |
| Portfolio-Trades              | Day-wise PNL for scrip & strategy combination                    | scrip<br/>strategy<br/>date<br/>signal<br/>time<br/>open<br/>target<br/>day_close<br/>entry_price<br/>target_candle<br/>max_mtm<br/>target_pnl                                                                  |
| Portfolio-Trades-MTM          | Contains the minute-by-minute MTM for each Portfolio-Trade entry | scrip<br/>strategy<br/>date<br/>datetime<br/>signal<br/>time<br/>open<br/>high<br/>low<br/>close<br/>target<br/>target_met<br/>day_close<br/>entry_price<br/>mtm<br/>mtm_pct                                    |
| {acct}-BT-Trades              | Contains backtesting trades with weighted quantities plugged in  | signal<br/>time<br/>close<br/>target<br/>day_close<br/>entry_price<br/>target_candle<br/>max_mtm<br/>target_pnl<br/>scrip<br/>model<br/>date<br/>quantity<br/>margin<br/>pnl                                    |