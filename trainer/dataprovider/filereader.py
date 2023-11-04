import fnmatch

import pandas as pd
import os

from trainer.config.reader import cfg as config


def _file_combiner(data_dir_path: [str], scrip_name: str = None):
    csv_files = []
    for path in data_dir_path:
        for root, dirs, files in os.walk(path):
            for filename in fnmatch.filter(files, '*.csv'):
                csv_files.append(os.path.join(root, filename))

    if scrip_name is not None:
        csv_files = list(filter(lambda file: scrip_name + "," in file, csv_files))
    if len(csv_files) == 0:
        return None
    csv_files.sort(key=os.path.getctime)
    result = pd.DataFrame()

    for file in csv_files:
        if len(result) == 0:
            result = pd.read_csv(file)
        else:
            curr_df = pd.read_csv(file)
            columns_to_merge = list(result.columns.intersection(curr_df.columns))
            result = pd.merge(result, curr_df, on='time', how='outer', suffixes=('_1', '_2'))
            filtered_column_list = [col for col in columns_to_merge if col != "time"]

            for col in filtered_column_list:
                result[col] = result[col + '_1'].fillna(result[col + '_2'])
                result.drop(col + '_1', axis=1, inplace=True)
                result.drop(col + '_2', axis=1, inplace=True)
    return result


def get_base_data(scrip_name: str = None):
    path = config['base-data-dir-path']
    ret_df = _file_combiner(path, scrip_name)
    return ret_df


def get_tick_data(scrip_name: str = None):
    path = config['low-tf-data-dir-path']
    ret_df = _file_combiner(path, scrip_name)
    return ret_df


# Example usage:
if __name__ == '__main__':
    print(get_base_data('NSE_RELIANCE'))
    tick_df = get_tick_data('NSE_RELIANCE')
    tick_df.to_clipboard()
    print(tick_df)
