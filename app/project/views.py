"""
Views for the project APIs.
"""
import os
import shutil
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from core.models import (
    Project,
    CommentProject,
)
from app.settings import MEDIA_ROOT
from project import serializers


class ProjectAdminViewSet(viewsets.ModelViewSet):
    """View for manage andmin project APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new project"""
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        dir_path = MEDIA_ROOT + '/uploads/projects/' + str(project.id) + '/'
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            project.delete()
            return Response("Deleted Successfully!!")
        else:
            project.delete()
            return Response("Deleted Successfully!!")

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer
        return self.serializer_class


class ProjectEmployeeViewSet(viewsets.ReadOnlyModelViewSet):
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


class CommentProjectViewSet(mixins.CreateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
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
