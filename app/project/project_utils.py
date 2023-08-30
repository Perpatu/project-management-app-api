from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from django.db.models import Q
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


def search_auth(search_word, project_status):
    """Searching project function for all auth users"""
    search_vector = vector()
    search_query = SearchQuery(search_word)
    forbidden_status = ['Completed', 'Suspended',
                        'My Active', 'My Suspended',
                        'My Completed']
    if project_status not in forbidden_status:
        if project_status == 'Active':
            query = Project.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
                ).filter(
                    Q(rank__gte=0.1),
                    Q(status='Started') | Q(status='In design')
                ).order_by('-rank')
            ser = ProjectSerializer(query, many=True)
            return Response(ser.data)
        info = {'message': 'There is no such project status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    info = {'message': 'you do not have permissions'}
    return Response(info, status=status.HTTP_403_FORBIDDEN)


def search_admin(search_word, project_status, user):
    """Searching project function for only admin users"""
    search_vector = vector()
    search_query = SearchQuery(search_word)
    if project_status == 'My Active' and user.is_staff:
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(rank__gte=0.1),
                Q(manager__id=user.id),
                Q(status='Started') | Q(status='In design')
            ).order_by('-rank')
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'My Completed' and user.is_staff:
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.1,
                manager__id=user.id,
                status='Completed'
            ).order_by('-rank')
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'My Suspended' and user.is_staff:
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.1,
                manager__id=user.id,
                status='Suspended'
            ).order_by('-rank')
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'Active':
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                Q(rank__gte=0.1),
                Q(status='Started') | Q(status='In design')
            ).order_by('-rank')
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'Completed' and user.is_staff:
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.1,
                status='Completed'
            ).order_by('-rank')
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'Suspended' and user.is_staff:
        query = Project.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.1,
                status='Suspended'
            ).order_by('-rank')
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    info = {'message': 'There is no such project status'}
    return Response(info, status=status.HTTP_404_NOT_FOUND)


def filter_auth(queryset, project_status):
    forbidden_status = ['Completed', 'Suspended',
                        'My Active', 'My Suspended',
                        'My Completed']
    if project_status not in forbidden_status:
        if project_status == 'Active':
            query = queryset.filter(
                Q(status='Started') | Q(status='In design')
            )
            ser = ProjectSerializer(query, many=True)
            return Response(ser.data)
        info = {'message': 'There is no such project status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    info = {'message': 'you do not have permissions'}
    return Response(info, status=status.HTTP_403_FORBIDDEN)


def filter_admin(queryset, project_status, user):
    if project_status == 'My Active' and user.is_staff:
        query = queryset.filter(
            Q(manager=user.id),
            Q(status='Started') | Q(status='In design')
        )
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'My Suspended' and user.is_staff:
        query = queryset.filter(
            manager=user.id,
            status='Suspended'
        )
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'My Completed' and user.is_staff:
        query = queryset.filter(
            manager=user.id,
            status='Completed'
        )
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'Active':
        query = queryset.filter(
            Q(status='Started') | Q(status='In design')
        )
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'Suspended' and user.is_staff:
        query = queryset.filter(
            status='Suspended'
        )
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    elif project_status == 'Completed' and user.is_staff:
        query = queryset.filter(
            status='Completed'
        )
        ser = ProjectSerializer(query, many=True)
        return Response(ser.data)
    info = {'message': 'There is no such project status'}
    return Response(info, status=status.HTTP_404_NOT_FOUND)
