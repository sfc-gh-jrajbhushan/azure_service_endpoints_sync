# src/logger.py
import logging

def setup_logger():
    logging.basicConfig(
        filename='../logs/app.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )
    return logging.getLogger()
