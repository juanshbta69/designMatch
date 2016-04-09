import json

from pprint import pprint

# from django.contrib.auth.models import User
from bson import ObjectId

from django.core.cache import cache
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils import timezone
from mongoAuthApp.DBUtils import Connection
from mongoAuthApp.session import Session
from mongoAuthApp.cookiesUtils import set_cookie, get_cookie
from batchApp.tasks import procesar_disenio

from .models import Proyecto, Administrador, Disenio
from django.contrib.auth import authenticate, logout, login
from django.core import serializers
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

PROYECTO_TABLE_NAME = 'designMatch_proyecto'
PROYECTO_TABLE_NAME = 'designMatch_usuario'
PROYECTO_TABLE_NAME = 'designMatch_administrador'
DISENIOS_ORIGINALES = 'diseniosOriginales'


@csrf_exempt
def index(request):
    username = get_cookie(request, 'userId')
    user = Session.verify_current_session(username)

    lista_proyectos = []

    if user['isverify']:
        lista_proyectos = consultar_proyectos(username)
        print 'lista_proyectos'
        print lista_proyectos

    #    if request.user.is_authenticated():
    #        lista_proyectos = Proyecto.objects.filter(usuario=request.user)
    #    else:
    #        lista_proyectos = Proyecto.objects.all()

    return HttpResponse(serializers.serialize("json", lista_proyectos))


# LOGIN / LOGOUT

@csrf_exempt
def validate_login(username, password):
    connection = Connection()

    user_count = connection.db.users.find({"username": username, "password": password}).count()

    if user_count > 0:
        return True
    else:
        return False


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        json_user = json.loads(request.body)
        username = json_user['username']
        password = json_user['password']

        if validate_login(username, password):
            Session().do_login(username)
            ctx = {"mensaje": "ok"}
            mensaje = "ok"
            # response = render_to_response("designMatchApp/login.html",json.dumps(ctx),content_type="application/json",status=200)
            response = JsonResponse({'mensaje': mensaje}, status=200)
            set_cookie(response, 'userId', username)
            return response
        else:
            ctx = {"mensaje": "Nombre de usuario o clave no valido."}
            mensaje = 'Nombre de usuario o clave no valido.'
            # response = render_to_response("designMatchApp/login.html",json.dumps(ctx),content_type="application/json",status=401)
            response = JsonResponse({'mensaje': mensaje}, status=401)
            return response

            # return HttpResponse({'mensaje': mensaje, 'response': response})

@csrf_exempt
def logout_view(request):
    user_id = get_cookie(request,'userId')
    response = HttpResponseRedirect("/")
    Session().do_logout(response,user_id)
    #logout(request)
    return JsonResponse({'mensaje': 'ok'})


@csrf_exempt
def consultar_usuario_logueado(request):
    administrador = Administrador()

    username = get_cookie(request, 'userId')
    user = Session.verify_current_session(username)

    if user['isverify']:
        loggedUser = Connection().db.users.find_one({'username': username})
        administrador._id = loggedUser['_id']
        administrador.username = loggedUser['username']
        administrador.nombre_empresa = loggedUser['nombreEmpresa']
        administrador.url_empresa = loggedUser['urlEmpresa']
        administrador.email = loggedUser['email']
        # administrador.username = loggedUser.username


        # if request.user is not None:
        # print request.user
        # usuario = User.objects.get_by_natural_key(request.user)
        # if usuario.is_authenticated():
        #    administrador = Administrador.objects.get(user=usuario)

    return HttpResponse(serializers.serialize("json", [administrador]))


@csrf_exempt
def is_logged_view(request):
    username = get_cookie(request, 'userId')
    user = Session.verify_current_session(username)

    if user['isverify']:
        mensaje = 'ok'
    else:
        mensaje = 'no'

    return JsonResponse({'mensaje': mensaje})

# ADMINISTRADORES

@csrf_exempt
def registrar_administrador(request):
    if request.method == 'POST':
        json_user = json.loads(request.body)
        username = json_user['username']
        password = json_user['password']
        email = json_user['email']
        nombre_empresa = json_user['enterprise_name']

        user = {
            'email': email,
            'username': username,
            'nombreEmpresa': nombre_empresa,
            'password': password,
            'proyectos': []
        }

        id_admin = Connection().db.users.insert(user)

        url_empresa = nombre_empresa.replace(" ", "") + "/" + scdtr(id_admin) + "/"
        Connection().db.users.update({"_id": id_admin}, {"$set": {'urlEmpresa': url_empresa}})

        return HttpResponse(json.dumps({'email': email, 'username': username, 'nombreEmpresa': nombre_empresa}))

@csrf_exempt
def consultar_administrador(username):
    user = Session.verify_current_session(username)
    administrador = Administrador()

    if user['isverify']:
        loggedUser = Connection().db.users.find_one({'username': username})
        administrador._id = loggedUser['_id']
        administrador.username = loggedUser['username']
        administrador.nombre_empresa = loggedUser['nombreEmpresa']
        administrador.url_empresa = loggedUser['urlEmpresa']
        administrador.email = loggedUser['email']

    return administrador


# PROYECTOS

@csrf_exempt
def consultar_proyectos(username):
    proyectos_ids = Connection().db.users.find_one({"username": username})['proyectos']
    proyectos = consultar_proyectos_por_ids(proyectos_ids)
    return proyectos


@csrf_exempt
def consultar_proyectos_por_ids(proyectos_ids):
    proyectos = []
    for current_proyecto_id in proyectos_ids:
        proyecto = consultar_proyecto(current_proyecto_id['_id'])
        proyectos.append(proyecto)

    return proyectos


@csrf_exempt
def consultar_proyecto(id):
    proyectoDB = Connection().db.proyectos.find_one({'_id': ObjectId(id)})
    proyecto = Proyecto()

    if proyectoDB:
        proyecto._id = id
        proyecto.nombre = proyectoDB['nombre']
        proyecto.descripcion = proyectoDB['descripcion']
        proyecto.valor_estimado = proyectoDB['valorEstimado']
        proyecto.fecha_creacion = proyectoDB['fechaCreacion']
        proyecto.usuario = proyectoDB['usuario']
        proyecto.username = proyectoDB['username']
        # proyecto.disenios = []
        return proyecto


@csrf_exempt
def crear_proyecto(request):
    if request.method == 'POST':
        proyecto = Proyecto()

        username = get_cookie(request, 'userId')
        user = Session.verify_current_session(username)
        admin = consultar_administrador(username)

        if user['isverify']:
            proyecto = Proyecto(nombre=request.POST['nombre'],
                                descripcion=request.POST['descripcion'],
                                valor_estimado=request.POST['valor_estimado'],
                                usuario=admin._id,
                                username=admin.username)

            proyectoDB = {
                'nombre': proyecto.nombre,
                'descripcion': proyecto.descripcion,
                'valorEstimado': proyecto.valor_estimado,
                'fechaCreacion': proyecto.fecha_creacion,
                'usuario': admin._id,
                'username': admin.username,
                'disenios': []
            }

            id_proyecto = Connection().db.proyectos.insert(proyectoDB)

            proyectos = Connection().db.users.find_one({"username": username})['proyectos']
            proyectos.append({"_id": id_proyecto})
            Connection().db.users.update({"username": username}, {"$set": {'proyectos': proyectos}})

            return HttpResponse(serializers.serialize("json", [proyecto]))
        else:
            return HttpResponse(serializers.serialize("json", [proyecto]))


@csrf_exempt
def editar_proyecto(request, pk):
    proyecto = Proyecto()
    if request.method == 'POST':
        json_proyecto = json.loads(request.body)
        nombre = json_proyecto['nombre']
        descripcion = json_proyecto['descripcion']
        valor_estimado = json_proyecto['valor_estimado']

        proyecto._id = pk
        proyecto.nombre = nombre
        proyecto.descripcion = descripcion
        proyecto.valor_estimado = valor_estimado
        proyecto.fecha_modificacion = timezone.now()

        Connection().db.proyectos.update({"_id": ObjectId(proyecto._id)}, {"$set": {'nombre': proyecto.nombre,
                                                                                    'descripcion': proyecto.descripcion,
                                                                                    'valorEstimado': proyecto.valor_estimado,
                                                                                    'fechaModificacion': proyecto.fecha_modificacion}})

    return HttpResponse(serializers.serialize("json", [proyecto]))


@csrf_exempt
def borrar_proyecto(request, pk):
    if request.method == 'POST':
        proyecto = consultar_proyecto(pk)

        result = Connection().db.proyectos.remove({"_id": ObjectId(proyecto._id)})

        Connection().db.users.update({"_id": ObjectId(proyecto.usuario)},
                                     {"$pull": {'proyectos': {"_id": ObjectId(proyecto._id)}}})

        mensaje = 'ok'
    else:
        mensaje = 'no'

    return JsonResponse({'mensaje': mensaje})


# DISENIOS

def ver_disenios_empresa(request, nombre, codigo):
    if request.is_ajax():
        proyectos_ids = Connection().db.users.find_one({"_id": ObjectId(codigo)})['proyectos']
        proyectos = consultar_proyectos_por_ids(proyectos_ids)

        return HttpResponse(serializers.serialize("json", proyectos))

    return render(request, "designMatchApp/index_diseniadores.html")


@csrf_exempt
def crear_disenio(request, pk):
    if request.method == 'POST':
        disenio = Disenio()
        print 'Disenio URL '
        print request.FILES['disenio']
        disenio = Disenio(nombres=request.POST['nombres'],
                          apellidos=request.POST['apellidos'],
                          email=request.POST['email'],
                          disenio_original=request.FILES['disenio'],
                          precio_solicitado=request.POST['precioSolicitado'],
                          proyecto=pk)

        currTime = str(timezone.now().strftime('%Y%m%d%H%M%S'))

        disenioDB = {
            'nombres': disenio.nombres,
            'apellidos': disenio.apellidos,
            'email': disenio.email,
            'disenioOriginal': 'diseniosOriginales/' + currTime + '_' + str(request.FILES['disenio']),
            'precioSolicitado': disenio.precio_solicitado,
            'estado': disenio.estado,
            'fechaCreacion': disenio.fecha_creacion,
            'proyecto': disenio.proyecto
        }

        id_disenio = Connection().db.disenios.insert(disenioDB)

        disenios = Connection().db.proyectos.find_one({"_id": ObjectId(pk)})['disenios']
        disenios.append({"_id": id_disenio})
        Connection().db.proyectos.update({"_id": ObjectId(pk)}, {"$set": {'disenios': disenios}})

#       img = Image.open(request.FILES['disenio'])
        print 'diseniosOriginales/' + currTime + '_' + str(request.FILES['disenio'])
#        img.save('diseniosOriginales/' + str(request.FILES['disenio']))

        data = request.FILES['disenio']
        ruta = 'diseniosOriginales/' + currTime + '_' + str(data)
        path = default_storage.save(ruta, File(data))

        procesar_disenio.delay(str(id_disenio))

        mensaje = 'ok'
    else:
        mensaje = 'error'

    # return HttpResponse(serializers.serialize("json", [disenio]))
    return JsonResponse({'mensaje': mensaje})


@csrf_exempt
def consultar_disenios(request, pk, ini, fin):
    print 'ini ' + str(ini)
    print 'fin ' + str(fin)
    disenios_ids = Connection().db.proyectos.find_one({"_id": ObjectId(pk)})['disenios']
    disenios = consultar_disenios_por_ids(disenios_ids)[int(ini):int(fin)]
    for disenio in disenios:
        pprint('Disenio... ' + str(disenio.disenio_original))
    context = {'disenios': disenios}
    return HttpResponse(serializers.serialize("json", disenios))


@csrf_exempt
def consultar_disenios_por_ids(disenios_ids):
    disenios = []
    for current_disenio_id in disenios_ids:
        disenio = consultar_disenio(current_disenio_id['_id'])
        disenios.append(disenio)

    return disenios


@csrf_exempt
def consultar_disenio(id):
    disenioDB = Connection().db.disenios.find_one({'_id': ObjectId(id)})
    disenio = Disenio()

    if disenioDB:
        disenio._id = id
        disenio.nombres = disenioDB['nombres']
        disenio.apellidos = disenioDB['apellidos']
        disenio.email = disenioDB['email']
        disenio.disenio_original = disenioDB['disenioOriginal']
        disenio.precio_solicitado = disenioDB['precioSolicitado']
        disenio.estado = disenioDB['estado']
        disenio.fecha_creacion = disenioDB['fechaCreacion']
        if disenio.estado == 'Disponible':
            disenio.disenio_procesado = disenioDB['disenioProcesado']
        return disenio


@csrf_exempt
def consultar_numero_disenios(request, pk):
    disenios = Connection().db.proyectos.find_one({"_id": ObjectId(pk)})['disenios']
    numDisenios = len(disenios)

    return JsonResponse({'numDisenios': numDisenios})





def ver_proyectos(request):
    return render(request, "designMatchApp/index.html")


def ver_detalles_proyecto(request, pk):
    return render(request, "designMatchApp/detalles_proyecto.html")


def ver_disenios_proyecto(request, pk):
    return render(request, "designMatchApp/disenios_proyecto.html")


def agregar_proyecto(request):
    return render(request, "designMatchApp/proyecto_form.html")


def agregar_administrador(request):
    return render(request, "designMatchApp/registro.html")


def ingresar(request):
    return render(request, "designMatchApp/login.html")


def actualizar_proyecto(request):
    return render(request, "designMatchApp/editar_proyecto_form.html")


def agregar_disenio(request):
    return render(request, "designMatchApp/disenio_form.html")
