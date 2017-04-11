#!/usr/bin/env python
# -*- coding: utf-8 -*-

import peewee
import json
settings = json.loads(open("settings.json").read())
db = peewee.MySQLDatabase(settings["database"], 
                            user=settings["user"],
                            passwd=settings["password"],
                            host=settings["host"],
                            port=settings["port"])

class eg_email(peewee.Model):
    id = peewee.IntegerField()
    creado_por = peewee.IntegerField()
    asignado_a = peewee.IntegerField()
    asunto = peewee.CharField()
    destinatario = peewee.CharField()
    detalle = peewee.TextField()
    e_mail = peewee.TextField()
    creado_el = peewee.DateTimeField()
    fecha_hora_inicio = peewee.DateTimeField()
    actividad = peewee.CharField()
    estado = peewee.CharField()
    class Meta:
        database = db

class eg_cuenta_de_email(peewee.Model):
    id = peewee.IntegerField()
    nombre = peewee.CharField()
    email = peewee.CharField()
    clave_email = peewee.CharField()
    servidor_pop3 = peewee.CharField()
    puerto_pop3 = peewee.CharField()
    activo = peewee.BooleanField()
    lista_blanca = peewee.TextField()
    class Meta:
        database = db

class email_adjunto_api(peewee.Model):
    id = peewee.IntegerField()
    id_email = peewee.IntegerField()
    file_path = peewee.CharField()