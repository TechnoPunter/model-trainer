import logging

from trainer.loggers.setup_logger import setup_logging
from trainer.service.train import ModelTrainer

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logging("portfolio-analysis.log")
    logger.info("Started portfolio analysis")
    mt = ModelTrainer()
    l_opts = ['tv-download', 'run-backtest', 'run-accuracy']
    x = mt.run_pipeline(opts=l_opts, params=None)
    print(x)
    logger.info("Finished portfolio analysis")
