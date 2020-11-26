from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import ProtocolProject
import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_protocols_by_project(request):
    """
    :param request: user, protocol, project
    :return: message, state
    """
    data = request.data
    logging.info('Se pidieron los protocolos para el projecto %s', data['project'])
    try:
        #ACA deberiamos setear los resultados y aprobados todos en null, porque podria volver a empezar todo
        protocol_projects = ProtocolProject.objects.filter(project=data['project'], project__active=True).order_by("protocol__order")
        protocols_list = {}
        if len(protocol_projects) > 0:
            for index, protocol_p in enumerate(protocol_projects, start=1):
                protocols_list[index] = {'id': protocol_p.protocol.id,
                        'nombre': protocol_p.protocol.name,
                        'orden': protocol_p.protocol.order,
                        'es_local': protocol_p.protocol.is_local
                    }
            logging.debug('Se deberan cargar los siguientes protocolos: %s', protocols_list)
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
    :param request: user, protocol, project
    :return: message, state
    """
    data = request.data
    logging.info('Se solicitó la información proyecto %s en el caso %s', data['project'], data['processInstanceId'])
    try:
        protocol_project = ProtocolProject.objects.filter(project=data['project'], result__isnull=True, approved__isnull=True).order_by("protocol__order").first()
        if protocol_project:
            protocol_project.running_task = str(data['activityInstanceId'])
            return JsonResponse({"id": str(protocol_project.id),
                                "responsible": protocol_project.responsible,
                                "order": protocol_project.protocol.order,
                                "is_local": protocol_project.protocol.is_local,
                                "last": "true"
                               })
        # Setear la variable last en true si es el ultimo.
        else:
            logging.debug('Los protocolos ya han sido todos procesados.')
            return JsonResponse({'error': 'Los protocolos ya han sido todos procesados.', 'status': status.HTTP_400_BAD_REQUEST})
    except ProtocolProject.DoesNotExist:
        logging.debug('Otro error que todavia no se.')
        return JsonResponse({'error': 'Otro error que todavia no se', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


def get_result_by_protocol(protocol, activities_checked):
    # activities_checked = 0
    logging.info('Se pidió el resultado del protocolo %s', protocol.id)
    total = protocol.activities.count()
    logging.info('El total de actividades era %s, la cantidad de actividades aprobadas fue %s', total, activities_checked)
    # for activity in protocol.activityprotocol_set.all():
    #     print(activity.approved)
    #     activities_checked += 1 if activity.approved else 0

    points = activities_checked * 100 / total
    logging.info('Los puntos necesarios eran %s, los puntos obtenidos fueron %s', protocol.points, points)
    logging.info('El resultado del protocolo fue %s', protocol.points <= points)
    return protocol.points <= points


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_result_remote_protocol(request):
    """
    :param request: protocol_project, approved
    :return: message, state
    """
    data = request.data

    try:
        protocol_project = ProtocolProject.objects.get(pk=request.data["protocol_project"])
        if protocol_project:
            protocol_project.approved = request.data['approved']
            protocol_project.save()
            return JsonResponse(
                {'message': "El protocolo fue actualizado", 'status': status.HTTP_200_OK})
    except ProtocolProject.DoesNotExist:
        logging.debug('Otro error que todavia no se.')
        return JsonResponse({'error': 'Otro error que todavia no se', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        logging.debug('Excepcion: %s', str(e))
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})