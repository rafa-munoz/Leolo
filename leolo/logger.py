import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import settings

try:
    PATH = settings.LEOLO_PATH
except AttributeError:
    PATH = os.path.join(os.path.expanduser('~'), '.leolo')
LOG_FILENAME = os.path.join(PATH, "leolo.log")

class Logger(object):
    """
    Logger Manager.
    Handles all logging files.
    """

    def __init__(self, loggername="root"):
        self.logger = logging.getLogger(loggername)
        if not os.path.isdir(PATH):
            try:
                os.mkdir(PATH) # create dir if it doesn't exist
            except:
                raise IOError("Couldn't create \"" + PATH +
                              "\" folder. Check permissions")
        try:
            handler = RotatingFileHandler(LOG_FILENAME,
               mode="a", maxBytes=61440)
        except Exception, error:
            raise IOError("Couldn't create/open file \"" + LOG_FILENAME + "\""
                          ". Check permissions. Details:\n" + str(error))
        formatter = logging.Formatter("%(asctime)s %(name)s - %(levelname)s "
                                      "- %(message)s")
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

