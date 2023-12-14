from tests.Utils import *
from trainer.analysis.combiner import Combiner


class TestCombiner(unittest.TestCase):
    cb = Combiner()
    scrip = "NSE_ACME"
    strategy = "TEST.ME"

    def test_weighted_backtest(self):
        self.cb.weighted_backtest()
        assert True

    def test_combine_predictions(self):
        self.cb.combine_predictions()
        assert True
