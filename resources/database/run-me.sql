select
--key
base.scrip, base.strategy, base.date, base.signal,
--matching
base.entry_time, base.entry_price, base.max_mtm, base.max_mtm_pct,
--diff
base.target as base_target,	rf.target as rf_target,
base.bod_strength as base_bod_strength,	rf.bod_strength as rf_bod_strength,
base.bod_sl as base_bod_sl,	rf.bod_sl as rf_bod_sl,
base.sl_range as base_sl_range,	rf.sl_range as rf_sl_range,
base.trail_sl as base_trail_sl,	rf.trail_sl as rf_trail_sl,
base.strength as base_strength,	rf.strength as rf_strength,
base.status as base_status,	rf.status as rf_status,
base.exit_price as base_exit_price,	rf.exit_price as rf_exit_price,
base.exit_time as base_exit_time,	rf.exit_time as rf_exit_time,
base.pnl as base_pnl,	rf.pnl as rf_pnl,
base.sl as base_sl,	rf.sl as rf_sl,
base.sl_update_cnt as base_sl_update_cnt,	rf.sl_update_cnt as rf_sl_update_cnt
from base_bt_accuracy_trades base
full outer join rf_bt_accuracy_trades rf
on base.scrip = rf.scrip
and base.strategy = rf. strategy
and base."date" = rf."date"
where base.signal = '-1'
order by scrip, strategy, "date"
;


select * from base_bt_accuracy_summary
where scrip='NSE_LTIM'
--and strategy = 'trainer.strategies.gspcV2'
order by scrip, strategy, trade_date asc;