import os
import unittest

import pandas as pd

HOME_DIR = "/Users/pralhad/Documents/99-src/98-trading/model-trainer/"
os.environ["RESOURCE_PATH"] = os.path.join(HOME_DIR, "resources/test/backtesting/resources/config")
os.environ["GENERATED_PATH"] = os.path.join(HOME_DIR, "resources/test/backtesting/generated")
from trainer.analysis.accuracy import get_accuracy

TEST_STRATEGY = "model1"
TEST_SCRIP = "NSE_ACME"


class TestApiLogin(unittest.TestCase):

    def test_get_accuracy(self):
        accuracy_resp = get_accuracy(strategy=TEST_STRATEGY, scrip=TEST_SCRIP)
        expected_trades = pd.read_csv(os.path.join(HOME_DIR, "resources/test/backtesting/results",
                                                   "trainer.strategies.model1.NSE_ACME_Raw_Trades.csv"))
        actual_trades = pd.read_csv(os.path.join(HOME_DIR, "resources/test/backtesting/generated",
                                                 "NSE_ACME/trainer.strategies.model1.NSE_ACME_Raw_Trades.csv"))
        pd.testing.assert_frame_equal(expected_trades, actual_trades)

        expected_accuracy_resp = pd.read_json(os.path.join(HOME_DIR, "resources/test/backtesting/results",
                                                           "accuracy_resp.json"), precise_float=True)
        actual_accuracy_resp = pd.DataFrame([accuracy_resp])
        pd.testing.assert_frame_equal(expected_accuracy_resp, actual_accuracy_resp)
