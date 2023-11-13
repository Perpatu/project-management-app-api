import math
from django.core.paginator import Paginator
from project.serializers import ProjectProgressSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from file import serializers
from department.serializers import DepartmentSerializer
from file.serializers import FileDepartmentSerializer
from core.models import (
    Project,
    QueueLogic,
    File,
    Department,
    NotificationTask,
    User,
    CommentFile
)
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone, timedelta


def get_file_project_data(file_id):
    file = File.objects.filter(id=file_id).first()
    serializer_file = serializers.FileProjectSerializer(file, many=False)
    return serializer_file.data


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
    if all_task > 0 and procent >= 0 and procent < 100:
        data = {'status': 'Started'}
        serializer = ProjectProgressSerializer(project, data=data)
        if serializer.is_valid():
            serializer.save()
    if procent == 100:
        data = {'status': 'Completed'}
        serializer = ProjectProgressSerializer(project, data=data)
        if serializer.is_valid():
            serializer.save()
    data = {'progress': int(procent)}
    serializer = ProjectProgressSerializer(project, data=data)
    if serializer.is_valid():
        serializer.save()


def filter_files(params, user):
    dep_id = params.get('dep_id')
    queue_status = params.get('status')
    
    status_filter = get_queue_status(queue_status)

    if status_filter is None:
        return Response(
            {'message': 'There is no such file status'},
            status=status.HTTP_404_NOT_FOUND
        )

    query_dep = Department.objects.get(id=int(dep_id))
    serializer_dep = DepartmentSerializer(query_dep, many=False)
    department = serializer_dep.data

    if status_filter:
        if user.role == 'Employee':        
            query_file = File.objects.filter(
                queue__department=int(dep_id),
                queue__users__in=[user.id],
                queue__end=False
            )
        else:
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


def search_files(params):
    queue_status = params.get('status')
    search_phase = params.get('search')
    dep_id = params.get('dep_id')
    status_filter = get_queue_status(queue_status)

    if status_filter is None:
        return Response({'message': 'There is no such file status \
                          or you do not have permission'},
                        status=status.HTTP_404_NOT_FOUND)

    query_dep = Department.objects.get(id=int(dep_id))
    serializer_dep = DepartmentSerializer(query_dep, many=False)
    department = serializer_dep.data

    query_file = File.objects.filter(
        name__icontains=search_phase,
        queue__department=int(dep_id),
        queue__end=not status_filter
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


def notification_ws(data):
    dep = Department.objects.get(id=data['department'])
    file = File.objects.get(id=data['file'])
    users = User.objects.all()
    content = f'New Task ({file}) appeared in {dep}'

    for user in users:
        notification = NotificationTask(
            user=user,
            department=dep,
            file=file,
            content=content,
            type='task'
        )
        notification.save()

        noti_ser = serializers.NotificationTaskSerializer(
            notification,
            many=False
        )
        message = {
            'data': noti_ser.data,
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_task_noti_{user.id}',
            {
                'type': 'task_noti',
                'message': message,
            }
        )


def task(data, users, where):
    project_progress(data['project'])
    project = Project.objects.get(id=data['project'])
    serializer = ProjectProgressSerializer(project, many=False)
    message = {
        'file': data,
        'project': serializer.data,
        'type': 'task'
    }
    for user in users:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_file_modify_{where}_{user.id}',
        {
            'type': f'task_modify_{where}',
            'message': message,
            }
        )


def comment(comment_id, users, destiny, where):
    comment = CommentFile.objects.get(id=comment_id)
    comment_ser = serializers.CommentFileDisplaySerializer(
        comment,
        many=False
    )
    comment_data = comment_ser.data
    message = {
        'comment': comment_data,
        'type': destiny,
    }
    for user in users:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_file_modify_{where}_{user.id}',
            {
                'type': f'task_modify_{where}',
                'message': message,
            }
        )

def file_delete(data, users, where):
    message = {
        'file': data,
        'type': 'file_delete'
    }
    for user in users:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_file_modify_{where}_{user.id}',
            {
                'type': f'task_modify_{where}',
                'message': message,
            }
        )


def update_task_project_ws(data, destiny):
    """Refresh task for file and progress for project in project view"""
    users = User.objects.all()

    if destiny == 'task':
        task(data, users, 'project')

    elif destiny == 'comment_add' or destiny == 'comment_delete':
        comment(data, users, destiny, 'project')
        
    elif destiny == 'file_delete':
        file_delete(data, users, 'project')


def update_task_department_ws(data, destiny):
    """Refresh task for file in department view"""

    users = User.objects.all()

    if destiny == 'task':
        query = File.objects.get(id=data['id'])
        try:
            dep_id = data['queue'][0]['department']
            context = {'dep_id': dep_id}
            serializer_file = serializers.FileDepartmentSerializer(
                query,
                context=context
            )
            file_data = serializer_file.data
            file_data['project'] = serializer_file.data['project']['id']
            task(file_data, users, 'department')
        except IndexError:
            pass       
    
    elif destiny == 'comment_add' or destiny == 'comment_delete':
        comment(data, users, destiny, 'department')
       
    elif destiny == 'file_delete':
        file_delete(data, users, 'department')


def is_current_date_in_range(start, end):
    current_date = datetime.now(timezone.utc)
    return start <= current_date <= end


def check_user_status(user_id):
    query = QueueLogic.objects.filter(users__in=[user_id], end=False)
    serializer = serializers.QueueLogicCalendarSerializer(query, many=True)
    data = serializer.data
    results = []
    for obj in data:
        start_date = datetime.fromisoformat(obj['planned_start_date'])
        end_date = datetime.fromisoformat(obj['planned_end_date'])
        results.append(is_current_date_in_range(start_date, end_date))

    user = User.objects.get(id=user_id)
    if True in results:        
        user.status = 'Busy'
        user.save()
    else:
        user.status = 'Free'
        user.save()

def check_all_user_status():
    users = User.objects.filter(role='Employee')
    for user in users:
        query = QueueLogic.objects.filter(users__in=[user.id], end=False)
        serializer = serializers.QueueLogicCalendarSerializer(query, many=True)
        data = serializer.data
        results = []
        for obj in data:
            start_date = datetime.fromisoformat(obj['planned_start_date'])
            end_date = datetime.fromisoformat(obj['planned_end_date'])
            results.append(is_current_date_in_range(start_date, end_date))

        #user = User.objects.get(id=user_id)
        if True in results:        
            user.status = 'Busy'
            user.save()
        else:
            user.status = 'Free'
            user.save()
