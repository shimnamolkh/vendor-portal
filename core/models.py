from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('finance', 'Finance Team'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='vendor')
    vendor_name = models.CharField(max_length=255, blank=True, help_text="Legal name of the vendor")
    vendor_code = models.CharField(max_length=50, blank=True, help_text="Unique vendor code")
    
    def __str__(self):
        if self.user_type == 'vendor':
            return f"{self.vendor_name} ({self.username})"
        return self.username

class AuditModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_by' and 'updated_by' fields.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name="created_%(class)s_set", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name="updated_%(class)s_set", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="User who last updated this record"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ActivityLog(models.Model):
    """
    Model to track user activities for security and auditing.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
