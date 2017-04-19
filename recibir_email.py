#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import time
import smtplib
import poplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from email.Utils import parsedate, parseaddr, formataddr
from email.parser import Parser
from email.header import decode_header
import os
import json
from models import db, eg_email as NotificadorExterno, eg_cuenta_de_email as configuracionBPM, email_adjunto_api as AttachAPI
import poplib

poplib._MAXLINE=20480
now = datetime.now()
settings = json.loads(open("settings.json").read())
current_path = os.path.dirname(os.path.realpath(__file__))
print "current_path:", current_path

WEB_URL = "http://192.168.0.38:5000"

class Attachement(object):
    def __init__(self):
        self.data = None;
        self.content_type = None;
        self.size = None;
        self.name = None;


def recibir_email(config):
    # Se establece conexion con el servidor pop3
    print "Email", config.email
    m = poplib.POP3(config.servidor_pop3 , str(config.puerto_pop3))
    m.user(config.email)
    m.pass_(config.clave_email)
    #contar mails sin leer


    #obtener los mensajes para analizarlos
    attachments = []

    msglist = []
    poplist = m.list()
    if not poplist[0].startswith('+OK'):
        msglist = poplist[1]

    numero = len(msglist)
    print (numero)
    for i in range (numero):

        print "Mensaje numero"+str(i+1)
        print "--------------------"
        # Se lee el mensaje y se parsea el mje
        response, headerLines, bytes = m.retr(i+1)
        mensaje='\n'.join(headerLines)
        p = Parser()
        email = p.parsestr(mensaje)
        print (parseaddr(email['From'])[1])
        #remitentes = config.lista_blanca.split(',')
        #print remitentes
        #for remitente in remitentes:
        try:
            #print (parseaddr(email['From'])[1].index(remitente))
            #if parseaddr(email['From'])[1].index(remitente)>=0:
            #Se formatea la hora para guardarla en la BD
            a = parsedate(email['Date'])
            b = time.mktime(a)
            c = datetime.fromtimestamp(int(b)).strftime('%Y-%m-%d %H:%M')
            #''.join([ unicode(t[0], t[1] or default_charset) for t in dh ])
            #Si es compuesto con HTML o texto plano ascii
            # default_charset = 'ascii'

            tit = decode_header(email['Subject'])
            default_charset = 'ASCII'
            tipo_mail = tit[0][1]

            t_ = unicode("")
            tit = t_.join([ unicode(t[0], t[1] or default_charset) for t in tit ])
            is_html = False
            for part in email.walk():
                parte=''
                print "content type:", part.get_content_type()
                if part.get_content_type()=="text/html" or part.get_content_type() == "text/plain":
                    if part.get_content_type()=="text/html":
                        is_html = True

                        charset = part.get_content_charset()
                        print "charset.", charset
                        print part.get_content_type()
                        print "part pre sanitise", part
                        part = sanitise(part)
                        parte_utf = unicode(part.get_payload(decode=True), str(charset), "ignore") \
                            .encode('utf8', 'replace')
                        print "part post sanitise", parte_utf

                    if not is_html:
                        charset = part.get_content_charset()
                        print "charset.", charset
                        print part.get_content_type()
                        print "part pre sanitise", part
                        part = sanitise(part)
                        parte_utf = unicode(part.get_payload(decode=True), str(charset), "ignore")\
                                        .encode('utf8', 'replace')
                        print "part post sanitise", parte_utf

                else:
                    # print 'Texto plano'
                    # part = sanitise(part)
                    # parte = part.get_payload(decode=True)
                    print "attach type:", part.get_content_type()
                    attach = get_attach(part)
                    if attach:
                        attachments.append(attach)

                     #    else:
                     # print "ascii way"
                     #        for part in email.walk():
                     #            parte=''
                     #            if part.get_content_type()=="text/html" or part.get_content_type() == "text/plain":
                     #                print 'html'
                     #                part = sanitise(part)
                     #                parte_ascii = unicode(part.get_payload(decode=True))
                     #            else:
                     #                # print 'Texto plano'
                     #                # part = sanitise(part)
                     #                # parte = part.get_payload(decode=True)
                     #                print "attach type:", part.get_content_type()
                     #                attach = get_attach(part)
                     #                if attach:
                     #                    attachments.append(attach)

            #Se guarda una instancia del Mail
	        print "titulo",tit
            print "detalle", parte_utf
            print "connect db..."
            try:
                db.connect()
            except Exception, e:
                print "DB re Connect error", e
            print "db ok"
            cuenta = config.nombre
            noti = NotificadorExterno()
            noti.creado_por =1
            # noti.asignado_a = 8
            noti.destinatario = cuenta
            noti.creado_el = datetime.now().strftime('%Y-%m-%d %H:%M')
            noti.fecha_hora_inicio = noti.creado_el
            noti.asunto = tit[:255]
            noti.actividad = 'Email'
            noti.estado = 1
            noti.e_mail = parseaddr(email['From'])[1]
            try:
                noti.detalle = parte_utf
            except Exception, e:
                print "error detalle", e
                noti.detalle = ""

            try:
                '''if NotificadorExterno.select().where():
                    print 'YA EXISTE'
                else:'''
                print "pre save", noti.e_mail
                noti.save()
                print "save ok!"
                print noti.id
                print 'Se grabo!!!'
                auditable = []
                print "adjuntos:", attachments
                for attach in attachments:
                    print "save attach!"
                    folder = get_folder(noti.id)
                    pathfile = save_attach(folder, attach)
                    attach_db = save_attach_db(noti.id, attach.name, pathfile)
                    audit = create_attach_link(attach_db)
                    auditable.append(audit)

                    if auditable:
                        noti.adjuntos = "\n".join(auditable)
                        noti.save()
                        print "save auditable"


            except Exception, e:
                print ('NO SE GRABO!!!!')
                print repr(e)
        except Exception, e:
                print "ERROR en el while:", e


    poplist = m.list()
    if poplist[0].startswith('+OK') :
        msglist = poplist[1]
        for msgspec in msglist :
            # msgspec is something like "3 3941", 
            # msg number and size in octets
            msgnum = int(msgspec.split(' ')[0])
            #print "Deleting msg %d\r" % msgnum,
            #m.dele(msgnum)
            print "non deleted -fork"
        else :
            print "No messages for"
    else :
        print "Couldn't list messages: status", poplist[0]
    m.quit()	
#clase para filtrado de EMail por tipo de documentos adjuntos

import re
BAD_CONTENT_RE = re.compile('application/(msword|msexcel)', re.I)
BAD_FILEEXT_RE = re.compile(r'(\.exe|\.zip|\.pif|\.scr|\.ps|\.doc|\.xls|\.docx|\.xlsx)$')
ReplaceString = """

This message contained an attachment that was stripped out.

The original type was: %(content_type)s
The filename was: %(filename)s,
(and it had additional parameters of:
%(params)s)

"""
def sanitise(msg):
    # Strip out all payloads of a particular type
    ct = msg.get_content_type()
    # We also want to check for bad filename extensions
    fn = msg.get_filename()
    # get_filename() returns None if there's no filename
    if BAD_CONTENT_RE.search(ct) or (fn and BAD_FILEEXT_RE.search(fn)):
        # Ok. This part of the message is bad, and we're going to stomp
        # on it. First, though, we pull out the information we're about to
        # destroy so we can tell the user about it.

        # This returns the parameters to the content-type. The first entry
        # is the content-type itself, which we already have.
        params = msg.get_params()[1:]
        # The parameters are a list of (key, value) pairs - join the
        # key-value with '=', and the parameter list with ', '
        params = ', '.join([ '='.join(p) for p in params ])
        # Format up the replacement text, telling the user we ate their
        # email attachment.
        replace = ReplaceString % dict(content_type=ct,
                                       filename=fn,
                                       params=params)
        # Install the text body as the new payload.
        msg.set_payload(replace)
        # Now we manually strip away any paramaters to the content-type
        # header. Again, we skip the first parameter, as it's the
        # content-type itself, and we'll stomp that next.
        for k, v in msg.get_params()[1:]:
            msg.del_param(k)
        # And set the content-type appropriately.
        msg.set_type('text/plain')
        # Since we've just stomped the content-type, we also kill these
        # headers - they make no sense otherwise.
        del msg['Content-Transfer-Encoding']
        del msg['Content-Disposition']
    else:
        # Now we check for any sub-parts to the message
        if msg.is_multipart():
            # Call the sanitise routine on any subparts
            payload = [ sanitise(x) for x in msg.get_payload() ]
            # We replace the payload with our list of sanitised parts
            msg.set_payload(payload)
    # Return the sanitised message
    return msg


def get_attach(message_part):
    content_disposition = message_part.get("Content-Disposition", None);
    print "content_disposition", content_disposition
    if content_disposition:
        dispositions = content_disposition.strip().split(";");
        if bool(content_disposition and dispositions[0].lower() == "attachment"):

            attachment = Attachement();
            attachment.data = message_part.get_payload(decode=True);
            attachment.content_type = message_part.get_content_type();
            attachment.size = len(attachment.data);
            attachment.name = message_part.get_filename();

            return attachment;

    return None;

def save_attach(folder, attach):
    print folder, attach.name
    newfile = folder + "/" + str(attach.name)
    file = open(newfile, 'w')
    file.write(attach.data)
    file.close()
    print "SAVE ATTACH", newfile
    return newfile

def get_folder(email_id):
    newpath = str(current_path) + "/downloads/email_" + str(email_id) 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
        print "newpath:", newpath
    return newpath


def save_attach_db(email_id, name, file_path):
    attach = AttachAPI()
    attach.id_email = email_id
    attach.file_path = file_path
    attach.name = name
    attach.save()
    print "save attach index in DB!"
    return attach

def create_attach_link(attach):
    attach.link = WEB_URL + "/email/adjunto/"+ str(attach.id) + "/"
    print "attach link", link
    attach.save()
    """2017-04-11 23:08"""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    to_auditable = """- ['<a href="XXLINKXX" target="_blank">XXNAMEXX</a>', '0', 'XXFECHAXX']""".replace("XXLINKXX",attach.link).replace("XXNAMEXX",attach.name).replace("XXFECHAXX",fecha)
    print to_auditable
    return to_auditable


def main():
    cuentas = configuracionBPM.select().where(configuracionBPM.activo==True)
    for cta in cuentas:
        recibir_email(cta)
        

if __name__ == '__main__':
    print "Start Email Receiver"
    while True:
        main()
        time.sleep(30)

