# NOTSET=0: No level is set for the logger.
# DEBUG=10: Detailed information for debugging purposes.
# INFO=20: Confirmation that things are working as expected.
# WARN=30: Indication of something unexpected or a potential problem.
# ERROR=40: Error that prevents the program from performing a function.
# CRITICAL=50: Critical error that causes the program to stop or crash.

from logging.handlers import RotatingFileHandler
import logging

def setup_logging():
    rotating_handler = RotatingFileHandler(
        "app.log",
        maxBytes=1024*1024*1,
        backupCount=5,
        mode='a',
        encoding='utf-8'
    )
    
    log_format = '%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    date_format = '%Y-%m-%d:%H:%M:%S'
    
    logging.basicConfig(
        format=log_format,
        datefmt=date_format,
        level=logging.INFO,
        handlers=[
            rotating_handler,
            logging.StreamHandler()
        ]
    )
