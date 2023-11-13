from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.models import (
    Project,
    NotificationProject,
    User
)
from project.serializers import (
    ProjectSerializer,
    NotificationProjectSerializer
)
from django.core.paginator import Paginator
from django.db.models import Q

import math


def paginate(page_size, page_number, query):
    paginator = Paginator(query, page_size)
    page_obj = paginator.get_page(page_number)
    serializer = ProjectSerializer(page_obj, many=True)
    total_items = paginator.count
    max_pages = math.ceil(total_items / int(page_size))
    data = {
        'data': serializer.data if max_pages >= int(page_number) else {},
        'totalItems': total_items
    }
    return data


def project_production_status(project_status, user=None):
    status_mapping = {
        'Active': ['Started', 'In design'],
        'My_Active': ['Started', 'In design'],
        'My_Completed': ['Completed'],
        'My_Suspended': ['Suspended'],
        'Suspended': ['Suspended'],
        'Completed': ['Completed'],
    }

    status_filter = status_mapping.get(project_status)

    if status_filter is None:
        return None

    if user and not user.is_staff and project_status.startswith('My'):
        status_filter = None

    return status_filter


def project_secretariat_status(project_status, user=None):
    status_mapping = {
        'YES': ['YES', 'YES (LACK OF INVOICE)'],
        'NO': ['NO'],
    }

    status_filter = status_mapping.get(project_status)

    if status_filter is None:
        return None

    if user and not user.is_staff:
        status_filter = None

    return status_filter


def search_projects(params, user):
    status = params.get('status')
    search = params.get('search')
    status_filter = project_production_status(status, user)

    if status_filter is None:
        info = {
            'message': 'There is no such project status '
                       'or you do not have permission'
        }
        return Response(info, status=status.HTTP_404_NOT_FOUND)

    queryset = Project.objects.filter(
        Q(status__in=status_filter) &
        (Q(number__icontains=search) |
         Q(name__icontains=search) |
         Q(order_number__icontains=search))
    )

    if user and not user.is_staff and status.startswith('My'):
        queryset = queryset.filter(manager=user)

    serializer = ProjectSerializer(queryset, many=True)
    return serializer.data


def search_secretariat_projects(params, user):
    status = params.get('status')
    search = params.get('search')
    status_filter = project_secretariat_status(status, user)

    if status_filter is None:
        info = {
            'message': 'There is no such project status '
                       'or you do not have permission'
        }
        return Response(info, status=status.HTTP_404_NOT_FOUND)

    queryset = Project.objects.filter(
        Q(invoiced__in=status_filter) &
        Q(secretariat=True) &
        (Q(number__icontains=search) |
         Q(name__icontains=search) |
         Q(order_number__icontains=search))
    )

    serializer = ProjectSerializer(queryset, many=True)
    return serializer.data


def filter_production_projects(queryset, params, user=None):
    project_status = params.get('status')
    status_filter = project_production_status(project_status, user)

    if status_filter is None:
        info = {'message': 'There is no such project status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)

    if status_filter and project_status.startswith('My'):
        queryset = queryset.filter(manager=user, status__in=status_filter)
    else:
        queryset = queryset.filter(status__in=status_filter)

    status_paginate = ['Completed', 'Suspended',
                       'My Suspended', 'My Completed']

    if project_status in status_paginate:
        page_size = params.get('page_size')
        page_number = params.get('page_number')
        data = paginate(page_size, page_number, queryset)
        return data

    serializer = ProjectSerializer(queryset, many=True)
    data = serializer.data
    return data


def filter_secretariat_projects(queryset, params, user=None):
    invoice_status = params.get('status')
    status_filter = project_secretariat_status(invoice_status, user)

    if status_filter is None:
        info = {'message': 'There is no such project status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    else:
        queryset = queryset.filter(
            invoiced__in=status_filter,
            secretariat=True
        )

    status_paginate = ['YES', 'YES (LACK OF INVOICE)']

    if invoice_status in status_paginate:
        page_size = params.get('page_size')
        page_number = params.get('page_number')
        data = paginate(page_size, page_number, queryset)
        return data

    serializer = ProjectSerializer(queryset, many=True)
    data = serializer.data
    return data


def send_message(group, type, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group,
        {
            'type': type,
            'message': message,
        }
    )


def notification_ws(data):
    project = Project.objects.get(id=data['id'])
    users = User.objects.all()
    content = f'Project ({project}) has been added'

    for user in users:
        notification = NotificationProject(
            user=user,
            project=project,
            content=content,
            type='project'
        )
        notification.save()

        noti_ser = NotificationProjectSerializer(notification, many=False)
        message = {
            'data': noti_ser.data,
        }
        group = f'user_project_noti_{user.id}'
        type = 'project_noti'
        send_message(group, type, message)


def manage_project_ws(data, destiny):
    users = User.objects.all()

    for user in users:
        message = {
            'data': data,
            'type': destiny
        }
        group = f'project_manage_{user.id}'
        type = 'project_manage'
        send_message(group, type, message)


