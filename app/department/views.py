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
    QueueLogic,
)
from department import serializers


class DepartmentAdminViewSet(mixins.CreateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    """View for manage admin department APIs"""
    serializer_class = serializers.DepartmentSerializer
    queryset = Department.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """Create a new department"""
        serializer.save()


class DepartmentAuthViewSet(mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """View for auth users department APIs"""
    serializer_class = serializers.DepartmentStatsSerializer
    queryset = QueueLogic.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Returns a list of how much files are assigned to department"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        dep_info_dict = {}

        for item in data:
            dep_info = item["department"]
            dep_id = dep_info["id"]
            dep_name = dep_info["name"]
            
            if dep_name in dep_info_dict:
                dep_info_dict[dep_name]["quantity"] += 1
            else:
                dep_info_dict[dep_name] = {
                    "id": dep_id,
                    "quantity": 1,
                    "name": dep_name
                }

        result = list(dep_info_dict.values())
        return Response(result)
