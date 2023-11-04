from trainer.loggers.setup_logger import setup_logging
from trainer.train import ModelTrainer
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    setup_logging("model-train.log")
    logger.info("Started model training")
    mt = ModelTrainer()
    x = mt.run_pipeline()
    print(x)
    logger.info("Finished model training")
