from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Set default role for superuser
        return self.create_user(username, email, password, **extra_fields)

class users(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        QA = 'qa', 'QA'
        STAFF = 'staff', 'Staff'

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length = 20, 
        choices = Roles.choices,
        default = Roles.STAFF
    )
    dob = models.DateField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    department = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role', 'first_name', 'dob', 'last_name', 'department']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_manager(self):
        return self.role == self.Roles.MANAGER