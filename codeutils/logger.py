import logging
import os
import time
import json
from torch import distributed as dist


def serialize(obj):
    try:
        return str(obj)  # Fallback: Convert to string
    except Exception:
        return "<non-serializable>"
    

def is_main_process():
    rank, _ = get_dist_info()
    return rank == 0


def get_dist_info():
    if dist.is_available() and dist.is_initialized():
        rank = dist.get_rank()
        world_size = dist.get_world_size()
    else:
        rank = 0
        world_size = 1
    return rank, world_size


def get_root_logger(log_file=None, log_level=logging.INFO):
    logger = logging.getLogger('acoustics')
    # if the logger has been initialized, just return it
    if logger.hasHandlers():
        return logger
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=log_level)
    if not is_main_process():
        logger.setLevel('ERROR')
    elif log_file is not None:
        file_handler = logging.FileHandler(log_file, 'w')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    return logger


def init_train_logger(args, config=None, save_directory=None):
    # Make sure previous handlers are removed
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    if save_directory is None:
        save_directory = args.dir
    os.makedirs(os.path.abspath(save_directory), exist_ok=True)
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    log_file = os.path.join(save_directory, f'{timestamp}.log')
    logger = get_root_logger(log_file=log_file)
    logger.info(f'Args:\n{json.dumps(args, indent=4, default=serialize)}')
    if config is not None:
        logger.info(f'Config:\n{json.dumps(config, indent=4, default=serialize)}')
    return logger


def print_log(msg, logger=None, level=logging.INFO):
    if logger is None:
        print(msg)
    elif isinstance(logger, logging.Logger):
        logger.log(level, msg)
    else:
        raise TypeError(
            'logger should be either a logging.Logger object, '
            f'"silent" or None, but got {type(logger)}')


def close_logger(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()
