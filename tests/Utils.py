import json
import logging
import os
import unittest


import pandas as pd

if os.path.exists('/var/www/model-trainer'):
    REPO_PATH = '/var/www/model-trainer/'
else:
    REPO_PATH = '/Users/pralhad/Documents/99-src/98-trading/model-trainer/'

ACCT = 'Trader-V2-Pralhad'
TEST_RESOURCE_DIR = os.path.join(REPO_PATH, 'resources/test')

os.environ['RESOURCE_PATH'] = os.path.join(TEST_RESOURCE_DIR, 'resources/config')
os.environ['GENERATED_PATH'] = os.path.join(TEST_RESOURCE_DIR, 'generated')
os.environ['LOG_PATH'] = os.path.join(REPO_PATH, 'logs')

logger = logging.getLogger(__name__)


def read_file(name, ret_type: str = "JSON"):
    res_file_path = os.path.join(TEST_RESOURCE_DIR, name)
    with open(res_file_path, 'r') as file:
        result = file.read()
        if ret_type == "DF":
            if "csv" in name:
                return pd.read_csv(res_file_path)
            else:
                return pd.DataFrame(json.loads(result))
        else:
            return json.loads(result)


def read_file_df(name):
    return read_file(name, ret_type="DF")
