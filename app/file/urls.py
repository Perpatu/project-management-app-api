"""
ULR mapping for the file app
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from file import views

router = DefaultRouter()
router.register(
    'files-admin',
    views.FileAdminViewSet,
    basename='files-admin'
)

app_name = 'file'

urlpatterns = [
    path('', include(router.urls)),
]