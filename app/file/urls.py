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
    'admin',
    views.FileAdminViewSet,
    basename='admin'
)
router.register(
    'auth',
    views.FileAuthViewSet,
    basename='auth'
)
router.register(
    'comments',
    views.CommentFileViewSet,
    basename='comments'
)
router.register(
    'queue-logic',
    views.QueueLogicViewSet,
    basename='queue-logic'
)

app_name = 'file'

urlpatterns = [
    path('', include(router.urls)),
]
