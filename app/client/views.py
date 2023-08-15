"""
Views for the client APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

from core.models import Client
from client import serializers


class ClientViewSet(viewsets.ModelViewSet):
    """View for manage client APIs"""
    serializer_class = serializers.ClientSerializer
    queryset = Client.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new client"""
        serializer.save()
