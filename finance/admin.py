from django.contrib import admin
from .models import ExtractionTask

@admin.register(ExtractionTask)
class ExtractionTaskAdmin(admin.ModelAdmin):
    list_display = ('submission', 'status', 'model_used', 'processing_time', 'created_at')
    list_filter = ('status', 'model_used', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Task Information', {
            'fields': ('submission', 'status', 'model_used')
        }),
        ('Results', {
            'fields': ('extracted_data', 'error_log', 'processing_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
