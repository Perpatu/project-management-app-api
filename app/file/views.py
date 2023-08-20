"""
Views for the file APIs.
"""
import os
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from app.settings import MEDIA_ROOT
from file import serializers

from core.models import (
    File
)


class FileAdminViewSet(mixins.DestroyModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    """Manage file APIs"""
    serializer_class = serializers.FileSerializer
    queryset = File.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        file = self.get_object()
        path = str(file.file)
        os.remove(MEDIA_ROOT + '/' + path)
        file.delete()
        return Response('deleted')

    def create(self, request, *args, **kwargs):
        serializer = serializers.FilesUploadSerializer(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            message = {'detail': qs, 'status': True}
            return Response(message, status=status.HTTP_201_CREATED)
        data = {"detail": serializer.errors, 'status': False}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
