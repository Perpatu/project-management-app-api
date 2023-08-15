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
    views.ProjectViewAdminSet,
    basename='project-admin'
)
router.register(
    'projects-employee',
    views.ProjectViewEmployeeSet,
    basename='project-employee'
)

app_name = 'project'

urlpatterns = [
    path('', include(router.urls)),
]
