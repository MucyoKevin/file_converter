"""
Celery tasks for asynchronous file conversion
"""
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.files import File
from django.utils import timezone
import os
import traceback

from .models import FileConversion
from .utils import get_converter


@shared_task(bind=True, max_retries=3)
def convert_file_task(self, conversion_id):
    """
    Celery task to convert a file from one format to another
    """
    channel_layer = get_channel_layer()
    
    try:
        # Get conversion record
        conversion = FileConversion.objects.get(id=conversion_id)
        conversion.status = 'processing'
        conversion.save()
        
        # Send initial progress via WebSocket
        send_progress_update(channel_layer, conversion_id, 10, 'processing')
        
        # Get source file path
        source_path = conversion.original_file.path
        source_format = conversion.original_format.lower()
        target_format = conversion.target_format.lower()
        
        # Get appropriate converter function
        converter = get_converter(source_format, target_format)
        
        if not converter:
            raise ValueError(
                f"Conversion from {source_format} to {target_format} is not supported"
            )
        
        # Update progress
        send_progress_update(channel_layer, conversion_id, 30, 'processing')
        
        # Perform conversion
        output_path = converter(source_path, target_format)
        
        # Update progress
        send_progress_update(channel_layer, conversion_id, 70, 'processing')
        
        # Save converted file
        if output_path and os.path.exists(output_path):
            base_name = os.path.splitext(conversion.original_filename)[0]
            converted_filename = f"{base_name}_converted.{target_format}"
            
            with open(output_path, 'rb') as f:
                conversion.converted_file.save(
                    converted_filename,
                    File(f),
                    save=False
                )
            
            # Get converted file size
            conversion.converted_file_size = os.path.getsize(output_path)
            
            # Clean up temporary file
            try:
                os.remove(output_path)
            except:
                pass
        
        # Update status
        conversion.status = 'completed'
        conversion.completed_at = timezone.now()
        conversion.save()
        
        # Send completion notification
        send_progress_update(channel_layer, conversion_id, 100, 'completed')
        
        return {
            'status': 'success',
            'conversion_id': str(conversion_id),
            'message': 'Conversion completed successfully'
        }
        
    except FileConversion.DoesNotExist:
        error_msg = f"Conversion record not found: {conversion_id}"
        return {'status': 'error', 'message': error_msg}
        
    except Exception as e:
        # Handle errors
        error_message = str(e)
        error_trace = traceback.format_exc()
        
        try:
            conversion = FileConversion.objects.get(id=conversion_id)
            conversion.status = 'failed'
            conversion.error_message = f"{error_message}\n\n{error_trace}"
            conversion.save()
            
            # Send error notification
            send_progress_update(channel_layer, conversion_id, 0, 'failed', error_message)
        except:
            pass
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        return {
            'status': 'error',
            'conversion_id': str(conversion_id),
            'message': error_message
        }


def send_progress_update(channel_layer, conversion_id, progress, status, error=None):
    """
    Send progress update via WebSocket
    """
    try:
        async_to_sync(channel_layer.group_send)(
            f'conversion_{conversion_id}',
            {
                'type': 'conversion_progress',
                'conversion_id': str(conversion_id),
                'progress': progress,
                'status': status,
                'error': error
            }
        )
    except Exception as e:
        print(f"Error sending WebSocket message: {e}")


@shared_task
def cleanup_old_files(days=7):
    """
    Cleanup old conversion files
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_conversions = FileConversion.objects.filter(created_at__lt=cutoff_date)
    
    deleted_count = 0
    for conversion in old_conversions:
        try:
            # Delete files
            if conversion.original_file:
                conversion.original_file.delete()
            if conversion.converted_file:
                conversion.converted_file.delete()
            
            # Delete record
            conversion.delete()
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting conversion {conversion.id}: {e}")
    
    return {
        'status': 'success',
        'deleted_count': deleted_count,
        'message': f'Cleaned up {deleted_count} old conversions'
    }

