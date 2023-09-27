"""
Views for the user API
"""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import (
    viewsets,
    mixins,
)
from core.models import User
from user.serializers import (
    UserSerializer,
    UserManageSerializer,
    AuthTokenSerializer
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManagerUserView(mixins.ListModelMixin, generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserManageSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user
    

class UserViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """View for users APIs"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @action(methods=['GET'], detail=False, url_path='admin')
    def user_admin_view(self, request):
        """Return admin users"""
        queryset = self.queryset.filter(role='Admin')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='not-admin')
    def user_employee_view(self, request):
        """Return employee users"""
        queryset = self.queryset.filter(role='Employee')
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)    

    @action(methods=['GET'], detail=False, url_path='columns')
    def user_columns_view(self, request):
        """Return columns users"""
        data = ['name', 'email', 'role', 'options']
        return Response(data)
