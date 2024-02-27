# NOTSET=0: No level is set for the logger.
# DEBUG=10: Detailed information for debugging purposes.
# INFO=20: Confirmation that things are working as expected.
# WARN=30: Indication of something unexpected or a potential problem.
# ERROR=40: Error that prevents the program from performing a function.
# CRITICAL=50: Critical error that causes the program to stop or crash.

import logging

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("app.log", mode='a'),
            logging.StreamHandler()
        ])
