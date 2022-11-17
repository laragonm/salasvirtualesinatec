from datetime import date, timedelta, datetime
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Max
from django_currentuser.middleware import get_current_authenticated_user
from zoomus import ZoomClient
from .models import Solicitud, Ocurrencia
from ..catalogos.models import Sala
from ..usuarios.helpers import verificar_permiso_administrador, obtener_correos_administradores


def codigo_siguiente():
    codigo = Solicitud.objects.aggregate(maximo=Max('codigo'))
    return codigo['maximo'] + 1 if codigo['maximo'] else 1


def obtener_salas():
    usuario = get_current_authenticated_user()
    if verificar_permiso_administrador(usuario):
        return Sala.objects.filter(estado=1)
    else:
        return Sala.objects.filter(usuarios__in=[usuario, ])


def obtener_fecha_inicio():
    usuario = get_current_authenticated_user()
    if verificar_permiso_administrador(usuario):
        return date.today()
    else:
        return date.today() + timedelta(days=1)


def obtener_fecha_fin():
    fecha = obtener_fecha_inicio()
    return fecha + timedelta(days=30)


def obtener_solicitudes():
    usuario = get_current_authenticated_user()
    if verificar_permiso_administrador(usuario):
        return Solicitud.objects.all()
    else:
        return Solicitud.objects.filter(usuario_grabacion=usuario)


def crear_reunion(solicitud):
    cliente = ZoomClient(settings.ZOOM_API_KEY, settings.ZOOM_API_SECRET)
    params = {
        'user_id': solicitud.sala.correo,
        'topic': solicitud.tema,
        'agenda': solicitud.agenda,
        'start_time': solicitud.fecha_inicio_utc,
        'duration': solicitud.duracion,
        'settings': {
            'waiting_room': solicitud.usa_sala_espera,
        },
    }

    if solicitud.usa_codigo_acceso:
        params['password'] = solicitud.codigo_acceso

    if solicitud.es_recurrente:
        params['type'] = 8
        params['recurrence'] = {
            'type': 2,
            'repeat_interval': 1,
            'weekly_days': solicitud.dias_display,
            'end_date_time': solicitud.fecha_fin_utc
        }

    response = cliente.meeting.create(**params)
    if response.status_code == 201:
        reunion = response.json()
        solicitud.zoom_uuid = reunion['uuid']
        solicitud.zoom_id = reunion['id']
        solicitud.zoom_start_url = reunion['start_url']
        solicitud.zoom_join_url = reunion['join_url']
        solicitud.save()

        if solicitud.es_recurrente:
            for ocurrencia in reunion['occurrences']:
                fecha = datetime.strptime(ocurrencia['start_time'], '%Y-%m-%dT%H:%M:%SZ')
                Ocurrencia(zoom_id=int(ocurrencia['occurrence_id']), fecha=fecha,
                           duracion=int(ocurrencia['duration']), solicitud=solicitud).save()


def actualizar_reunion(solicitud):
    cliente = ZoomClient(settings.ZOOM_API_KEY, settings.ZOOM_API_SECRET)
    params = {
        'id': solicitud.zoom_id,
        'start_time': solicitud.fecha_inicio_utc,
        'duration': solicitud.duracion,
        'topic': solicitud.tema,
        'agenda': solicitud.agenda
    }

    if solicitud.es_recurrente:
        params['type'] = 8
        params['recurrence'] = {
            'type': 2,
            'repeat_interval': 1,
            'weekly_days': solicitud.dias_display,
            'end_date_time': solicitud.fecha_fin_utc
        }

    response = cliente.meeting.update(**params)
    return True if response.status_code == 204 else False


def eliminar_reunion(solicitud):
    cliente = ZoomClient(settings.ZOOM_API_KEY, settings.ZOOM_API_SECRET)
    response = cliente.meeting.delete(id=solicitud.zoom_id)
    return True if response.status_code == 204 else False


def notificar_nueva_solicitud(solicitud):
    message = '<style>'
    message += '.container {display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: auto;'
    message += 'grid-template-areas: "main main main" "footer footer footer"; font-size: 14pt;'
    message += 'font-family: "calibri light", sans-serif;}'
    message += '.main {grid-area: main; margin-left: 2rem;}'
    message += '.footer {grid-area: footer;margin-left: 2rem;}'
    message += '</style>'
    message += '<div class="container"><div class="main">'
    message += f'<p>Se ha registrado una nueva solicitud <strong>{solicitud.__str__()},</strong><br/></p>'

    message += f'<p>CONVOCATORIA | <strong>{solicitud.tema}</strong> <br>'
    message += f'{solicitud.fecha_inicio_formato}, {solicitud.horario}. <br>'
    message += f'Solicitante: <strong>{solicitud.solicitante}</strong><br>'
    message += f'Revisar: <a href="{settings.WEBSITE_URL}/solicitudes">{settings.WEBSITE_URL}/solicitudes</a><br></p>'

    message += '</div><div class="footer">Saludos.<br/></div></div>'
    subject = f'Nueva solicitud de sala virtual {solicitud.__str__()}'
    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        obtener_correos_administradores()
    )
    email.content_subtype = "html"
    email.send()


def enviar_mensaje(solicitud):
    message = '<style>'
    message += '.container {display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: auto;'
    message += 'grid-template-areas: "main main main" "footer footer footer"; font-size: 14pt;'
    message += 'font-family: "calibri light", sans-serif;}'
    message += '.main {grid-area: main; margin-left: 2rem;}'
    message += '.footer {grid-area: footer;margin-left: 2rem;}'
    message += '</style>'

    message += '<div class="container"><div class="main">'
    message += f'<p>Estimad@, <strong>{solicitud.solicitante},</strong> su solicitud '
    message += f'<strong>{solicitud.__str__()}</strong> fue <strong>{solicitud.get_estado_display()}</strong></p>'

    if solicitud.estado == 2:
        message += f'<p>CONVOCATORIA | <strong>{solicitud.tema}</strong> <br><br>'

        if solicitud.es_recurrente:
            for ocurrencia in solicitud.ocurrencia_set.all().order_by('zoom_id'):
                message += f'{ocurrencia.fecha_formato}, {solicitud.horario}. <br>'
        else:
            message += f'{solicitud.fecha_inicio_formato}, {solicitud.horario}. <br>'
        message += '<br>'
        message += f'Enlace de Invitación: <a href="{solicitud.join_url_display}">{solicitud.join_url_display}</a><br>'
        message += f'ID de reunión: <strong>{solicitud.zoom_id}</strong><br>'
        if solicitud.usa_codigo_acceso:
            message += f'Clave: <strong>{solicitud.codigo_acceso}</strong><br>'
        message += '<br>'
        message += f'Tema: <strong>{solicitud.tema}</strong><br>'
        palabra = solicitud.agenda.__str__()
        agenda = palabra.replace("\n", "<br>")
        message += f'Agenda:<br>'
        message += f'<strong>{agenda}</strong><br>'
        message += f'Sala: <strong>{solicitud.sala}</strong><br>'
        message += f'Fecha: <strong>{solicitud.fecha_inicio_formato}</strong><br>'
        message += f'Hora: <strong>{solicitud.hora_inicio_formato}</strong><br>'
        message += '</p>'
        message += f'<strong>Centros Partipantes:</strong><br>'
        if solicitud.centros:
            for centro in solicitud.centros.all():
                message += f' {centro.nombre} <br>'
        message += '<br>'
        message += f'Se remite el enlace de administrador de la reunion solicitada:<br>'
        message += f'<strong>{solicitud.zoom_start_url}</strong><br>'
        message += '<br>'
    message += '</div><div class="footer">Saludos.<br/></div></div>'

    subject = f'Solicitud de sala virtual {solicitud.__str__()}'
    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [solicitud.usuario_grabacion.email, ]
    )
    email.content_subtype = 'html'
    email.send()
