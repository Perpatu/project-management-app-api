"""
Views for the file APIs.
"""
import os
from rest_framework import (
    viewsets,
    mixins,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from app.settings import MEDIA_ROOT
from .file_utils import (
    project_progress,
    search_file_department,
    filter_file_department
)
from file import serializers
from department.serializers import DepartmentSerializer
from core.models import (
    File,
    Department,
    CommentFile,
    QueueLogic,
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
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == 204:
            file_data = {'id': file.id}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'file_group',
                {
                    'type': 'file_delete',
                    'message': file_data,
                }
            )        
            return response
        return response
    
    def create(self, request, *args, **kwargs):
        """Create file object"""
        serializer = serializers.FilesUploadSerializer(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            file_data = serializer.data
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'file_group',
                {
                    'type': 'file_add',
                    'message': file_data,
                }
            )
            message = {'detail': qs, 'status': True}
            return Response(message, status=status.HTTP_201_CREATED)
        info = {'message': serializer.errors, 'status': False}
        return Response(info, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='columns-manage')
    def file_admin_mange_columns(self, request):
        """Columns for mange files"""
        deps = Department.objects.all()
        deps_ser = DepartmentSerializer(deps, many=True)
        deps_name = []
        for dep in deps_ser.data:
            deps_name.append(dep['name'])
        columns = ['view', 'filename', 'options']
        result = columns[0:2] + deps_name + [columns[2]]
        return Response(result)


class FileAuthViewSet(viewsets.GenericViewSet):
    """Manage file APIs"""
    serializer_class = serializers.FileManageSerializer
    queryset = File.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(methods=['GET'], detail=False, url_path='department')
    def department_view(self, request):
        """Files assigned for department add params dep_id to url"""
        dep_id = self.request.query_params.get('dep_id')
        status = self.request.query_params.get('status')
        response = filter_file_department(int(dep_id), status)
        return response
    
    @action(methods=['GET'], detail=False, url_path='search')
    def file_search_view(self, request):
        dep_id = self.request.query_params.get('dep_id')
        search = self.request.query_params.get('search')
        status = self.request.query_params.get('status')
        response = search_file_department(dep_id, search, status)
        return response

    @action(methods=['GET'], detail=False, url_path='columns-project')
    def file_auth_project_columns(self, request):
        """Columns for files at project"""
        deps = Department.objects.all()
        deps_ser = DepartmentSerializer(deps, many=True)
        deps_name = []
        for dep in deps_ser.data:
            deps_name.append(dep['name'])
        columns = ['view', 'filename', 'comments']
        result = columns[0:2] + deps_name + [columns[2]]
        return Response(result)

    @action(methods=['GET'], detail=False, url_path='columns-department')
    def file_auth_department_columns(self, request):
        """Columns for files at project"""
        deps = Department.objects.all()
        deps_ser = DepartmentSerializer(deps, many=True)
        deps_name = []
        for dep in deps_ser.data:
            deps_name.append(dep['name'])
        columns = ['view', 'filename',
                   'task', 'manager',
                   'project', 'comments']
        return Response(columns)


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

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            comment_object = self.get_object()
            if user.id == comment_object.user.id:
                return super().destroy(request, *args, **kwargs)
            else:
                info = {'message': 'This is not your comment'}
                Response(info, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class QueueLogicViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """Manage Queue Logic for file APIs"""
    serializer_class = serializers.QueueLogicManageSerializer
    queryset = QueueLogic.objects.all()
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action == 'update' or self.request.method == 'PATCH':
            return [IsAuthenticated()]
        else:
            return [IsAdminUser()]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'update' or self.request.method == 'PATCH':
            return serializers.QueueLogicUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Creating logic and calculate project progress"""
        ser_data = serializer.validated_data
        file = File.objects.filter(id=ser_data['file'].id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = []
        if len(data['queue']) != 0:
            for dep in data['queue']:
                deps_id.append(dep['department'])
            if ser_data['department'].id in deps_id:
                raise Exception(
                    'Queue with this department exist'
                )
            deps_id.append(ser_data['department'].id)
            if min(deps_id) == ser_data['department'].id:
                ser_data['permission'] = True
                logic = QueueLogic.objects.get(
                    file=ser_data['file'].id, department=deps_id[0]
                )
                logic.permission = False
                logic.save()
            super().perform_create(serializer)
        ser_data['permission'] = True
        super().perform_create(serializer)
        project_progress(ser_data['project'].id)
        info = {'message': 'queue has been added'}
        return Response(info)

    def update(self, request, *args, **kwargs):
        """Updating logic and calculate project progress"""
        request_data = request.data
        queue_obj = self.get_object()
        file = File.objects.filter(id=queue_obj.file.id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = []
        for dep in data['queue']:
            deps_id.append(dep['department'])
        if len(deps_id) > 1:
            if request_data['end'] and queue_obj.permission:
                index = deps_id.index(queue_obj.department.id)
                logic = QueueLogic.objects.get(
                    file=queue_obj.file.id, department=deps_id[index+1]
                )
                logic.permission = True
                logic.save()
            if not request_data['end'] and queue_obj.permission:
                index = deps_id.index(queue_obj.department.id)
                deps_id = deps_id[index+1:]
                for dep_id in deps_id:
                    logic = QueueLogic.objects.get(
                        file=queue_obj.file.id, department=dep_id
                    )
                    logic.permission = False
                    logic.end = False
                    logic.start = False
                    logic.paused = False
                    logic.save()
        super().update(request, *args, **kwargs)
        info = {'message': f'queue logic with id \
                {queue_obj.id} has been updated'}
        project_progress(request_data['project'])
        return Response(info)

    def destroy(self, request, *args, **kwargs):
        """deleting logic and calculate project progress"""
        queue_obj = self.get_object()
        file = File.objects.filter(id=queue_obj.file.id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = []
        for dep in data['queue']:
            deps_id.append(dep['department'])
        if min(deps_id) == queue_obj.department.id:
            if len(deps_id) != 1:
                deps_id.remove(queue_obj.department.id)
            logic = QueueLogic.objects.get(
                file=queue_obj.file.id, department=deps_id[0]
            )
            logic.permission = True
            logic.save()
        super().destroy(request, *args, **kwargs)
        project_progress(queue_obj.project.id)
        info = {'message': f'queue with id {queue_obj.id} has been deleted'}
        return Response(info)
