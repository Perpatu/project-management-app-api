"""
ULR mapping for the department app
"""

from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from department import views


router = DefaultRouter()
router.register(
    'department-admin',
    views.DepartmentAdminViewSet,
    basename='department-admin'
)
router.register(
    'department-employee',
    views.DepartmentEmployeeViewSet,
    basename='department-employee'
)

app_name = 'department'

urlpatterns = [
    path('', include(router.urls)),
]
