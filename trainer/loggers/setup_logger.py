import logging
import logging.config
import os

import yaml


def setup_logging(log_file_name: str = "traderV3.log", file_path: str = 'resources/config'):
    module_path = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(file_path + "/logging-local.yaml", 'r') as child_file:
            config = yaml.safe_load(child_file)
    except FileNotFoundError:
        with open(file_path + "/logging.yaml", 'r') as child_file:
            config = yaml.safe_load(child_file)

    config['handlers']['fileHandler']['filename'] = module_path + "/../../logs/" + log_file_name
    logging.config.dictConfig(config)


try:
    setup_logging()
except FileNotFoundError:
    setup_logging(file_path='../../resources/config')

if __name__ == "__main__":
    setup_logging()
