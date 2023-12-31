-- DELETE FROM sl_thresholds ;

INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_APOLLOHOSP',0.9,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_APOLLOHOSP',2.4,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_APOLLOHOSP',0.9,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_APOLLOHOSP',2.4,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ASIANPAINT',0.9,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ASIANPAINT',0.8,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ASIANPAINT',2.9,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ASIANPAINT',1.4,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_AXISBANK',0.1,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_AXISBANK',1.2,1,0.1,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_AXISBANK',1.6,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_AXISBANK',1.4,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BAJAJ_AUTO',1.0,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BAJAJ_AUTO',1.0,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BAJAJ_AUTO',1.5,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BAJAJ_AUTO',1.0,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BAJAJFINSV',2.1,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BAJAJFINSV',2.1,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BAJAJFINSV',1.2,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BAJAJFINSV',1.1,1,0.6,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_BAJFINANCE',1.3,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BAJFINANCE',0.6,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BAJFINANCE',1.4,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BAJFINANCE',1.3,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BANDHANBNK',2.0,-1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BANDHANBNK',2.0,1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BANDHANBNK',2.0,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BANDHANBNK',2.2,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BHARTIARTL',0.3,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BHARTIARTL',0.3,1,0.35,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_BHARTIARTL',0.8,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BHARTIARTL',1.6,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BPCL',0.5,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BPCL',0.5,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BPCL',1.6,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BPCL',2.2,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BRITANNIA',0.3,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BRITANNIA',1.7,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_BRITANNIA',2.3,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_BRITANNIA',1.6,1,0.1,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_CIPLA',1.0,-1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_CIPLA',0.9,1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_CIPLA',1.1,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_CIPLA',1.0,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_COALINDIA',0.2,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_COALINDIA',1.4,1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_COALINDIA',1.9,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_COALINDIA',1.1,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_DIVISLAB',1.3,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_DIVISLAB',1.3,1,0.1,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_DIVISLAB',1.9,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_DIVISLAB',0.8,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_DRREDDY',0.6,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_DRREDDY',0.6,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_DRREDDY',1.7,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_DRREDDY',1.0,1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_EICHERMOT',1.8,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_EICHERMOT',1.8,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_EICHERMOT',1.8,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_EICHERMOT',1.8,1,0.1,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_GRASIM',1.7,-1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_GRASIM',1.7,1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_GRASIM',1.3,-1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_GRASIM',1.7,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HCLTECH',0.1,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HCLTECH',2.6,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HCLTECH',1.6,-1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HCLTECH',1.3,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HDFCBANK',2.5,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HDFCBANK',2.5,1,0.1,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_HDFCBANK',2.5,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HDFCBANK',1.3,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HDFCLIFE',2.2,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HDFCLIFE',1.6,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HDFCLIFE',2.2,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HDFCLIFE',1.6,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HEROMOTOCO',1.0,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HEROMOTOCO',2.2,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HEROMOTOCO',1.6,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HEROMOTOCO',1.3,1,0.6,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_HINDALCO',2.2,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HINDALCO',1.6,1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HINDALCO',2.2,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HINDALCO',1.6,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HINDUNILVR',0.5,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HINDUNILVR',0.5,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_HINDUNILVR',0.7,-1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_HINDUNILVR',1.2,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ICICIBANK',0.5,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ICICIBANK',0.5,1,0.35,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_ICICIBANK',1.5,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ICICIBANK',1.4,1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_INDUSINDBK',1.2,-1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_INDUSINDBK',1.5,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_INDUSINDBK',1.2,-1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_INDUSINDBK',1.5,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_INFY',0.3,-1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_INFY',0.6,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_INFY',3.2,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_INFY',1.2,1,0.35,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_ITC',1.6,-1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ITC',1.6,1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ITC',1.6,-1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ITC',1.6,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_JSWSTEEL',1.8,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_JSWSTEEL',1.8,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_JSWSTEEL',2.7,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_JSWSTEEL',0.4,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_KOTAKBANK',1.2,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_KOTAKBANK',1.2,1,0.1,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_KOTAKBANK',1.0,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_KOTAKBANK',0.8,1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_LT',0.4,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_LT',0.4,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_LT',2.3,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_LT',1.5,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_LTIM',0.4,-1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_LTIM',0.4,1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_LTIM',3.6,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_LTIM',0.7,1,0.6,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_MARUTI',0.3,-1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_MARUTI',2.1,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_MARUTI',1.2,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_MARUTI',0.6,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_M_M',0.2,-1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_M_M',1.8,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_M_M',1.9,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_M_M',2.0,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_NESTLEIND',2.0,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_NESTLEIND',1.4,1,0.1,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_NESTLEIND',2.0,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_NESTLEIND',1.4,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_NTPC',0.9,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_NTPC',1.2,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_NTPC',1.9,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_NTPC',0.6,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ONGC',0.1,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ONGC',0.4,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ONGC',1.7,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ONGC',0.1,1,0.1,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_POWERGRID',0.6,-1,0.2,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_POWERGRID',0.6,1,0.2,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_POWERGRID',1.9,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_POWERGRID',1.1,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_RELIANCE',0.4,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_RELIANCE',0.8,1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_RELIANCE',1.3,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_RELIANCE',1.8,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_SBILIFE',0.3,-1,0.85,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_SBILIFE',0.2,1,0.6,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_SBILIFE',2.0,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_SBILIFE',1.6,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_SBIN',0.5,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_SBIN',0.5,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_SBIN',1.8,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_SBIN',0.9,1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_SUNPHARMA',1.5,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_SUNPHARMA',1.5,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_SUNPHARMA',1.4,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_SUNPHARMA',1.1,1,0.35,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_TATACONSUM',0.6,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TATACONSUM',0.6,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TATACONSUM',1.6,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TATACONSUM',1.3,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TATAMOTORS',0.9,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TATAMOTORS',0.9,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TATAMOTORS',1.9,-1,0.85,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TATAMOTORS',0.9,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TATASTEEL',0.1,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TATASTEEL',0.1,1,0.35,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_TATASTEEL',0.9,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TATASTEEL',1.7,1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TCS',0.3,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TCS',0.3,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TCS',1.2,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TCS',1.0,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TECHM',0.4,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TECHM',0.8,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TECHM',1.1,-1,0.6,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TECHM',1.8,1,0.6,0.05,NULL,'trainer.strategies.rfcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_TITAN',0.9,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TITAN',0.9,1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_TITAN',2.0,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_TITAN',2.2,1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ULTRACEMCO',1.5,-1,0.1,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ULTRACEMCO',1.0,1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_ULTRACEMCO',1.5,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_ULTRACEMCO',1.0,1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_UPL',0.4,-1,0.35,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_UPL',0.4,1,0.35,0.05,NULL,'trainer.strategies.gspcV2');
INSERT INTO sl_thresholds (scrip,sl,direction,trail_sl,tick,target,strategy) VALUES
	 ('NSE_UPL',1.9,-1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_UPL',1.9,1,0.1,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_WIPRO',0.2,-1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_WIPRO',0.2,1,0.6,0.05,NULL,'trainer.strategies.gspcV2'),
	 ('NSE_WIPRO',1.2,-1,0.35,0.05,NULL,'trainer.strategies.rfcV2'),
	 ('NSE_WIPRO',1.4,1,0.35,0.05,NULL,'trainer.strategies.rfcV2');