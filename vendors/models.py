from django.db import models
from django.conf import settings
from core.models import AuditModel
import uuid

class Submission(AuditModel):
    SUBMISSION_TYPE_CHOICES = (
        ('inward', 'Supplier Inward'),
        ('direct', 'Direct Purchase'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    
    # Verification fields
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_submissions')
    verification_notes = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # created_at and updated_at are inherited from AuditModel
    # created_by and updated_by are inherited from AuditModel

    def __str__(self):
        # Determine valid date display (handle None if not saved yet)
        date_str = self.created_at.date() if self.created_at else "New"
        vendor_display = self.vendor.vendor_name if self.vendor and self.vendor.vendor_name else str(self.vendor)
        return f"{self.get_submission_type_display()} - {vendor_display} ({date_str})"

    class Meta:
        ordering = ['-created_at']

class SubmissionDocument(AuditModel):
    DOCUMENT_TYPE_CHOICES = (
        ('invoice', 'Invoice'),
        ('delivery_order', 'Delivery Order'),
        ('purchase_order', 'Purchase Order'),
        ('other', 'Other Document'),
    )

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='submissions/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="Size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.submission.id}"
