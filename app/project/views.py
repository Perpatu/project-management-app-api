"""
Views for the project APIs.
"""
import os
import shutil
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

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.ProjectDetailSerializer
        return self.serializer_class

    @action(methods=['GET'], detail=False, url_path='status')
    def project_admin_status_view(self, request):
        """Project view for admin"""
        status = self.request.query_params.get('status')
        if status == 'My':
            queryset = self.queryset.filter(manager__id=request.user.id)
            ser = serializers.ProjectSerializer(queryset, many=True)
            return Response(ser.data)
        else:
            queryset = self.queryset.filter(status=status)
            ser = serializers.ProjectSerializer(queryset, many=True)
            return Response(ser.data)

    @action(methods=['GET'], detail=False, url_path='search')
    def project_admin_search_view(self, request):
        """Search project for admin"""
        query = self.request.query_params.get('search')
        project_status = self.request.query_params.get('status')
        search_vector = SearchVector('number', weight='A') + \
            SearchVector('manager__first_name', weight='A') + \
            SearchVector('manager__last_name', weight='A') + \
            SearchVector('client__name', weight='A') + \
            SearchVector('deadline', weight="B") + \
            SearchVector('priority', weight="C")
        search_query = SearchQuery(query)
        result = Project.objects.annotate(
            search=search_vector, rank=SearchRank(search_vector, search_query)
                ).filter(rank__gte=0.1,
                         status=project_status).order_by('-rank')
        ser = serializers.ProjectSerializer(result, many=True)
        return Response(ser.data)

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
    def project_employee_status_view(self, request):
        """Project view for employee"""
        project_status = self.request.query_params.get('status')
        forbidden_status = ['Completed', 'Suspended']
        if project_status not in forbidden_status:
            queryset = self.queryset.filter(status=project_status)
            ser = serializers.ProjectSerializer(queryset, many=True)
            return Response(ser.data)
        info = {'message': 'you do not have permissions'}
        return Response(info, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['GET'], detail=False, url_path='search')
    def project_employee_search_view(self, request):
        """Search project for employee"""
        query = self.request.query_params.get('search')
        project_status = self.request.query_params.get('status')
        forbidden_status = ['Completed', 'Suspended']
        if project_status not in forbidden_status:
            search_vector = SearchVector('number', weight='A') + \
                SearchVector('manager__first_name', weight='A') + \
                SearchVector('manager__last_name', weight='A') + \
                SearchVector('client__name', weight='A') + \
                SearchVector('deadline', weight="B") + \
                SearchVector('priority', weight="C")
            search_query = SearchQuery(query)
            result = Project.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
                    ).filter(rank__gte=0.1,
                             status=project_status).order_by('-rank')
            ser = serializers.ProjectSerializer(result, many=True)
            return Response(ser.data)
        info = {'message': 'you do not have permissions'}
        return Response(info, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['GET'], detail=False, url_path='columns')
    def project_employee_columns(self, request):
        """Columns for employee"""
        columns = ['number', 'start', 'deadline',
                   'status', 'progress', 'priority']
        return Response(columns)


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
