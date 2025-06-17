from django.contrib.auth.models import AbstractUser
from django.db import models

class Patient(AbstractUser):
    # Add any additional fields specific to a patient here in the future
    # For example: date_of_birth, address, phone_number
    # For now, we'll rely on AbstractUser fields and add more later.
    email = models.EmailField(unique=True) # Ensure email is unique for login

    # Specify unique related_name arguments to avoid clashes with default User model
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='patient_set', # Unique related_name
        related_query_name='patient'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='patient_set', # Unique related_name
        related_query_name='patient'
    )

    def __str__(self):
        return self.username
