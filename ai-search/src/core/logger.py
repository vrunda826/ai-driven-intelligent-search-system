import logging
from pathlib import Path


def get_logger(name: str, log_dir: str):

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s : %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file = logging.FileHandler(
        Path(log_dir) / "project.log"
    )
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)
    logger.propagate = False
    return logger