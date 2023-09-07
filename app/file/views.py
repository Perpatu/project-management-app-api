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
from .file_utils import project_progress
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
        super().destroy(request, *args, **kwargs)

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

        data = {'departments': deps_id}
        serializer_file = serializers.TestSerializer(file, data=data)

        if serializer_file.is_valid():
            serializer_file.save()
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

        super().update(request, *args, **kwargs)

        info = {'message': f'Queue logic with id \
                {q_obj.id} has been updated'}
        project_progress(request_data['project'])

        return Response(info)

    def destroy(self, request, *args, **kwargs):
        """Deleting logic and calculate project progress"""
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
