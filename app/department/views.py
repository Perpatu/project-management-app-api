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

from core.models import (
    Department,
    QueueLogic
)
from department import serializers
from file.serializers import DepStatsSerializer


class DepartmentAdminViewSet(viewsets.ModelViewSet):
    """View for manage andmin department APIs"""
    serializer_class = serializers.DepartmentSerializer
    queryset = Department.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new department"""
        serializer.save()


class DepartmentEmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """View for manage employee project APIs"""
    serializer_class = serializers.DepartmentSerializer
    queryset = Department.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


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
