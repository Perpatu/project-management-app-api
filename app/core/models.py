"""
db models
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Manager for user"""

    def create_user(self, email, password=None, **extra_field):
        """create, save and return a new user"""
        if not email:
            raise ValueError('User must have email address')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Client(models.Model):
    """Client Model"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, blank=True)
    phone_number = PhoneNumberField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_add = models.DateField(auto_now_add=True)
    color = models.CharField(max_length=30, blank=True)

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    """Project Model"""
    priority_choice = [
        ('High', 'High'),
        ('Normal', 'Normal'),
        ('Low', 'Low')
    ]

    status_choice = [
        ('In design', 'In design'),
        ('Started', 'Started'),
        ('Completed', 'Completed'),
        ('Suspended', 'Suspended')
    ]

    id = models.AutoField(primary_key=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    start = models.DateField(blank=False)
    deadline = models.DateField(blank=False)
    progress = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    priority = models.CharField(max_length=20, choices=priority_choice)
    status = models.CharField(
        max_length=20,
        default='In design',
        choices=status_choice
    )
    number = models.CharField(max_length=255, blank=False)
    secretariat = models.BooleanField(default=True)
    invoiced = models.CharField(max_length=30, default='NO')

    def __str__(self) -> str:
        return self.number
