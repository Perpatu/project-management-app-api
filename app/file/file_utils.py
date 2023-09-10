import math
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator
from project.serializers import ProjectProgressSerializer
from department.serializers import DepartmentSerializer
from file import serializers
from core.models import (
    Project,
    QueueLogic,
    File,
    Department
)
from rest_framework.response import Response
from rest_framework import status


def vector():
    search_vector = SearchVector('name', weight='B') + \
                SearchVector('file', weight="A")
    return search_vector


def get_queue_status(queue_status):
    if queue_status == 'Active':
        status_filter = True
    elif queue_status == 'Completed':
        status_filter = False
    else:
        status_filter = None

    if status_filter is None:
        return None

    return status_filter


def paginate(page_size, page_number, dep_id, query):
    paginator = Paginator(query, page_size)
    page_obj = paginator.get_page(page_number)
    context = {'dep_id': int(dep_id)}
    serializer = serializers.FileDepartmentSerializer(
        page_obj,
        many=True,
        context=context
    )
    total_items = paginator.count
    max_pages = math.ceil(total_items / int(page_size))
    ser_data = serializer.data if max_pages >= int(page_number) else {}
    data = {
        'data': ser_data,
        'totalItems': total_items
    }
    return data


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


def filter_files(params):
    project_status = params.get('status')
    dep_id = params.get('dep_id')
    status_filter = get_queue_status(project_status)

    if status_filter is None:
        return Response(
            {'message': 'There is no such file status'},
            status=status.HTTP_404_NOT_FOUND
        )

    query_dep = Department.objects.get(id=int(dep_id))
    serializer_dep = DepartmentSerializer(query_dep, many=False)
    department = serializer_dep.data

    if status_filter:
        query_file = File.objects.filter(
            queue__department=int(dep_id),
            queue__end=False
        )
        context = {'dep_id': int(dep_id)}
        serializer_file = serializers.FileDepartmentSerializer(
            query_file,
            many=True,
            context=context
        )
        files = serializer_file.data
        data = {
            'department': department,
            'files': files
        }
        return data
    else:
        query_file = File.objects.filter(
            queue__department=int(dep_id),
            queue__end=True
        )
        page_size = params.get('page_size')
        page_number = params.get('page_number')
        files = paginate(page_size, page_number, dep_id, query_file)
        data = {
            'department': department,
            'files': files
        }
        return data
