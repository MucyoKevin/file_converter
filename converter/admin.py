from django.contrib import admin
from .models import FileConversion


@admin.register(FileConversion)
class FileConversionAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'original_format', 'target_format', 
                    'conversion_type', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'conversion_type', 'original_format', 'target_format', 'created_at']
    search_fields = ['original_filename', 'id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'task_id']
    
    fieldsets = (
        ('File Information', {
            'fields': ('id', 'original_filename', 'original_file', 'converted_file')
        }),
        ('Conversion Details', {
            'fields': ('original_format', 'target_format', 'conversion_type', 'status')
        }),
        ('File Sizes', {
            'fields': ('file_size', 'converted_file_size')
        }),
        ('Task Information', {
            'fields': ('task_id', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )

