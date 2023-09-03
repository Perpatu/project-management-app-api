from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from rest_framework.response import Response
from rest_framework import status
from core.models import Project
from project.serializers import ProjectSerializer


def vector():
    search_vector = SearchVector('number', weight='A') + \
        SearchVector('manager__first_name', weight='A') + \
        SearchVector('manager__last_name', weight='A') + \
        SearchVector('client__name', weight='A') + \
        SearchVector('deadline', weight="B") + \
        SearchVector('priority', weight="C")
    return search_vector


def search_auth(search_phase, project_status):
    forbidden_status = {'Completed', 'Suspended', 'My Active',
                        'My Suspended', 'My Completed'}
    if project_status in forbidden_status:
        return Response({'message': 'You do not have permissions'},
                        status=status.HTTP_403_FORBIDDEN)
    search_vector = vector()
    search_query = SearchQuery(search_phase)

    if project_status == 'Active':
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            rank__gte=0.1,
            status__in=['Started', 'In design']
        ).order_by('-rank')
    else:
        return Response({'message': 'There is no such project status'},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = ProjectSerializer(query, many=True)
    return Response(serializer.data)


def search_admin(search_phase, project_status, user):
    if not user.is_staff:
        return Response({'message': 'You do not have permissions'},
                        status=status.HTTP_403_FORBIDDEN)
    search_vector = vector()
    search_query = SearchQuery(search_phase)
    project_queryset = Project.objects.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(rank__gte=0.1)
    if project_status == 'My Active':
        project_queryset = project_queryset.filter(
            manager__id=user.id,
            status__in=['Started', 'In design']
        )
    elif project_status == 'My Completed':
        project_queryset = project_queryset.filter(
            manager__id=user.id,
            status='Completed'
        )
    elif project_status == 'My Suspended':
        project_queryset = project_queryset.filter(
            manager__id=user.id,
            status='Suspended'
        )
    elif project_status == 'Active':
        project_queryset = project_queryset.filter(
            status__in=['Started', 'In design']
        )
    elif project_status == 'Completed':
        project_queryset = project_queryset.filter(
            status='Completed'
        )
    elif project_status == 'Suspended':
        project_queryset = project_queryset.filter(
            status='Suspended'
        )
    else:
        return Response({'message': 'There is no such project status'},
                        status=status.HTTP_404_NOT_FOUND)
    projects = project_queryset.order_by('-rank')
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)


def filter_auth(queryset, project_status):
    forbidden_status = {'Completed', 'Suspended', 'My Active',
                        'My Suspended', 'My Completed'}
    if project_status not in forbidden_status:
        if project_status == 'Active':
            query = queryset.filter(
                status__in=['Started', 'In design']
            )
            serializer = ProjectSerializer(query, many=True)
            return Response(serializer.data)
        info = {'message': 'There is no such project status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    info = {'message': 'you do not have permissions'}
    return Response(info, status=status.HTTP_403_FORBIDDEN)


def filter_admin(queryset, project_status, user):
    if not user.is_staff:
        info = {'message': 'You do not have permission to \
                perform this action.'}
        return Response(info, status=status.HTTP_403_FORBIDDEN)

    if project_status == 'My_Active':
        query = queryset.filter(
            manager=user.id,
            status__in=['Started', 'In design']
        )
    elif project_status == 'My Suspended':
        query = queryset.filter(
            manager=user.id,
            status='Suspended'
        )
    elif project_status == 'My Completed':
        query = queryset.filter(
            manager=user.id,
            status='Completed'
        )
    elif project_status == 'Active':
        query = queryset.filter(
            status__in=['Started', 'In design']
        )
    elif project_status == 'Suspended':
        query = queryset.filter(
            status='Suspended'
        )
    elif project_status == 'Completed':
        query = queryset.filter(
            status='Completed'
        )
    else:
        info = {'message': 'There is no such project status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    serializer = ProjectSerializer(query, many=True)
    return Response(serializer.data)
