# Source - https://stackoverflow.com/a/7622029
# Posted by koehlma, modified by community. See post 'Timeline' for change history
# Retrieved 2026-06-05, License - CC BY-SA 3.0

import logging

def get_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s- %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger