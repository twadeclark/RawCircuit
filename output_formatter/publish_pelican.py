import os
import logging

from log_config import setup_logging
setup_logging()


def publish_pelican(config):
    logger = logging.getLogger(__name__)
    local_content_path = config.get('local_content_path')
    local_pelicanconf = config.get('local_pelicanconf')
    local_publish_path = config.get('local_publish_path')
    os_result = os.system("pelican " + local_content_path + " -s " + local_pelicanconf + " -o " + local_publish_path)
    if os_result != 0:
        logger.info("     Pelican failed to execute. Exiting...")
        return
    logger.info("     Pelican executed.")
