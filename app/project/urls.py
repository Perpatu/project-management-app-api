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
    basename='project-admin'
)
router.register(
    'projects-employee',
    views.ProjectEmployeeViewSet,
    basename='project-employee'
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
