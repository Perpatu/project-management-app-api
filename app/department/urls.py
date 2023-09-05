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
    'admin',
    views.DepartmentAdminViewSet,
    basename='admin'
)
router.register(
    'stats',
    views.StatsViewSet,
    basename='stats'
)
app_name = 'department'

urlpatterns = [
    path('', include(router.urls)),
]
