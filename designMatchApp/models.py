from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.forms import ModelForm
from django.utils import timezone


class Administrador(models.Model):
    _id = models.CharField(max_length=200)
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    nombre_empresa = models.CharField(max_length=200)
    url_empresa = models.CharField(max_length=1000, null=True)

    def __unicode__(self):
        return self.username


class UserForm(ModelForm):
    username = forms.CharField(max_length=50)
    # first_name = forms.CharField(max_length=20)
    # last_name = forms.CharField(max_length=20)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def clean_username(self):
        # comprueba que no exista el usuario en base de datos
        username = self.cleaned_data['username']
        if User.objects.filter(username=username):
            raise forms.ValidationError('Nombre de usuario ya registrado.')

        return username

    def clean_email(self):
        # comprueba que no exista un email igual en base de datos
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('Ya existe un email igual registrado.')

        return email

    def clean_password2(self):
        # comprueba que password y password2 sean iguales
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password != password2:
            raise forms.ValidationError('Las claves no coinciden.')

        return password2


class AdministradorForm(ModelForm):
    class Meta:
        model = Administrador
        fields = ['nombre_empresa', 'url_empresa']


class Proyecto(models.Model):
    _id = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200, null=False)
    descripcion = models.CharField(max_length=1000, null=False)
    valor_estimado = models.DecimalField(decimal_places=2, max_digits=10)
    fecha_creacion = models.DateTimeField(default=timezone.now, null=False)
    fecha_modificacion = models.DateTimeField(null=True)
    usuario = models.CharField(max_length=200)
    username = models.CharField(max_length=50)


class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ['_id', 'nombre', 'descripcion', 'valor_estimado', 'fecha_creacion', 'fecha_modificacion', 'usuario', 'username']


class Disenio(models.Model):
    _id = models.CharField(max_length=200)
    nombres = models.CharField(max_length=100, null=False)
    apellidos = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=False)
    disenio_original = models.ImageField(upload_to='diseniosOriginales', null=False)
    disenio_procesado = models.ImageField(upload_to='diseniosProcesados', null=True)
    precio_solicitado = models.DecimalField(decimal_places=2, max_digits=10)
    fecha_creacion = models.DateTimeField(default=timezone.now, null=False)
    estado = models.CharField(max_length=20, default="En proceso", null=False)
    proyecto = models.CharField(max_length=200)


class DisenioForm(ModelForm):
    class Meta:
        model = Disenio
        fields = ['_id', 'nombres', 'apellidos', 'email', 'disenio_original', 'precio_solicitado', 'fecha_creacion', 'estado', 'proyecto']

