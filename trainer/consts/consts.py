import datetime

import pytz

from trainer.config.reader import cfg as _cfg

GENERATED_DATA_PATH = _cfg['generated']
MODELS_PATH = GENERATED_DATA_PATH + "models/"
PRED_FILE_NAME = "_Predict.csv"
RESULT_FILE_NAME = "_Result.csv"
RAW_PRED_FILE_NAME = "_Raw_Pred.csv"
NEXT_CLOSE_FILE_NAME = "_Next_Close.csv"
PNL_FILE_NAME = "_PNL.csv"
MODEL_SCRIPT_NAME = '_tpot_exported_pipeline.py'
COLUMN_SEPARATOR = ","
TRAIN_TEST_SPLIT_PCT = 0.99
IST = pytz.timezone('Asia/Kolkata')
MODEL_SAVE_FILE_NAME = '.sav'
TODAY = datetime.datetime.today().date()
