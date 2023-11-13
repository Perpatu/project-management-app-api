"""
ULR mapping for the project app
"""

from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from project import views


router = DefaultRouter()
router.register(
    'admin',
    views.ProjectAdminViewSet,
    basename='admin'
)
router.register(
    'auth',
    views.ProjectAuthViewSet,
    basename='auth'
)
router.register(
    'comments',
    views.CommentProjectViewSet,
    basename='comments'
)
router.register(
    'notification',
    views.NotificationsProjectView,
    basename='notification'
)

app_name = 'project'

urlpatterns = [
    path('', include(router.urls)),
]
