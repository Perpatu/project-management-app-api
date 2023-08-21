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
    'projects-admin',
    views.ProjectAdminViewSet,
    basename='projects-admin'
)
router.register(
    'projects-employee',
    views.ProjectEmployeeViewSet,
    basename='projects-employee'
)
router.register(
    'comments',
    views.CommentProjectViewSet,
    basename='comments'
)

app_name = 'project'

urlpatterns = [
    path('', include(router.urls)),
]
