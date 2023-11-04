import datetime
import logging
import time

from trainer.consts.consts import IST

logger = logging.getLogger(__name__)


def get_epoch(date_string: str):
    if date_string == '0':
        return int(time.time())
    else:
        # Define the date string and format
        date_format = '%d-%m-%Y %H:%M:%S'
        return int(IST.localize(datetime.datetime.strptime(date_string, date_format)).timestamp())
