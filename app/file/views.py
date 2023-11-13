"""
Views for the file APIs.
"""
import os
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError
from app.settings import MEDIA_ROOT
from file import serializers
from department.serializers import DepartmentSerializer
from core.models import (
    File,
    Department,
    CommentFile,
    QueueLogic,
    NotificationTask,
)
from .file_utils import (
    project_progress,
    get_file_project_data,
    filter_files,
    search_files,
    notification_ws,
    update_task_project_ws,
    update_task_department_ws,
    check_user_status
)


class FileAdminViewSet(mixins.DestroyModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """Manage file APIs"""
    serializer_class = serializers.FileManageSerializer
    queryset = File.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        """Delete file object in db and file on server"""
        file = self.get_object()
        file_path = MEDIA_ROOT + '/' + str(file.file)
        os.remove(file_path)
        file_data = serializers.FileProjectSerializer(file).data
        super().destroy(request, *args, **kwargs)
        if len(file_data['queue']) > 0:
            project_progress(file_data['project'])
        update_task_project_ws(file_data, 'file_delete')
        update_task_department_ws(file_data, 'file_delete')
        return Response({'File has been deleted'})

    def create(self, request, *args, **kwargs):
        """Create file object"""
        serializer = serializers.FilesUploadSerializer(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            message = {'detail': qs, 'status': True}
            return Response(message, status=status.HTTP_201_CREATED)        
        info = {'message': serializer.errors, 'status': False}
        return Response(info, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='columns-manage')
    def file_mange_columns(self, request):
        """Columns for mange files"""
        deps = Department.objects.all()
        deps_ser = DepartmentSerializer(deps, many=True)
        deps_name = []
        for dep in deps_ser.data:
            deps_name.append(dep['name'])
        static = ['view', 'name', 'options']
        merged = static[0:2] + deps_name + [static[2]]
        result = {
            'departments': deps_ser.data,
            'merged': merged
        }
        return Response(result)

    @action(methods=['GET'], detail=False, url_path='columns-secretariat')
    def file_secretariat_columns(self, request):
        """Columns for secretariat files"""
        result = ['view', 'name', 'comments', 'options']
        return Response(result)
    
    @action(methods=['GET'], detail=False, url_path='columns-department')
    def file_admin_department_columns(self, request):
        """Columns for files at department auth"""
        columns = ['view', 'name', 'prev_task',
                   'task', 'next_task', 'project','manager',
                   'comments']
        return Response(columns) 

    @action(methods=['GET'], detail=False, url_path='detail-name')
    def file_by_name(self, request):
        """file by name add to params name=filename project=project_id """
        name = self.request.query_params.get('name')
        project = self.request.query_params.get('project')
        file = File.objects.get(name=name, project=project)
        serializer = serializers.FileManageSerializer(file)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='secretariat')
    def file_secretariat(self, request):
        """get Secretariat files assigned to project params project_id"""
        project = self.request.query_params.get('project')
        file = File.objects.filter(project=project, destiny='Secretariat')
        serializer = serializers.FileProjectSerializer(file, many=True)
        return Response(serializer.data)
    

class FileAuthViewSet(viewsets.GenericViewSet):
    """Manage file APIs"""
    serializer_class = serializers.FileManageSerializer
    queryset = File.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], detail=False, url_path='columns-project')
    def file_auth_project_columns(self, request):
        """Columns for files at project"""
        deps = Department.objects.all()
        deps_ser = DepartmentSerializer(deps, many=True)
        deps_name = []
        for dep in deps_ser.data:
            deps_name.append(dep['name'])
        columns = ['view', 'name', 'comments']
        merged = columns[0:2] + deps_name + [columns[2]]
        result = {
            'departments': deps_ser.data,
            'merged': merged
        }
        return Response(result)

    @action(methods=['GET'], detail=False, url_path='columns-department')
    def file_auth_department_columns(self, request):
        """Columns for files at department auth"""
        columns = ['view', 'name', 'prev_task',
                   'task', 'next_task', 'manager',
                   'comments']
        return Response(columns)   

    @action(methods=['GET'], detail=False, url_path='department')
    def file_department(self, request):
        """
            Returns info about department given it params dep_id
            and all files assigned to it
        """
        params = self.request.query_params
        user = request.user
        data = filter_files(params, user)
        return Response(data)

    @action(methods=['GET'], detail=False, url_path='department/search')
    def file_department_search(self, request):
        """
            Search
            Returns info about department given it params dep_id
            and all files assigned to it
        """
        params = self.request.query_params
        data = search_files(params)
        return Response(data)


class QueueLogicViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """Manage Queue Logic for file APIs"""
    serializer_class = serializers.QueueLogicManageSerializer
    queryset = QueueLogic.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'update' or self.request.method == 'PATCH':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'update' or self.request.method == 'PATCH':
            return serializers.QueueLogicUpdateSerializer
        return super().get_serializer_class()

    @action(methods=['GET'], detail=False, url_path='calendar')
    def users_task_calendar(self, request):
        """Return task for the user calendar"""
        user_id = self.request.query_params.get('user_id')
        queryset = self.queryset.filter(users__in=user_id, end=False)
        serializer = serializers.QueueLogicCalendarSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Creating logic and calculate project progress"""
        validated_data = serializer.validated_data
        dep_id = validated_data['department'].id
        file_id = validated_data['file'].id
        exists = QueueLogic.objects.filter(
            file=file_id,
            department=dep_id
        ).exists()

        if exists:
            info = {'message': 'Queue with this department exists'}
            raise ValidationError(info)

        file_data = get_file_project_data(file_id)
        queue_deps = [
            dep['department'] for dep in file_data.get('queue', [])
        ]

        queue_deps.append(dep_id)
        queue_deps.sort()
        validated_data['permission'] = False

        if dep_id == queue_deps[0]:
            validated_data['permission'] = True
            QueueLogic.objects.filter(
                file=file_id,
                department__in=queue_deps[1:]
            ).update(permission=False)

        elif dep_id == queue_deps[-1] and len(queue_deps) > 1:
            penultimate_dep = queue_deps[-2]
            logic = QueueLogic.objects.get(
                file=file_id,
                department=penultimate_dep
            )
            logic_ser = serializers.QueueLogicToFileSerializer(logic)
            validated_data['permission'] = logic_ser.data.get('end', False)

        else:
            index = queue_deps.index(dep_id)
            dep = queue_deps[index-1]
            dep_next = queue_deps[index+1]
            logic = QueueLogic.objects.get(file=file_id, department=dep)
            logic_ser = serializers.QueueLogicToFileSerializer(logic)
            logic_next = QueueLogic.objects.get(
                file=file_id,
                department=dep_next
            )
            logic_next.permission = False
            logic_next.start = False
            logic_next.paused = False
            logic_next.end = False
            logic_next.save()
            validated_data['permission'] = logic_ser.data.get('end', False)

        super().perform_create(serializer)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            file = File.objects.get(id=response.data['file'])
            file.new = False
            file.save()
            file = File.objects.get(id=response.data['file'])
            serializer_file = serializers.FileProjectSerializer(
                file,
                many=False
            )
            file_data = serializer_file.data
            notification_ws(response.data)
            update_task_project_ws(file_data, 'task')
            update_task_department_ws(file_data,'task')
            return response

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_409_CONFLICT)

    def destroy(self, request, *args, **kwargs):
        """Delete logic and calculate project progress"""
        q_obj = self.get_object()
        dep_id = q_obj.department.id
        file_data = get_file_project_data(q_obj.file.id)
        queue_deps = [
            dep['department'] for dep in file_data.get('queue', [])
        ]

        if dep_id == queue_deps[0] and len(queue_deps) > 1:
            queue_deps.remove(dep_id)

            logic = QueueLogic.objects.get(
                file=q_obj.file.id,
                department=queue_deps[0]
            )
            logic.permission = True
            logic.save()
        else:
            try:
                index = queue_deps.index(dep_id)
                dep_next = queue_deps[index+1]
                logic_next = QueueLogic.objects.get(
                    file=q_obj.file.id,
                    department=dep_next
                )
                logic_next.permission = True
                logic_next.save()
            except IndexError:
                pass

        response = super().destroy(request, *args, **kwargs)
        if response.status_code == 204:
            file_data = get_file_project_data(q_obj.file.id)
            update_task_project_ws(file_data, 'task')
            update_task_department_ws(file_data,'task')
            return response

    def update(self, request, *args, **kwargs):
        """Updating logic and calculate project progress"""
        request_data = request.data
        user_id = request.user.id
        q_obj = self.get_object()
        file_data = get_file_project_data(q_obj.file.id)
        deps_id = [dep['department'] for dep in file_data['queue']]
        if len(deps_id) > 1 and request_data.get('end') and q_obj.permission:
            if max(deps_id) != q_obj.department.id:
                index = deps_id.index(q_obj.department.id)
                next_dep_id = deps_id[index + 1]

                logic = QueueLogic.objects.get(
                    file=q_obj.file.id, department=next_dep_id
                )
                logic.permission = True
                logic.save()

        if not request_data.get('end') and q_obj.permission:
            index = deps_id.index(q_obj.department.id)
            deps_to_update = deps_id[index + 1:]

            for dep_id in deps_to_update:
                logic = QueueLogic.objects.get(
                    file=q_obj.file.id, department=dep_id
                )
                logic.permission = False
                logic.end = False
                logic.start = False
                logic.paused = False
                logic.save()
        response = super().update(request, *args, **kwargs)
        check_user_status(user_id)
        file_data = get_file_project_data(q_obj.file.id)
        update_task_project_ws(file_data, 'task')
        update_task_department_ws(file_data, 'task')
        return response


class CommentFileViewSet(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """Manage comments file APIs"""
    serializer_class = serializers.CommentFileDisplaySerializer
    queryset = CommentFile.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'create' or self.action == 'destroy':
            return serializers.CommentFileManageSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        update_task_project_ws(response.data['id'], 'comment_add')
        update_task_department_ws(response.data['id'], 'comment_add')
        return response

    def destroy(self, request, *args, **kwargs):
        user = request.user
        comment_object = self.get_object()
        comment_id = comment_object.id
        if not user.is_staff:            
            if user.id == comment_object.user.id:
                update_task_project_ws(comment_id, 'comment_delete')
                update_task_department_ws(comment_id, 'comment_delete')
                return super().destroy(request, *args, **kwargs)
            else:
                info = {'message': 'This is not your comment'}
                return Response(info, status=status.HTTP_403_FORBIDDEN)
        update_task_project_ws(comment_id, 'comment_delete')
        update_task_department_ws(comment_id, 'comment_delete')
        return super().destroy(request, *args, **kwargs)


class NotificationsTaskView(mixins.ListModelMixin,
                            mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = serializers.NotificationTaskSerializer
    queryset = NotificationTask.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(read=False, user=self.request.user)
        return super().get_queryset()

    @action(methods=['GET'], detail=False, url_path='quantity')
    def notification_task_quantity(self, request):
        """Return notification quantity"""
        quantity = self.queryset.filter(read=False, user=request.user).count()
        return Response(quantity)
