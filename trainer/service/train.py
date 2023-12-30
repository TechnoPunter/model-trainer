import logging
import multiprocessing
from multiprocessing import Pool

import pandas as pd
from commons.broker.Shoonya import Shoonya
from commons.config.reader import cfg
from commons.consts.consts import *
from commons.dataprovider.ScripData import ScripData
from commons.dataprovider.database import DatabaseEngine
from commons.loggers.setup_logger import setup_logging
from commons.service.ScripDataService import ScripDataService

from trainer.analysis.accuracy import run_base_accuracy, load_rf_mtm, run_rf_accuracy, run_prep_data, \
    load_base_accuracy_results, load_rf_accuracy_results
from trainer.analysis.combiner import Combiner
from trainer.analysis.resultranker import rank_results
from trainer.analysis.results import Result
from trainer.backtest.nova import Nova
from trainer.service.run_get_predictions import run_get_predictions
from trainer.utils.TrainSplit import get_filtered_df
from trainer.utils.standard_prep import standard_prep

logger = logging.getLogger(__name__)

ACCT = 'Trader-V2-Pralhad'


class ModelTrainer:
    cfg: dict
    trader_db: DatabaseEngine

    def __init__(self, scrip_data: ScripData = None, exec_mode: str = "SERVER"):
        self.cfg = cfg
        self.trader_db = DatabaseEngine()
        self.threshold = self.__get_sl_threshold()
        self.threshold_range = self.__get_sl_threshold_range()
        self.exec_mode = exec_mode
        if scrip_data is None:
            self.sd = ScripData(trader_db=self.trader_db)
        else:
            self.sd = scrip_data
        self.s = Shoonya(ACCT)
        self.sds = ScripDataService(shoonya=self.s, trader_db=self.trader_db)

    def __get_sl_threshold_range(self) -> dict:
        result = {}
        records = self.trader_db.query("SlThresholdRange", "1==1")
        for rec in records:
            result[rec.scrip] = rec
        return result

    def __get_sl_threshold(self) -> dict:
        result = {}
        records = self.trader_db.query("SlThresholds", "1==1")
        for rec in records:
            result[":".join([rec.scrip, str(rec.direction)])] = rec
        return result

    def __analyse(self, strategies, scrip_name: str, params: dict):
        """
        Calls run_scenario to create PNL Files for each of the strategies with set or range of SL/Target/Trail SL
        :param strategies: Name of strategies to run on
        :param scrip_name:
        :param params:
        :return:
        """
        ra_list = {}
        range_list = []  # SL / Trail SL / Target range combination
        run_list = []  # Strategy / Range List combination
        tick_df = self.sd.get_tick_data(scrip_name)
        threshold = self.threshold_range.get(scrip_name.replace("NSE_", ""))
        mode = self.cfg['steps']["analysis"]["mode"]
        if mode == "goal-seek":
            if threshold is None:
                min_target = self.cfg['steps']["analysis"]['goal-seek']['min_target']
                max_target = self.cfg['steps']["analysis"]['goal-seek']['max_target']
                target_step = self.cfg['steps']["analysis"]['goal-seek']['target_step']

                min_sl = self.cfg['steps']["analysis"]['goal-seek']['min_sl']
                max_sl = self.cfg['steps']["analysis"]['goal-seek']['max_sl']
                sl_step = self.cfg['steps']["analysis"]['goal-seek']['sl_step']

                min_trail_sl = self.cfg['steps']["analysis"]['goal-seek']['min_trail_sl']
                max_trail_sl = self.cfg['steps']["analysis"]['goal-seek']['max_trail_sl']
                trail_sl_step = self.cfg['steps']["analysis"]['goal-seek']['trail_sl_step']
            else:
                min_target = threshold.min_target
                max_target = threshold.max_target
                target_step = threshold.target_step

                min_sl = threshold.min_sl
                max_sl = threshold.max_sl
                sl_step = threshold.sl_step

                min_trail_sl = threshold.min_trail_sl
                max_trail_sl = threshold.max_trail_sl
                trail_sl_step = threshold.trail_sl_step

            if min_target is None:
                sl = min_sl
                while sl <= max_sl:
                    trail_sl = min_trail_sl
                    while trail_sl <= max_trail_sl:
                        range_param = {
                            'key': ".".join(['target', "None",
                                             'sl', format(sl, ".2f"),
                                             'trail_sl', format(trail_sl, ".2f")
                                             ]),
                            'signal': '0',
                            'sl': sl,
                            'trail_sl': trail_sl,
                            'target': None
                        }
                        range_list.append(range_param)

                        trail_sl += trail_sl_step
                    sl += sl_step
            else:
                target = min_target
                while target <= max_target:
                    sl = min_sl
                    while sl <= max_sl:
                        trail_sl = min_trail_sl
                        while trail_sl <= max_trail_sl:
                            range_param = {
                                'key': ".".join(['target', "None" if target is None else format(target, ".2f"),
                                                 'sl', format(sl, ".2f"),
                                                 'trail_sl', format(trail_sl, ".2f")
                                                 ]),
                                'signal': '0',
                                'sl': sl,
                                'trail_sl': trail_sl,
                                'target': target
                            }
                            range_list.append(range_param)

                            trail_sl += trail_sl_step
                        sl += sl_step
                    target += target_step
        else:
            l_key = f"{scrip_name}:1"
            long_scrip_threshold = self.threshold.get(l_key)
            s_key = f"{scrip_name}:-1"
            short_scrip_threshold = self.threshold.get(s_key)
            if long_scrip_threshold is None or long_scrip_threshold.sl is None is None:
                sl = self.cfg['steps']["analysis"]['calc']['sl']
                trail_sl = self.cfg['steps']["analysis"]['calc']['trail_sl']
                target = self.cfg['steps']["analysis"]['calc']['target']
            else:
                sl = long_scrip_threshold.sl
                trail_sl = long_scrip_threshold.trail_sl
                target = long_scrip_threshold.target
            range_list.append({
                'key': ".".join(['target', "None" if target is None else format(target, ".2f"),
                                 'sl', format(sl, ".2f"),
                                 'trail_sl', format(trail_sl, ".2f")
                                 ]),
                'signal': '1',
                'sl': sl,
                'trail_sl': trail_sl,
                'target': target
            })

            if short_scrip_threshold is None or short_scrip_threshold.sl is None:
                sl = self.cfg['steps']["analysis"]['calc']['sl']
                trail_sl = self.cfg['steps']["analysis"]['calc']['trail_sl']
                target = self.cfg['steps']["analysis"]['calc']['target']
            else:
                sl = short_scrip_threshold.sl
                trail_sl = short_scrip_threshold.trail_sl
                target = short_scrip_threshold.target
            range_list.append({
                'key': ".".join(['target', "None" if target is None else format(target, ".2f"),
                                 'sl', format(sl, ".2f"),
                                 'trail_sl', format(trail_sl, ".2f")
                                 ]),
                'signal': '-1',
                'sl': sl,
                'trail_sl': trail_sl,
                'target': target
            })

        for strategy in strategies:
            strategy_result_path = str(os.path.join(params['result_path'], strategy))
            if not os.path.exists(strategy_result_path):
                os.makedirs(strategy_result_path)
            pred_key = ".".join([strategy, scrip_name])
            pred_file_path = str(os.path.join(params['work_path'], pred_key + RAW_PRED_FILE_NAME))
            raw_df_out = pd.read_csv(pred_file_path)
            raw_df_out['time'] = raw_df_out['time'].shift(-1)
            raw_df_out.dropna(subset=['time'], inplace=True)
            long_pred = raw_df_out.loc[raw_df_out.signal == 1]
            short_pred = raw_df_out.loc[raw_df_out.signal == -1]
            for rec in range_list:
                run_key = ".".join([pred_key, rec.get("key")])
                logger.debug(f"Run Key: {run_key}")
                pred = None
                if rec.get("signal") == '0':
                    pred = raw_df_out
                elif rec.get("signal") == '1':
                    pred = long_pred
                elif rec.get("signal") == '-1':
                    pred = short_pred
                if pred is not None:
                    param = (run_key, rec, scrip_name, pred, tick_df, strategy_result_path)
                    run_list.append(param)

            with Pool() as pool:
                for result in pool.imap_unordered(self.run_scenario, run_list):
                    pass
        return ra_list

    @staticmethod
    def run_scenario(run_list: tuple):
        run_key, run_params, scrip, pred_df, tick_df, result_path = run_list
        n = Nova(scrip=scrip, pred_df=pred_df, tick_df=tick_df)
        pnl_file_path = str(os.path.join(result_path, run_key + PNL_FILE_NAME))
        n.process_events(pnl_file_path, params=run_params)

    @staticmethod
    def handle_result_files(ra_data):

        results = Result()
        results.load_results()

        # # Create a Pandas Excel writer object
        # writer = pd.ExcelWriter(GENERATED_DATA_PATH + 'combined_output.xlsx', engine='xlsxwriter')
        #
        # # Iterate over the data array
        # for pred_key, df in ra_data.items():
        #     sheet_name = pred_key.replace("trainer.strategies.", "")
        #     # Write each DataFrame to a separate sheet
        #     df['datein'] = df['datein'].dt.tz_localize(None)
        #     df['dateout'] = df['dateout'].dt.tz_localize(None)
        #     df.to_excel(writer, sheet_name=sheet_name, index=False)
        #
        # # Save the Excel file
        # writer.close()

    def run_pipeline(self, opts=None, params: dict = None) -> [(str, pd.DataFrame)]:
        """
        0. Read base data
        1. Standard Prep
            inputs: base_data : pd.DataFrame,
        2. Custom Prep
        3. Get pipeline
        4. Backtest
        Returns: None

        """
        logger.info(f"Running pipeline with {opts}")

        if opts is None:
            opts = self.cfg['steps']['opts']
        ra_data = {}

        if "tv-download" in opts:
            self.sds.load_scrips_data(scrip_names=self.cfg['steps']['scrips'])

        prediction_param_list = []

        for scrip in self.cfg['steps']['scrips']:
            scrip_params = params
            work_path = os.path.join(GENERATED_DATA_PATH, scrip)
            if scrip_params is None:
                scrip_params = {"work_path": work_path}
            else:
                scrip_params['work_path'] = work_path
            if not os.path.exists(work_path):
                os.makedirs(work_path)

            result_path = os.path.join(GENERATED_DATA_PATH, scrip, "results")
            if scrip_params is None:
                scrip_params = {"result_path": result_path}
            else:
                scrip_params['result_path'] = result_path
            if not os.path.exists(result_path):
                os.makedirs(result_path)

            if "run-backtest" in opts or "run-next-close" in opts:
                base_data = self.sd.get_base_data(scrip)

                filtered_data = get_filtered_df(df=base_data, cfg=self.cfg, type="train")

                prep_data = standard_prep(filtered_data)
                if "run-backtest" in opts:
                    prediction_param_list.append((scrip_params, prep_data, scrip, 'BACKTEST'))

                if "run-next-close" in opts:
                    prediction_param_list.append((scrip_params, prep_data, scrip, 'NEXT-CLOSE'))

        if self.exec_mode == "SERVER":
            try:
                logger.info(f"About to start prediction calc with {len(prediction_param_list)} objects")
                with Pool(processes=multiprocessing.cpu_count()) as pool:
                    for result in pool.imap(run_get_predictions, prediction_param_list):
                        logger.info(result)
            except Exception as ex:
                print(ex)
                logger.error(f"Error in Multi Processing {ex}")
        else:
            for param in prediction_param_list:
                result = run_get_predictions(param)
                logger.info(result)

        strategies = self.cfg['steps']['strats']
        for scrip in self.cfg['steps']['scrips']:
            if "run-analysis" in opts:
                ra_data.update(self.__analyse(strategies, scrip, params))

        if "combine-predictions" in opts:
            c = Combiner(shoonya=self.s, scrip_data=self.sd)
            res = c.combine_predictions()
            logger.info(f"Combiner Results: {res}")

        if "load-results" in opts:
            self.handle_result_files(ra_data)

        if "run-ranking" in opts:
            rank_results()

        if "run-base-accuracy" in opts or "run-rf-accuracy" in opts:
            params = run_prep_data()

            if "run-base-accuracy" in opts:
                run_base_accuracy(params=params, scrip_data=self.sd, exec_mode=self.exec_mode)
                load_base_accuracy_results(self.trader_db)

            if "run-rf-accuracy" in opts:
                run_rf_accuracy(params=params, scrip_data=self.sd, exec_mode=self.exec_mode)
                load_rf_accuracy_results(self.trader_db)
                load_rf_mtm(self.trader_db)

        if "run-weighted-bt" in opts:
            c = Combiner(shoonya=self.s, scrip_data=self.sd)
            res = c.weighted_backtest()
            logger.info(f"Combiner Results: {res}")

        return ra_data


if __name__ == "__main__":
    setup_logging("train.log")

    logger.info("Started steps")
    mt = ModelTrainer(exec_mode="SERVER")
    l_opts = None
    # l_opts = []
    # l_opts.append('tv-download')
    # l_opts.append('run-backtest')
    # l_opts.append('run-accuracy')
    # l_opts.append('run-next-close')
    res_ = mt.run_pipeline(opts=l_opts, params=None)
    logger.info("Finished steps")
