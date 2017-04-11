from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from flask import send_from_directory
from models import eg_email as NotificadorExterno, eg_cuenta_de_email as configuracionBPM, email_adjunto_api as attach_api

app = FlaskAPI(__name__)

notes = {
    0: 'adjunto 1',
    1: 'adjunto 2',
    2: 'adjunto 3',
}
def email_repr(attach):
    return {
        'link': attache.file_path,
        'email_id': attach.id_email
    }

def note_repr(key):
    return {
        'url': request.host_url.rstrip('/') + url_for('notes_detail', key=key),
        'text': notes[key]
    }


@app.route("/", methods=['GET', 'POST'])
def attach_list():
    """
    Lista de archivos adjuntos.
    """
    if request.method == 'POST':
        note = str(request.data.get('text', ''))
        idx = max(notes.keys()) + 1
        notes[idx] = note
        return note_repr(idx), status.HTTP_201_CREATED

    # request.method == 'GET'
    return [note_repr(idx) for idx in sorted(notes.keys())]


@app.route("/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def notes_detail(key):
    """
    Retrieve, update or delete note instances.
    """
    if request.method == 'PUT':
        note = str(request.data.get('text', ''))
        notes[key] = note
        return note_repr(key)

    elif request.method == 'DELETE':
        notes.pop(key, None)
        return '', status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    if key not in notes:
        raise exceptions.NotFound()
    return note_repr(key)

@app.route("/email/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def email_attach_list(key):
    """
    Lista de archivos adjuntos
    """
    if request.method == 'GET':
        try:
            email = attach_api.select(attach_api.id_email == key)
            return [email_repr(idx) for idx in sorted(email.keys())]
        except Exception, e:
            return str(e)


if __name__ == "__main__":
    app.run(debug=True)