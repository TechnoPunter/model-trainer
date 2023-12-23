from unittest.mock import patch

from tests.Utils import *


class TestCombiner(unittest.TestCase):
    scrip = "NSE_ACME"
    strategy = "TEST.ME"
    steps_param = read_file('reward-factor/trainer-config.yaml')

    @patch.dict('commons.config.reader.cfg', {"steps": steps_param['steps']})
    @patch.dict('commons.config.reader.cfg',
                {"generated": os.path.join(TEST_RESOURCE_DIR, 'reward-factor', 'generated')})
    # @patch('commons.backtest.fastBT.FastBT.ScripData')
    @patch('commons.dataprovider.ScripData.ScripData')
    def test_run_pipeline(self, mock_api):
        from trainer.service.train import ModelTrainer
        tick_data = read_file_df(name="reward-factor/tick-data.csv")
        base_data = read_file_df(name="reward-factor/base-data.csv")

        mock_api.get_tick_data.return_value = tick_data
        mock_api.get_base_data.return_value = base_data

        mt = ModelTrainer(scrip_data=mock_api)
        l_opts = ['run-base-accuracy', 'run-rf-accuracy', 'run-weighted-bt']
        x = mt.run_pipeline(opts=l_opts, params=None)
        assert True
