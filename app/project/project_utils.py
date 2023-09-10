from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from rest_framework.response import Response
from rest_framework import status
from core.models import Project
from project.serializers import ProjectSerializer
from django.core.paginator import Paginator

import math


def vector():
    search_vector = SearchVector('number', weight='A') + \
        SearchVector('manager__first_name', weight='A') + \
        SearchVector('manager__last_name', weight='A') + \
        SearchVector('client__name', weight='A') + \
        SearchVector('deadline', weight="B") + \
        SearchVector('priority', weight="C")
    return search_vector


def paginate(page_size, page_number, query):
    paginator = Paginator(query, page_size)
    page_obj = paginator.get_page(page_number)
    serializer = ProjectSerializer(page_obj, many=True)
    total_items = paginator.count
    max_pages = math.ceil(total_items / int(page_size))
    ser_data = serializer.data if max_pages >= int(page_number) else {}
    data = {
        'data': ser_data,
        'totalItems': total_items
    }
    return data


def get_project_status(project_status, user=None):
    if project_status == 'Active':
        status_filter = ['Started', 'In design']
    elif project_status == 'My Active':
        status_filter = ['Started', 'In design']
    elif project_status == 'My Completed':
        status_filter = ['Completed']
    elif project_status == 'My Suspended':
        status_filter = ['Suspended']
    elif project_status == 'Suspended':
        status_filter = ['Suspended']
    elif project_status == 'Completed':
        status_filter = ['Completed']
    else:
        status_filter = None

    if status_filter is None:
        return None

    if user and not user.is_staff:
        if project_status.startswith('My'):
            status_filter = None

    return status_filter


def search_projects(search_phase, project_status, user=None):
    status_filter = get_project_status(project_status, user)

    if status_filter is None:
        return Response({'message': 'There is no such project status \
                          or you do not have permission'},
                        status=status.HTTP_404_NOT_FOUND)

    search_vector = vector()
    search_query = SearchQuery(search_phase)

    project_queryset = Project.objects.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(rank__gte=0.1)

    if status_filter:
        project_queryset = project_queryset.filter(status__in=status_filter)

    if user and not user.is_staff:
        if project_status.startswith('My'):
            project_queryset = project_queryset.filter(manager__id=user.id)

    projects = project_queryset.order_by('-rank')

    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


def filter_projects(queryset, params, user=None):
    project_status = params.get('status')
    status_filter = get_project_status(project_status, user)

    if status_filter is None:
        return Response(
            {'message': 'There is no such project status'},
            status=status.HTTP_404_NOT_FOUND
        )

    if status_filter and project_status.startswith('My'):
        queryset = queryset.filter(manager=user.id, status__in=status_filter)
    else:
        queryset = queryset.filter(status__in=status_filter)

    status_paginate = ['Completed', 'Suspended',
                       'My Suspended', 'My Completed']

    if project_status in status_paginate:
        page_size = params.get('page_size')
        page_number = params.get('page_number')
        data = paginate(page_size, page_number, queryset)
        return Response(data)

    serializer = ProjectSerializer(queryset, many=True)
    return Response(serializer.data)
