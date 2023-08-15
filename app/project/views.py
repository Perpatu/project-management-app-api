"""
Views for the project APIs.
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from core.models import Project
from project import serializers


class ProjectViewAdminSet(viewsets.ModelViewSet):
    """View for manage client APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new client"""
        serializer.save()


class ProjectViewEmployeeSet(viewsets.ReadOnlyModelViewSet):
    """View for manage client APIs"""
    serializer_class = serializers.ProjectSerializer
    queryset = Project.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
