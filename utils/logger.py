import logging
import os
import warnings
from transformers import logging as transformers_logging

warnings.simplefilter(action='ignore', category=FutureWarning)
transformers_logging.set_verbosity_error()


def get_logger(name):
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(log_dir, f'{name}.log'))
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
    return logger