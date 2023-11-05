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

