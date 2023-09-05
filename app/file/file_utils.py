from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from project.serializers import ProjectProgressSerializer
from file.serializers import FileDepartmentSerializer
from core.models import (
    Project,
    File,
    QueueLogic,
)
from rest_framework.response import Response
from rest_framework import status


def vector():
    search_vector = SearchVector('name', weight='B') + \
                SearchVector('file', weight="A")
    return search_vector


def project_progress(project_id):
    all_task = QueueLogic.objects.filter(project=project_id).count()
    end_task = QueueLogic.objects.filter(project=project_id, end=True).count()
    project = Project.objects.get(id=project_id)
    try:
        procent = (end_task / all_task) * 100
    except ZeroDivisionError:
        procent = 0
    data = {'progress': int(procent)}
    serializer = ProjectProgressSerializer(project, data=data)
    if serializer.is_valid():
        serializer.save()
    info = {'message': serializer.errors, 'status': False}
    return Response(info, status=status.HTTP_400_BAD_REQUEST)


def filter_file_department(dep_id, queue_status):
    if queue_status == 'Active':
        query = File.objects.filter(
            queue__department__in=[dep_id],
            queue__end=False,
            )
    elif queue_status == 'Completed':
        query = File.objects.filter(
            queue__department__in=[dep_id],
            queue__end=True,
        )
    else:
        info = {'message': 'There is no such file queue status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    serializer = FileDepartmentSerializer(
            query, many=True, context={'dep_id': dep_id})
    return Response(serializer.data)


def search_file_department(dep_id, search, queue_status):
    if queue_status == 'Active':
        search_vector = vector()
        search_query = SearchQuery(search)
        query = File.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.3,
                queue__department__in=[dep_id],
                queue__end=False,
            ).order_by('-rank')
    elif queue_status == 'Completed':
        search_vector = vector()
        search_query = SearchQuery(search)
        query = File.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
            ).filter(
                rank__gte=0.3,
                queue__department__in=[dep_id],
                queue__end=True,
            ).order_by('-rank')
    else:
        info = {'message': 'There is no such file queue status'}
        return Response(info, status=status.HTTP_404_NOT_FOUND)
    serializer = FileDepartmentSerializer(
            query, many=True, context={'dep_id': dep_id})
    return Response(serializer.data)
