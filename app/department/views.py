"""
Views for the department APIs.
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from core.models import (
    Department,
    QueueLogic
)
from department import serializers
from file.serializers import DepStatsSerializer


class DepartmentAdminViewSet(mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """View for manage andmin department APIs"""
    serializer_class = serializers.DepartmentSerializer
    queryset = Department.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.DepartmentDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new department"""
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        department = self.get_object()
        #print(department['files'])
        department_pk = department.pk
        context = {'department_pk': department_pk}
        serializer = self.get_serializer(department, context=context)
        return super().retrieve(request, *args, **kwargs)


class StatsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DepStatsSerializer
    queryset = QueueLogic.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Returns a list of how much files are assigned to department"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        department_counts = {}

        for item in data:
            department_name = item["department"]["name"]
            if department_name in department_counts:
                department_counts[department_name] += 1
            else:
                department_counts[department_name] = 1

        result = [
            {
                "quantity": count,
                "department": department_name
            } for department_name, count in department_counts.items()
        ]
        return Response(result)
