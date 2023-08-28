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
from project.serializers import ProjectProgressSerializer

from core.models import (
    File,
    Project,
    CommentFile,
    QueueLogic,
)


def project_progress(project_id):
    all_task = QueueLogic.objects.filter(project=project_id).count()
    end_task = QueueLogic.objects.filter(project=project_id, end=True).count()
    project = Project.objects.get(id=project_id)
    procent = (end_task / all_task) * 100
    data = {'progress': int(procent)}
    serializer = ProjectProgressSerializer(project, data=data)
    if serializer.is_valid():
        serializer.save()


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

    def perform_create(self, serializer):
        """Creating logic and calculate project progress"""
        ser_data = serializer.validated_data
        file = File.objects.filter(id=ser_data['file'].id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = []
        if len(data['queue']) != 0:
            for dep in data['queue']:
                deps_id.append(dep['department'])
            if ser_data['department'].id in deps_id:
                raise Exception(
                    'Queue with this department exist'
                )
            else:
                deps_id.append(ser_data['department'].id)
                if min(deps_id) == ser_data['department'].id:
                    ser_data['permission'] = True
                    logic = QueueLogic.objects.get(
                        file=ser_data['file'].id, department=deps_id[0]
                    )
                    logic.permission = False
                    logic.save()
                super().perform_create(serializer)
        else:
            ser_data['permission'] = True
        super().perform_create(serializer)
        project_progress(ser_data['project'].id)
        info = {'message': 'queue has been added'}
        return Response(info)

    def update(self, request, *args, **kwargs):
        """Updating logic and calculate project progress"""
        self.serializer_class = serializers.QueueLogicUpdateSerializer
        request_data = request.data
        queue_obj = self.get_object()
        file = File.objects.filter(id=queue_obj.file.id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = []
        for dep in data['queue']:
            deps_id.append(dep['department'])
        if request_data['end'] and queue_obj.permission:
            index = deps_id.index(queue_obj.department.id)
            logic = QueueLogic.objects.get(
                file=queue_obj.file.id, department=deps_id[index+1]
            )
            logic.permission = True
            logic.save()
        if request_data['end'] and queue_obj.permission:
            index = deps_id.index(queue_obj.department.id)
            deps_id = deps_id[index+1:]
            if len(deps_id) > 1:
                for dep_id in deps_id:
                    logic = QueueLogic.objects.get(
                        file=queue_obj.file.id, department=dep_id
                    )
                    logic.permission = False
                    logic.end = False
                    logic.start = False
                    logic.paused = False
                    logic.save()
        super().update(request, *args, **kwargs)
        project_progress(request_data['project'])
        info = {'message': f'queue with id {queue_obj.id} has been updated'}
        return Response(info)

    def destroy(self, request, *args, **kwargs):
        """deleting logic and calculate project progress"""
        queue_obj = self.get_object()
        file = File.objects.filter(id=queue_obj.file.id).first()
        serializer_file = serializers.FileProjectSerializer(file, many=False)
        data = serializer_file.data
        deps_id = []
        for dep in data['queue']:
            deps_id.append(dep['department'])
        if min(deps_id) == queue_obj.department.id:
            if len(deps_id) != 1:
                deps_id.remove(queue_obj.department.id)
            logic = QueueLogic.objects.get(
                file=queue_obj.file.id, department=deps_id[0]
            )
            logic.permission = True
            logic.save()
        super().destroy(request, *args, **kwargs)
        project_progress(queue_obj.project.id)
        info = {'message': f'queue with id {queue_obj.id} has been deleted'}
        return Response(info)
