"""
db models
"""
import os

from django.db import models
from django.utils import timezone
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
    name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Client(models.Model):
    """Client Model"""
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, blank=True)
    phone_number = PhoneNumberField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_add = models.DateField(auto_now_add=True)
    color = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name


class Project(models.Model):
    """Project Model"""

    class ProjectStatus(models.TextChoices):
        IN_DESIGN = 'In design'
        STARTED = 'Started'
        COMPLETED = 'Completed'
        SUSPENDDED = 'Suspended'

    class InvoiceStatus(models.TextChoices):
        YES = 'YES'
        LACK_OF_INVOICE = 'YES (LACK OF INVOICE)'
        NO = 'NO'

    class Priority(models.TextChoices):
        HIGH = 'High'
        NORMAL = 'Normal'
        LOW = 'Low'

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
    priority = models.CharField(max_length=20, choices=Priority.choices)
    status = models.CharField(
        max_length=20,
        default='In design',
        choices=ProjectStatus.choices
    )
    number = models.CharField(max_length=255, blank=False)
    secretariat = models.BooleanField(default=True)
    invoiced = models.CharField(
        max_length=30,
        default='NO',
        choices=InvoiceStatus.choices
    )
    date_add = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['deadline']
        indexes = [
            models.Index(fields=['deadline', 'number'])
        ]

    def __str__(self) -> str:
        return self.number


class Department(models.Model):
    """Department Model"""
    name = models.CharField(max_length=255, blank=False, unique=True)
    order = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    date_add = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name


class File(models.Model):
    """File model"""
    class Destiny(models.TextChoices):
        PROJECT = 'Project'
        SECRETARIAT = 'Secretariat'

    def file_path(instance, filename):
        """Generate file path"""
        ext = os.path.splitext(filename)[1]
        filename = os.path.splitext(filename)[0] + ext
        return os.path.join(
            'uploads/projects',
            str(instance.project.id),
            filename
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project,
        related_name='files',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    destiny = models.CharField(
        max_length=30,
        blank=False,
        choices=Destiny.choices
    )
    file = models.FileField(upload_to=file_path, blank=False)
    date_add = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'file'])
        ]

    def __str__(self) -> str:
        return self.name


class QueueLogic(models.Model):
    """QueueLogic model"""
    file = models.ForeignKey(
        File,
        related_name='queue',
        on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE
    )
    chosen = models.BooleanField(default=False)
    permission = models.BooleanField(default=False)
    start = models.BooleanField(default=False)
    paused = models.BooleanField(default=False)
    end = models.BooleanField(default=False)

    class Meta:
        ordering = ['department__order']
        indexes = [
            models.Index(fields=['department'])
        ]


class CommentProject(models.Model):
    """Comment to Project Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(
        Project,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField(blank=False)
    date_posted = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['-date_posted'])
        ]

    def __str__(self) -> str:
        return self.text


class CommentFile(models.Model):
    """Comment to File Model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(
        File,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField(blank=False)
    date_posted = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['-date_posted'])
        ]

    def __str__(self) -> str:
        return self.text
