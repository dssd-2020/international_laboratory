from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import ProtocolProject


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_protocols_by_project(request):
    """
    :param request: user, protocol, project
    :return: message, state
    """
    data = request.data
    print(data)
    try:
        protocols = ProtocolProject.objects.filter(project=data['project'], project__active=True)
        if len(protocols) > 0:
            protocols_list = [protocol.id for protocol in protocols]
            return JsonResponse(
                {'data': {'protocols': protocols_list}, 'status': status.HTTP_200_OK})
        else:
            return JsonResponse({'error': 'El proyecto no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except ProtocolProject.DoesNotExist:
        return JsonResponse({'error': 'El proyecto no existe o no está activo', 'status': status.HTTP_400_BAD_REQUEST})
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': status.HTTP_400_BAD_REQUEST})


def get_result_by_protocol(protocol, activities_checked):
    # activities_checked = 0
    total = protocol.activities.count()
    # for activity in protocol.activityprotocol_set.all():
    #     print(activity.approved)
    #     activities_checked += 1 if activity.approved else 0

    points = activities_checked * 100 / total
    return protocol.points <= points
