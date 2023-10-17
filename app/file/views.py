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
from rest_framework.exceptions import ValidationError
from app.settings import MEDIA_ROOT
from .file_utils import project_progress, filter_files, search_files
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
        file_data = serializers.FileProjectSerializer(file).data
        super().destroy(request, *args, **kwargs)
        if len(file_data['queue']) > 0:
            project_progress(file_data['queue'][0]['project'])
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
        """Columns for files at department"""
        columns = ['view', 'name',
                   'task', 'manager',
                   'project', 'comments']
        return Response(columns)

    @action(methods=['GET'], detail=False, url_path='department')
    def file_department(self, request):
        """
            Returns info about department given it params dep_id
            and all files assigned to it
        """
        params = self.request.query_params
        data = filter_files(params)
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

    def perform_create(self, serializer):
        """Creating logic and calculate project progress"""
        validated_data = serializer.validated_data
        file = File.objects.filter(id=validated_data['file'].id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = [dep['department'] for dep in data['queue']]

        if validated_data['department'].id in deps_id:
            info = {'message': 'Queue with this department exists'}
            raise ValidationError(info)

        deps_id.append(validated_data['department'].id)
        deps_id.sort()
        validated_data['permission'] = False

        if min(deps_id) == validated_data['department'].id:
            validated_data['permission'] = True
            if len(deps_id) > 1:
                for dep_id in deps_id[1:]:
                    logic = QueueLogic.objects.get(
                        file=validated_data['file'].id, department=dep_id
                    )
                    logic.permission = False
                    logic.save()

        super().perform_create(serializer)

        if len(deps_id) == 0:
            deps_id.append(validated_data['department'].id)
        project_progress(validated_data['project'].id)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            queue_data = {'id': response.data['id']}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'queue_group',
                {
                    'type': 'queue_add',
                    'message': queue_data,
                }
            )
            file = File.objects.get(id=response.data['file'])
            file.new = False
            file.save()
            return response
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_409_CONFLICT)

    def update(self, request, *args, **kwargs):
        """Updating logic and calculate project progress"""
        request_data = request.data
        q_obj = self.get_object()
        file = File.objects.filter(id=q_obj.file.id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = [dep['department'] for dep in data['queue']]
        if len(deps_id) > 1 and request_data.get('end') and q_obj.permission:
            if max(deps_id) != q_obj.department.id:
                index = deps_id.index(q_obj.department.id)
                next_department_id = deps_id[index + 1]

                # Update permission for the next department
                logic = QueueLogic.objects.get(
                    file=q_obj.file.id, department=next_department_id
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

        info = {'message': f'Queue logic with id \
                {q_obj.id} has been updated'}
        project_progress(request_data['project'])

        return response

    def destroy(self, request, *args, **kwargs):
        """Delete logic and calculate project progress"""
        q_obj = self.get_object()
        file = File.objects.filter(id=q_obj.file.id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = [dep['department'] for dep in data['queue']]

        if min(deps_id) == q_obj.department.id and len(deps_id) > 1:
            deps_id.remove(q_obj.department.id)

            # Update permission for the next department
            logic = QueueLogic.objects.get(
                file=q_obj.file.id, department=deps_id[0]
            )
            logic.permission = True
            logic.save()

        response = super().destroy(request, *args, **kwargs)
        if response.status_code == 204:
            queue_data = {'id': q_obj.id}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'queue_group',
                {
                    'type': 'queue_delete',
                    'message': queue_data,
                }
            )
            project_progress(q_obj.project.id)
            info = {'message': f'Queue with id {q_obj.id} \
                    has been deleted'}
            return Response(info)


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
