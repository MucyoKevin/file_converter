from django.db import models
from django.utils import timezone
import uuid


class FileConversion(models.Model):
    """Model to track file conversions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    CONVERSION_TYPES = [
        ('image', 'Image Conversion'),
        ('document', 'Document Conversion'),
        ('video', 'Video Conversion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    converted_file = models.FileField(upload_to='converted/%Y/%m/%d/', null=True, blank=True)
    original_filename = models.CharField(max_length=255)
    original_format = models.CharField(max_length=10)
    target_format = models.CharField(max_length=10)
    conversion_type = models.CharField(max_length=20, choices=CONVERSION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    file_size = models.BigIntegerField(default=0)  # in bytes
    converted_file_size = models.BigIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['conversion_type']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} -> {self.target_format} ({self.status})"
    
    def get_processing_time(self):
        """Calculate processing time if completed"""
        if self.completed_at:
            return (self.completed_at - self.created_at).total_seconds()
        return None
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)

