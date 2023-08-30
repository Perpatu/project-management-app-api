"""
Views for the project APIs.
"""
import os
import shutil
from rest_framework import (
    viewsets,
    mixins,
)
# from datetime import datetime
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .project_utils import (
    search_admin,
    search_auth,
    filter_admin,
    filter_auth
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
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete project object in db and folder with files on server"""
        project = self.get_object()
        dir_path = MEDIA_ROOT + '/uploads/projects/' + str(project.id) + '/'
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            project.delete()
            return Response("Deleted Successfully!!")
        else:
            project.delete()
            return Response("Deleted Successfully!!")

    @action(methods=['GET'], detail=False, url_path='columns')
    def project_admin_columns(self, request):
        """Columns for admin"""
        columns = ['number', 'start', 'deadline',
                   'status', 'progress', 'priority', 'options']
        return Response(columns)


class ProjectAuthViewSet(viewsets.ReadOnlyModelViewSet):
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

    @action(methods=['GET'], detail=False, url_path='status')
    def project_status_view(self, request):
        """Project view for auth and admin users"""
        user = request.user
        project_status = self.request.query_params.get('status')
        if user.is_staff:
            response = filter_admin(self.queryset, project_status, user)
            return response
        response = filter_auth(self.queryset, project_status)
        return response

    @action(methods=['GET'], detail=False, url_path='search')
    def project_search_view(self, request):
        """Search project for auth and admin users"""
        user = request.user
        search_word = self.request.query_params.get('search')
        project_status = self.request.query_params.get('status')
        if user.is_staff:
            response = search_admin(search_word, project_status, user)
            return response
        response = search_auth(search_word, project_status)
        return response

    @action(methods=['GET'], detail=False, url_path='columns')
    def project_auth_columns(self, request):
        """Columns for auth users"""
        columns = ['number', 'start', 'deadline',
                   'status', 'progress', 'priority',
                   'manager']
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
