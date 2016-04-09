from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^crear/$', views.crear_proyecto, name='crearProyecto'),
    url(r'^editar/(?P<pk>\w+)/$', views.editar_proyecto, name='editarProyecto'),
    url(r'^borrar/(?P<pk>\w+)/$', views.borrar_proyecto, name='borrarProyecto'),
    url(r'^registrarAdministrador', views.registrar_administrador, name='registrarAdministrador'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^isLogged$', views.is_logged_view, name='isLogged'),
    url(r'^verProyectos', views.ver_proyectos, name='verProyectos'),
    url(r'^verDiseniosEmpresa/(?P<nombre>\w+)/(?P<codigo>\w+)/$', views.ver_disenios_empresa, name='verDiseniosEmpresa'),
    url(r'^agregarProyecto', views.agregar_proyecto, name='agregarProyecto'),
    url(r'^agregarAdministrador', views.agregar_administrador, name='agregarAdministrador'),
    url(r'^ingresar', views.ingresar, name='ingresar'),
    url(r'^actualizarProyecto', views.actualizar_proyecto, name='actualizarProyecto'),
    url(r'^crearDisenio/(?P<pk>\w+)/$', views.crear_disenio, name='crearDisenio'),
    url(r'^agregarDisenio', views.agregar_disenio, name='agregarDisenio'),
    url(r'^detallesProyecto/(?P<pk>\w+)/$', views.ver_detalles_proyecto, name='detallesProyecto'),
    url(r'^diseniosProyecto/(?P<pk>\w+)/$', views.ver_disenios_proyecto, name='diseniosProyecto'),
    url(r'^consultaDisenios/(?P<pk>\w+)/(?P<ini>\d+)/(?P<fin>\d+)/$', views.consultar_disenios, name='consultaDisenios'),
    url(r'^consultaNumDisenios/(?P<pk>\w+)/$', views.consultar_numero_disenios, name='consultaNumeroDisenios'),
    url(r'^usuario$', views.consultar_usuario_logueado, name='consultarAdministrador'),
]
