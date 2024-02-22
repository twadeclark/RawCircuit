# NOTSET=0: No level is set for the logger.
# DEBUG=10: Detailed information for debugging purposes.
# INFO=20: Confirmation that things are working as expected.
# WARN=30: Indication of something unexpected or a potential problem.
# ERROR=40: Error that prevents the program from performing a function.
# CRITICAL=50: Critical error that causes the program to stop or crash.

import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.FileHandler("app.log", mode='a'),
                            logging.StreamHandler()
                        ])
