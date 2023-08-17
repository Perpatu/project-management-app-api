"""
Test for comment project APIs
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import CommentProject, Client, Project

from project.serializers import CommentProjectSerializer


COMMENT_PROJECT_URL = reverse('project:comments-list')


def create_user(email='test@example.com', password='testpass123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


def create_client(**params):
    """Create and retrun a test client"""
    defaults = {
        'name': 'Test name client',
        'email': 'clien@example.com',
        'phone_number': '+1 604 401 1234',
        'address': 'Test street 56',
    }
    defaults.update(params)

    client = Client.objects.create(**defaults)
    return client


def create_project(user, **params):
    """Create and retrun a test client"""
    client_obj = create_client()

    defaults = {
        'start': '2023-08-15',
        'deadline': '2023-10-15',
        'priority': 'In design',
        'number': 'Test number project'
    }
    defaults.update(params)

    project = Project.objects.create(
        manager=user,
        client=client_obj,
        **defaults
    )
    return project


class PublicCommentProjectApiTests(TestCase):
    """Test unauthenticated API request"""

    def setUP(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(COMMENT_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentProjectApiTests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrive_commentprojects(self):
        """Test retrieving a list of comment projects"""
        project = create_project(user=self.user)
        CommentProject.objects.create(
            user=self.user,
            project=project,
            text='Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n'
                 'Nullam et enim blandit, mattis magna quis,\n'
                 'elementum risus. Duis ipsum ex.'
        )
        CommentProject.objects.create(
            user=self.user,
            project=project,
            text='Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        )

        res = self.client.get(COMMENT_PROJECT_URL)

        comments = CommentProject.objects.all().order_by('date_posted')
        serializer = CommentProjectSerializer(comments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
