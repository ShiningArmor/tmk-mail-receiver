from flask import request, url_for
from flask import send_from_directory
#from models import eg_email as NotificadorExterno, eg_cuenta_de_email as configuracionBPM, email_adjunto_api as AttachAPI, db
import json
import logging
import logging.handlers
from libs.colorlogging import ColorFormatter
from connector import get_data
from flask import Flask
app = Flask(__name__)



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


logger = get_logger("log_attach", True)

@app.route("/")
def hello():
    logger.info("#(bold green)test")
    return "test"

@app.route('/email/adjunto/<int:key>/')
def uploaded_file(key):
        logger.info("#(bold green)__________GET_________________")
        logger.info("#(bold cyan)id adjunto: %s" % str(key))

        #attach = get_data_db(key)
        logger.debug("get_data func:")
        attach = get_data(key, logger)
        logger.debug("get_data finish!")
        #return attach

        full_path = attach["file_path"]
        folder = full_path[:full_path.rfind("/")]
        file = full_path[full_path.rfind("/") + 1:]
        logger.info("#(bold cyan)carpeta: %s" % str(folder))
        logger.info("#(bold cyan)carpeta: %s" % str(folder))
        logger.info("#(bold green)___________END_GET____________")
        return send_from_directory(folder, file)

def get_data_db(key):
    pass



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)