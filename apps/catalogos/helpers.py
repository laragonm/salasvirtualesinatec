from django.db import connections
from http import HTTPStatus
from django.conf import settings
from zoomus import ZoomClient
from .models import Sala, Area, Centro


def sincronizar_salas():
    cliente = ZoomClient(settings.ZOOM_API_KEY, settings.ZOOM_API_SECRET)
    response = cliente.user.list(page_size=settings.ZOOM_PAGE_SIZE)
    if response.status_code == HTTPStatus.OK:
        users = response.json().get('users')
        token = response.json().get('next_page_token')
        while token:
            response = cliente.user.list(page_size=settings.ZOOM_PAGE_SIZE, next_page_token=token)
            if response.status_code == HTTPStatus.OK:
                users += response.json().get('users')
        for user in users:
            sala = Sala.objects.filter(zoom_id=user['id']).first()
            if sala:
                sala.nombre = f"{user['first_name']} {user['last_name']}"
                sala.estado = obtener_estado(user)
            else:
                sala = Sala(zoom_id=user['id'], nombre=f"{user['first_name']} {user['last_name']}",
                            correo=user['email'], estado=obtener_estado(user))
            sala.save()


def obtener_estado(user):
    if user['status'] == 'active':
        return 1
    elif user['status'] == 'inactive':
        return 2
    elif user['status'] == 'pending':
        return 3
    else:
        return 99


def sincronizar_areas():
    cursor = connections['inatec'].cursor()
    sql = "select id_area, id_direccion, id_centro, nombre, estado from public.vw_sincronizar_areas where id_centro = '1000'"
    cursor.execute(sql=sql)
    result = cursor.fetchall()
    cursor.close()
    for el in result:
        area = Area.objects.filter(id_area=el[0]).first()
        if area:
            area.id_direccion = el[1]
            area.id_centro = el[2]
            area.nombre = el[3]
            area.estado = el[4]
        else:
            area = Area(id_area=el[0], id_direccion=el[1], id_centro=el[2], nombre=el[3], estado=el[4])
        area.save()


def sincronizar_centros():
    cursor = connections['inatec'].cursor()
    sql = 'select id_centro, nombre, estado from public.vw_sincronizar_centros'
    cursor.execute(sql=sql)
    result = cursor.fetchall()
    cursor.close()
    for el in result:
        centro = Centro.objects.filter(id_centro=el[0]).first()
        if centro:
            centro.nombre = el[1]
            centro.estado = el[2]
        else:
            centro = Centro(id_centro=el[0], nombre=el[1], estado=el[2])
        centro.save()
