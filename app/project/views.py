"""
Views for the project APIs.
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from core.models import (
    Project,
    CommentProject,
)
from project import serializers


class ProjectAdminViewSet(viewsets.ModelViewSet):
    """View for manage client APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new client"""
        serializer.save()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer
        return self.serializer_class


class ProjectEmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """View for manage client APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer
        return self.serializer_class


class CommentProjectViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage comments project in db"""
    serializer_class = serializers.CommentProjectSerializer
    queryset = CommentProject.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to user"""
        return self.queryset.filter(
            user=self.request.user).order_by('date_posted')
