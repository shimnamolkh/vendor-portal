from django.db import models
from vendors.models import Submission

class ExtractionTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='extraction_task')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Store the raw JSON output from Ollama
    extracted_data = models.JSONField(null=True, blank=True)
    
    # Store any error messages
    error_log = models.TextField(blank=True)
    
    # Metadata about the extraction process
    model_used = models.CharField(max_length=50, default='llava:7b')
    processing_time = models.FloatField(null=True, help_text="Time taken in seconds")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Extraction for {self.submission.id} - {self.status}"
