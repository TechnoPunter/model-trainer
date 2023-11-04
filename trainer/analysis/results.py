import datetime
import fnmatch
import logging
import os

import pandas as pd
import progressbar

from trainer.config.reader import cfg
from trainer.consts.consts import RAW_PRED_FILE_NAME
from trainer.dataprovider.database import DatabaseEngine

TABLE = 'TrainingResult'
TODAY = str(datetime.datetime.today().date())

logger = logging.getLogger(__name__)
pd.options.mode.chained_assignment = None


class Result:
    trader_db: DatabaseEngine

    def __init__(self):
        logger.info("Initializing CloseOfBusiness")
        self.trader_db = DatabaseEngine()

    def __store_result(self, df):
        self.trader_db.delete_recs(table=TABLE,
                                   predicate=f"m.{TABLE}.training_date == '{TODAY}'")

        self.trader_db.bulk_insert(table=TABLE, data=df)

    @staticmethod
    def combine_results(path, reg):
        logger.debug(f"Path is {path}")
        files = []
        for root, dirs, files_ in os.walk(path):
            for filename in fnmatch.filter(files_, reg):
                files.append(os.path.join(root, filename))
        count = 0
        results = []
        for pnl_file in progressbar.progressbar(files):
            count += 1
            file = os.path.basename(pnl_file)
            logger.info(f"Processing {file}")
            elements = file.replace("_PNL.csv", "").split(".")
            scrip = elements[3]
            model = ".".join(elements[0:3])
            if elements[5] == "None":
                target = "0.0"
                sl = ".".join(elements[7:9])
                trail_sl = ".".join(elements[10:12])
            else:
                target = ".".join(elements[5:7])
                sl = ".".join(elements[8:10])
                trail_sl = ".".join(elements[11:13])
            key = file
            pnl_df = pd.read_csv(pnl_file)
            result_file = os.path.dirname(pnl_file) + "/../../" + ".".join([model, scrip]) + RAW_PRED_FILE_NAME
            result_df = pd.read_csv(result_file)

            result_df.rename(columns={result_df.columns[0]: "ref"}, inplace=True)
            result_columns = list(set(result_df.columns) - set(pnl_df.columns))
            result_columns.append('ref')

            combined_df = pd.merge(pnl_df, result_df[result_columns], left_on="ref", right_on="ref", how="inner")

            combined_df['training_date'] = TODAY
            combined_df['model'] = key
            combined_df['strategy'] = model
            combined_df['target_pct'] = target
            combined_df['sl_pct'] = sl
            combined_df['trail_sl_pct'] = trail_sl

            Q1 = combined_df.groupby('dir')['pnl'].quantile(0.25)
            Q3 = combined_df.groupby('dir')['pnl'].quantile(0.75)
            IQR = Q3 - Q1

            # identify outliers
            threshold = 1.5
            lower = Q1 - threshold * IQR
            upper = Q3 + threshold * IQR
            for direction, _ in Q1.items():
                curr_df = combined_df.loc[combined_df.dir == direction]
                curr_df['outlier'] = (((curr_df['dir'] == direction) & (curr_df['pnl'] < lower[direction])) |
                                      ((curr_df['dir'] == direction) & (curr_df['pnl'] > upper[direction])))
                results.append(curr_df)
        if len(results) == 0:
            return pd.DataFrame()
        final_df = pd.concat(results)
        logger.info(f"Combined data into results with {len(final_df)} records")
        return final_df

    @staticmethod
    def __store_files(df, path):

        grouped = df.groupby('scrip')

        # Loop through the groups and save each group as an individual CSV file
        for name, group_df in grouped:
            file_name = f'{name}.csv'
            group_df.to_csv(os.path.join(path, 'summary', file_name), index=False)
            print(f'Saved {file_name}')

    def load_results(self, path: str = cfg['generated'], reg: str = '*_PNL.csv', store_db: bool = False,
                     store_files: bool = True):
        data = self.combine_results(path=path, reg=reg)
        if store_files:
            self.__store_files(data, path=path)
        if store_db:
            self.__store_result(data)


if __name__ == "__main__":
    r = Result()
    r.load_results(store_files=True, store_db=True)
