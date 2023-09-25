"""
Views for the project APIs.
"""
import os
import shutil
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
from .project_utils import (
    filter_production_projects,
    search_projects,
    filter_secretariat_projects
)
from core.models import (
    Project,
    CommentProject,
)
from app.settings import MEDIA_ROOT
from project import serializers


class ProjectAdminViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    """View for manage andmin project APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'create':
            return serializers.ProjectCreateSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """Create and return new project"""
        response = super().create(request, *args, **kwargs)

        if response.status_code == 201:
            project_data = response.data
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'project_group',
                {
                    'type': 'project_add',
                    'message': project_data,
                }
            )

        return response

    def destroy(self, request, *args, **kwargs):
        """Delete project object in db and folder with files on server"""
        project = self.get_object()
        dir_path = MEDIA_ROOT + '/uploads/projects/' + str(project.id) + '/'
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            response = super().destroy(request, *args, **kwargs)
            if response.status_code == 204:
                project_data = {'id': project.id}
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'project_group',
                    {
                        'type': 'project_delete',
                        'message': project_data,
                    }
                )
            return response
        else:
            response = super().destroy(request, *args, **kwargs)
            if response.status_code == 204:
                project_data = {'id': project.id}
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'project_group',
                    {
                        'type': 'project_delete',
                        'message': project_data,
                    }
                )
            return response

    @action(methods=['GET'], detail=False, url_path='columns')
    def project_admin_columns(self, request):
        """Columns for admin"""
        columns = ['name', 'number', 'order_number', 'start',
                   'deadline', 'status', 'progress',
                   'priority', 'manager', 'options']
        return Response(columns)
    
    @action(methods=['GET'], detail=False, url_path='columns-secretariat')
    def project_secretariat_columns(self, request):
        """Columns for production project"""
        columns = ['number', 'order_number', 'start',
                   'deadline', 'progress', 'manager',
                    'status', 'options']
        return Response(columns)
    
    @action(methods=['GET'], detail=False, url_path='status-secretariat')
    def project_secretiarat_status_view(self, request):
        """Project view"""
        user = request.user
        params = self.request.query_params
        
        response = filter_secretariat_projects(self.queryset, params, user)
        return response


class ProjectAuthViewSet(mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """View for manage employee project APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]    

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer
        return self.serializer_class
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        data = response.data
        new_files = []
        for file in data['files']:
            if file['destiny'] != 'Secretariat':
                new_files.append(file)
        data['files'] = new_files
        return Response(data)

    @action(methods=['GET'], detail=False, url_path='status')
    def project_production_status_view(self, request):
        """Project view"""
        user = request.user
        params = self.request.query_params
        response = filter_production_projects(self.queryset, params, user)
        return response   

    @action(methods=['GET'], detail=False, url_path='search')
    def project_production_search_view(self, request):
        """Search project"""
        user = request.user
        params = self.request.query_params
        response = search_projects(params, user)
        return response

    @action(methods=['GET'], detail=False, url_path='columns')
    def project_production_columns(self, request):
        """Columns for production project"""
        columns = ['number', 'order_number', 'start',
                   'deadline', 'status', 'progress',
                   'priority', 'manager']
        return Response(columns)   


class CommentProjectViewSet(mixins.CreateModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Manage comments project APIs"""
    serializer_class = serializers.CommentProjectDisplaySerializer
    queryset = CommentProject.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'create' or self.action == 'destroy':
            return serializers.CommentProjectManageSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            comment_object = self.get_object()
            if user.id == comment_object.user.id:
                return super().destroy(request, *args, **kwargs)
            info = {'message': 'This is not your comment'}
            Response(info, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
