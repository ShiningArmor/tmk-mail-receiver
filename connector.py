import pymysql.cursors
import pymysql
import logging
import logging.handlers
from libs.colorlogging import ColorFormatter

def get_logger(name, debug=False):
    LOG_FILENAME = name + ".out"
    logFormatter = ColorFormatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger('%sLogger' % name[:name.find(".")].capitalize())
    logger.setLevel(logging.DEBUG)
    fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=1048576, backupCount=5, )
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    if debug:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)
    return logger
    
connection = pymysql.connect(host='saas.verticall.com.ar',
                              user='crmtelemercadoco',
                              password='vo(PTk+9IK=T',
                              db='crmtelemercadoco_bpm',
                              charset='utf8mb4',
                              cursorclass=pymysql.cursors.DictCursor)

