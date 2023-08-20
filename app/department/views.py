"""
Views for the department APIs.
"""

from rest_framework import (
    viewsets,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from core.models import (
    Department
)
from department import serializers


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
