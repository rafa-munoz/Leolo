import os
import logging
import logging.handlers
import sys
import settings

class Logger(object):
    """
    Logger Manager.
    Handles all logging files.
    """
    LOG_FILENAME = os.path.join(PATH, "leolo.log")

    def __init__(self, loggername="root"):
        self.logger = logging.getLogger(loggername)
        if not os.path.isdir(LEOLO_PATH):
            try:
                os.mkdir(LEOLO_PATH) # create dir if it doesn't exist
            except:
                raise IOError("Couldn't create \"" + LEOLO_PATH + "\" folder. Check"
                              " permissions")
        try:
            handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, mode="a", maxBytes=61440)
        except Exception, error:
            raise IOError("Couldn't create/open file \"" + LOG_FILENAME + "\""
                          ". Check permissions. Details:\n" + str(error))
        formatter = logging.Formatter("%(asctime)s %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def error(self, msg):
        self.logger.error(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

