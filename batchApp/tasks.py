from __future__ import absolute_import

import os
from PIL import Image, ImageFont
from PIL.ImageDraw import ImageDraw

import boto
import boto3
import time

import datetime
from bson import ObjectId
from celery import shared_task, task

from django.core.files.storage import default_storage
from django.utils import timezone

from mongoAuthApp.DBUtils import Connection

import smtplib




@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param


@task
def add(x, y):
    print 'Resultado= ' + str(x+y)
    return x + y


@task
def procesar():
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='designMatchQueue')

    print 'Queue'
    print str(queue.url)

    print 'Entra a procesar'
    lista_disenios = Connection().db.disenios.find({'estado' : 'En proceso'})
    print 'lista_disenios'
    print lista_disenios
    for disenio in lista_disenios:
        disenio = Connection.db.disenios.find_one({'_id' : ObjectId(disenio['_id'])})

        if disenio['estado']=='En proceso':
            Connection().db.disenios.update({"_id": ObjectId(disenio['_id'])}, {"$set": {'fechaInicioProceso': timezone.now(),
                                                                                         'fechaModificacion': timezone.now(),
                                                                                         'estado': 'Procesando'}})

            print 'Procesando disenio... ' + str(disenio['disenioOriginal'])
            imageS3 = default_storage.open(disenio['disenioOriginal'])
            imagenOrg = Image.open(imageS3)
            #Redimensionar
            imagenPro = imagenOrg.resize((800,600),Image.ANTIALIAS)
            #Marca de agua
            watermark = Image.new("RGBA", imagenPro.size)
            waterdraw = ImageDraw(watermark, "RGBA")
            font = ImageFont.truetype("fonts/DejaVuSans.ttf", 25)
            waterdraw.text((50,50), disenio['nombres'] + ' ' + disenio['apellidos'] + ' ' + str(disenio['fechaCreacion']), (255,255,255), font=font)
            watermask = watermark.convert("L").point(lambda x: min(x, 100))
            watermark.putalpha(watermask)
            imagenPro.paste(watermark, None, watermark)
            #Nueva extension
            nombreImagen = disenio['disenioOriginal'].split('/')[1].split('.')[0]
            #time.sleep(90)
            nuevaRuta = 'diseniosProcesados/' + nombreImagen + '_procesada.png'
            #Guardar local
            #imagenPro.save(nuevaRuta)
            #Guardar en base
            fh = default_storage.open(nuevaRuta, 'w')
            imagenPro.save(fh)
            fh.close()
            print "Imagen guardada en S3 " + nuevaRuta

            Connection().db.disenios.update({"_id": ObjectId(disenio['_id'])}, {"$set": {'disenioProcesado': nuevaRuta,
                                                                                         'fechaModificacion': timezone.now(),
                                                                                         'estado': 'Disponible'}})

            prompt(disenio)


def prompt(dise):

    fromaddr = os.environ.get('SES_SMTP_FROM_ADDRESS')
    toaddrs  = dise['email']
    diseName = str(dise['disenioOriginal']).split('/')[1].split('.')[0]
    subject = "Un nuevo diseno ha sido procesado! - " + str(diseName)

    text = ("Estimad@ " + str(dise['nombres']) + "\n\nEl diseno " + str(diseName) + ", creado el " + str(dise['fechaCreacion']) + ", ya ha sido procesado y publicado en la pagina del proyecto.").encode("utf8")

    message = 'Subject: %s\n\n%s' % (subject, text)

    #Credentials
    smtp_server = os.environ.get('SES_SMTP_SERVER')
    smtp_username = os.environ.get('SES_SMTP_USERNAME')
    smtp_password = os.environ.get('SES_SMTP_PASSWORD')
    smtp_port = os.environ.get('SES_SMTP_PORT')

    try:
        server = smtplib.SMTP(
            host = smtp_server,
            port = smtp_port,
            timeout = 60
        )
        server.set_debuglevel(10)
        server.starttls()
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(fromaddr, toaddrs, message)
        print server.quit()
        print "Successfully sent email"
    except smtplib.SMTPException:
       print "Error: unable to send email"

@task
def restaurar_disenios():
    print 'Entra a restaurar'
    lista_disenios = Connection().db.disenios.find({'estado' : 'Procesando'})
    for disenio in lista_disenios:
        print 'Restaurando disenio... ' + str(disenio['disenioOriginal'])
        currTime = datetime.datetime.now()
        diff = (currTime - disenio['fechaInicioProceso']).seconds
        if diff > 60:
            Connection().db.disenios.update({"_id": ObjectId(disenio['_id'])}, {"$set": {'fechaInicioProceso': None,
                                                                                         'fechaModificacion': timezone.now(),
                                                                                         'estado': 'En proceso'}})


@task
def procesar_disenio(idDisenio):

    print 'Entra a procesar disenio'
    disenio = Connection.db.disenios.find_one({'_id' : ObjectId(idDisenio)})

    if disenio['estado']=='En proceso':
        Connection().db.disenios.update({"_id": ObjectId(disenio['_id'])}, {"$set": {'fechaInicioProceso': timezone.now(),
                                                                                     'fechaModificacion': timezone.now(),
                                                                                     'estado': 'Procesando'}})

        print 'Procesando disenio... ' + str(disenio['disenioOriginal'])
        imageS3 = default_storage.open(disenio['disenioOriginal'])
        imagenOrg = Image.open(imageS3)
        #Redimensionar
        imagenPro = imagenOrg.resize((800,600),Image.ANTIALIAS)
        #Marca de agua
        watermark = Image.new("RGBA", imagenPro.size)
        waterdraw = ImageDraw(watermark, "RGBA")
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", 25)
        waterdraw.text((50,50), disenio['nombres'] + ' ' + disenio['apellidos'] + ' ' + str(disenio['fechaCreacion']), (255,255,255), font=font)
        watermask = watermark.convert("L").point(lambda x: min(x, 100))
        watermark.putalpha(watermask)
        imagenPro.paste(watermark, None, watermark)
        #Nueva extension
        nombreImagen = disenio['disenioOriginal'].split('/')[1].split('.')[0]
        #time.sleep(90)
        nuevaRuta = 'diseniosProcesados/' + nombreImagen + '_procesada.png'
        #Guardar local
        #imagenPro.save(nuevaRuta)
        #Guardar en base
        fh = default_storage.open(nuevaRuta, 'w')
        imagenPro.save(fh)
        fh.close()
        print "Imagen guardada en S3 " + nuevaRuta

        Connection().db.disenios.update({"_id": ObjectId(disenio['_id'])}, {"$set": {'disenioProcesado': nuevaRuta,
                                                                                     'fechaModificacion': timezone.now(),
                                                                                     'estado': 'Disponible'}})

        prompt(disenio)


