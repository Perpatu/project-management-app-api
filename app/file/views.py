"""
Views for the file APIs.
"""
import os
from rest_framework import (
    viewsets,
    mixins,
)
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from app.settings import MEDIA_ROOT
from file import serializers

from core.models import (
    File,
    CommentFile,
    QueueLogic,
)


class FileAdminViewSet(mixins.DestroyModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
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
        file.delete()
        return Response('deleted')

    def create(self, request, *args, **kwargs):
        """Create file object"""
        serializer = serializers.FilesUploadSerializer(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            message = {'detail': qs, 'status': True}
            return Response(message, status=status.HTTP_201_CREATED)
        info = {'message': serializer.errors, 'status': False}
        return Response(info, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=False, url_path='departments')
    def department_view(self, request):
        """Files assinged for department add params dep_id to url"""
        dep_id = self.request.query_params.get('dep_id')
        dep_id_int = int(dep_id)
        queryset = self.queryset.filter(queue__department__in=[dep_id_int])
        serializer = serializers.FileDepartmentSerializer(
            queryset, many=True, context={'dep_id': dep_id_int}
        )
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='department/count')
    def file_counts_in_department(self, request):
        """
            Counts how many files are assigned to department
            add params dep_id to url
        """
        dep_id = self.request.query_params.get('dep_id')
        dep_id_int = int(dep_id)
        queryset = self.queryset.filter(
            queue__department__in=[dep_id_int]).count()
        return Response(queryset)

    @action(methods=['GET'], detail=False, url_path='search')
    def file_search_view(self, request):
        query = self.request.query_params.get('search')
        search_vector = SearchVector('name', weight='B') + \
            SearchVector('file', weight="A")
        search_query = SearchQuery(query)
        result = File.objects.annotate(
            search=search_vector, rank=SearchRank(search_vector, search_query)
                                ).filter(rank__gte=0.3).order_by('-rank')
        ser = serializers.FileProjectSerializer(result, many=True)
        return Response(ser.data)


class CommentFileViewSet(mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
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


class QueueLogicViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """Manage Queue Logic for file APIs"""
    serializer_class = serializers.QueueLogicManageSerializer
    queryset = QueueLogic.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
