from flask import request, url_for
from flask import send_from_directory
from models import eg_email as NotificadorExterno, eg_cuenta_de_email as configuracionBPM, email_adjunto_api as AttachAPI
import json

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "test"

@app.route('/email/adjunto/<int:key>/')
def uploaded_file(key):
    try:
        print "key", key
        attach = AttachAPI.get(AttachAPI.id == key)
        full_path = attach.file_path
        folder = full_path[:full_path.rfind("/")]
        file = full_path[full_path.rfind("/") + 1:]
        print folder, file
        return send_from_directory(folder, file)
    except Exception, e:
        return str(e)


if __name__ == "__main__":
    app.run()