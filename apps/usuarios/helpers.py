from django.db import connections
from django.contrib.auth.models import User, Group
from .models import Perfil


def sincronizar_usuarios():
    cursor = connections['inatec'].cursor()
    sql = 'select usuario, id_area, id_direccion, id_centro from admon.vw_sincronizar_usuarios'
    cursor.execute(sql=sql)
    result = cursor.fetchall()
    cursor.close()
    for el in result:
        usuario = User.objects.filter(username=el[0]).first()
        if usuario:
            perfil = Perfil.objects.filter(usuario=usuario).first()
            perfil.id_area = el[1]
            perfil.id_direccion = el[2]
            perfil.id_centro = el[3]
            perfil.save()


def verificar_permiso_administrador(usuario):
    return True if usuario.is_superuser or usuario.groups.filter(name__in=['administrador', ]).exists() else False


def verificar_permiso_login(usuario):
    return True if usuario.is_superuser or usuario.groups.filter(
        name__in=['administrador', 'solicitante']).exists() else False


def obtener_usuarios():
    return User.objects.filter(email__contains='@inatec.edu.ni')


def obtener_roles(usuario):
    roles = []
    for grupo in usuario.groups.all():
        roles.append(grupo.name)
    return roles


def obtener_correos_administradores():
    grupos = Group.objects.filter(name__in=['administrador', ])
    correos = []
    for grupo in grupos:
        usuarios = grupo.user_set.filter(email__contains='@inatec.edu.ni')
        for usuario in usuarios:
            correos.append(usuario.email)
    return correos
