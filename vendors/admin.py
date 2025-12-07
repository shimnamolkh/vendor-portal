from django.contrib import admin
from .models import Submission, SubmissionDocument

class SubmissionDocumentInline(admin.TabularInline):
    model = SubmissionDocument
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'submission_type', 'status', 'created_at')
    list_filter = ('submission_type', 'status', 'created_at')
    search_fields = ('vendor__username', 'vendor__vendor_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SubmissionDocumentInline]
    
    fieldsets = (
        ('Submission Information', {
            'fields': ('vendor', 'submission_type', 'status', 'remarks')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verification_notes', 'verified_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(SubmissionDocument)
class SubmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'document_type', 'original_name', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
