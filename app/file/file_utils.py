from django.contrib.postgres.search import SearchVector
from project.serializers import ProjectProgressSerializer
from core.models import (
    Project,
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

