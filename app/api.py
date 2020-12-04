import logging

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import ProtocolProject, Project, Notification

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_protocols_by_project(request):
    """
    :param request: project
    :return: list of protocols
    """
    data = request.data
    logging.info('Se pidieron los protocolos para el projecto %s', data['project'])
    try:
        protocol_projects = ProtocolProject.objects.filter(project=data['project'], project__active=True).order_by(
            "protocol__order")
        protocols_list = {}
        if len(protocol_projects) > 0:
            for index, protocol_p in enumerate(protocol_projects, start=1):
                protocols_list[index] = {'id': protocol_p.protocol.id,
                                         'nombre': protocol_p.protocol.name,
                                         'orden': protocol_p.protocol.order,
                                         'es_local': protocol_p.protocol.is_local
                                         }
            logging.debug('Se deberán cargar los siguientes protocolos: %s', protocols_list)
            return JsonResponse(
                {'protocols': protocols_list})
        else:
            logging.debug('El proyecto no está activo.')
            return JsonResponse({'error': 'El proyecto no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except ProtocolProject.DoesNotExist:
        logging.debug('El proyecto no existe o no está activo.')
        return JsonResponse({'error': 'El proyecto no existe o no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_protocol_to_run(request):
    """

    :param request: project, processInstanceId, activityInstanceId
    :return: protocol to JSON
    """
    data = request.data
    logging.info('Se solicitó la información proyecto %s en el caso %s', data['project'], data['processInstanceId'])
    try:
        protocol_project = ProtocolProject.objects.filter(project=data['project'], result__isnull=True,
                                                          approved__isnull=True).order_by("protocol__order").first()
        if protocol_project:
            protocol_project.running_task = str(data['activityInstanceId'])
            protocol_project.save()
            return JsonResponse({"id": str(protocol_project.id),
                                 "responsible": protocol_project.responsible,
                                 "is_local": protocol_project.protocol.is_local,
                                 "protocol": str(protocol_project.protocol.id),
                                 "name": protocol_project.protocol.name
                                 })
            logging.info('Se envió a procesar el protocolo %s', protocol_project.id)
        else:
            logging.debug('Los protocolos ya han sido todos procesados.')
            return JsonResponse(
                {'error': 'Los protocolos ya han sido todos procesados.', 'status': status.HTTP_400_BAD_REQUEST})
    except ProtocolProject.DoesNotExist:
        logging.debug('Otro error que todavia no se.')
        return JsonResponse({'error': 'Otro error que todavia no se', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_processing(request):
    """
    Se setean en null las variables que determinan si el protocolo fue ejecutado y
    finalizó su ejecución.
    Se devuelve el id del protocolo en el proyecto que debe ejecutarse en último lugar
    :param request: project, processInstanceId
    :return: status, last
    """
    data = request.data
    logging.info('Se solicitó iniciar el procesamiento del proyecto %s en el caso %s', data['project'],
                 data['processInstanceId'])
    try:
        ProtocolProject.objects.filter(project=data['project']).update(result=None, approved=None, running_task='')
        protocol_project = ProtocolProject.objects.filter(project=data['project']).order_by("-protocol__order").first()
        if protocol_project:
            return JsonResponse({"last": str(protocol_project.id)})
    except ProtocolProject.DoesNotExist:
        logging.debug('No existen protocolos para este proyecto.')
        return JsonResponse(
            {'error': 'No existen protocolos para este proyecto.', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


def get_result_by_protocol(protocol_project, activities_checked):
    logging.info('Se pidió el resultado del protocol_project %s', protocol_project.id)
    total = protocol_project.protocol.activities.count()
    logging.info('El total de actividades era %s, la cantidad de actividades aprobadas fue %s', total,
                 activities_checked)

    points = activities_checked * 100 / total
    logging.info('Los puntos necesarios eran %s, los puntos obtenidos fueron %s', protocol_project.protocol.points,
                 points)
    protocol_project.result = points
    approved = protocol_project.protocol.points <= points
    if approved:
        protocol_project.approved = True
    protocol_project.save()
    notify(protocol_project.responsible, False, protocol_project.project, protocol_project.protocol)
    if not approved:
        notify(protocol_project.project.project_manager, True, protocol_project.project, protocol_project.protocol)
    logging.info('El resultado del protocolo fue %s', "aprobado" if approved else "desaprobado")
    return approved


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_result_remote_protocol(request, pk):
    """
    :param request: approved, points
    :return: message, state
    """
    data = request.data
    try:
        protocol_project = ProtocolProject.objects.get(pk=pk)
        if protocol_project:
            protocol_project.approved = data["approved"]
            protocol_project.result = data["points"]
            protocol_project.save()
            notify(protocol_project.responsible, False, protocol_project.project, protocol_project.protocol)
            if not data["approved"]:
                notify(protocol_project.project.project_manager, True, protocol_project.project, protocol_project.protocol)
            return JsonResponse(
                {'message': "El protocolo fue actualizado", 'status': status.HTTP_200_OK})
    except ProtocolProject.DoesNotExist:
        logging.debug('Otro error que todavia no se.')
        return JsonResponse({'error': 'Otro error que todavia no se', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_result_project(request, pk):
    """
    :param request
    :param pk
    :return: message, state
    """
    try:
        project = Project.objects.get(pk=pk)
        if project:
            project.approved = get_result_by_project(project)
            project.active = False
            project.save()
            notify(project.project_manager, False, project)
            return JsonResponse(
                {'message': "El resultado del proyecto fue actualizado", 'approved': project.approved, 'status': status.HTTP_200_OK})
    except Project.DoesNotExist:
        logging.debug('El proyecto no existe.')
        return JsonResponse({'error': 'El proyecto no existe.', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


def get_result_by_project(project):
    logging.info('Se pidió el resultado del projecto %s', project.id)
    total = project.protocols.count()
    cant = 0
    for protocol in project.protocolproject_set.all():
        cant += 1 if protocol.approved else 0

    logging.info('El total de protocolos era %s, la cantidad de aprobados fue %s', total,
                 cant)

    approved = cant >= total / 2

    logging.info('El resultado del protocolo fue %s', "aprobado" if approved else "desaprobado")
    return approved


def notify(user_id, need_resolution, project, protocol=None):
    Notification.objects.create(
        user_id=user_id,
        need_resolution=need_resolution,
        project=project,
        protocol=protocol
    )
