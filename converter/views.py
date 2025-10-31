from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
import os
import json

from .models import FileConversion
from .forms import FileUploadForm
from .tasks import convert_file_task


def index(request):
    """Home page with conversion options"""
    return render(request, 'converter/index.html')


def convert_file(request, conversion_type):
    """Page for specific conversion type"""
    if conversion_type not in ['image', 'document', 'video']:
        raise Http404("Invalid conversion type")
    
    form = FileUploadForm(conversion_type=conversion_type)
    context = {
        'conversion_type': conversion_type,
        'form': form,
    }
    return render(request, 'converter/convert.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """Handle file upload and start conversion"""
    try:
        file = request.FILES.get('file')
        target_format = request.POST.get('target_format')
        conversion_type = request.POST.get('conversion_type')
        
        if not all([file, target_format, conversion_type]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            }, status=400)
        
        # Validate file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            return JsonResponse({
                'success': False,
                'error': f'File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB'
            }, status=400)
        
        # Get original format
        original_format = os.path.splitext(file.name)[1][1:].lower()
        
        # Validate format
        all_formats = (settings.SUPPORTED_IMAGE_FORMATS + 
                      settings.SUPPORTED_DOCUMENT_FORMATS + 
                      settings.SUPPORTED_VIDEO_FORMATS)
        
        if original_format not in all_formats:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported file format: {original_format}'
            }, status=400)
        
        # Create conversion record
        conversion = FileConversion.objects.create(
            original_file=file,
            original_filename=file.name,
            original_format=original_format,
            target_format=target_format.lower(),
            conversion_type=conversion_type,
            file_size=file.size,
            status='pending'
        )
        
        # Start async conversion task
        task = convert_file_task.delay(str(conversion.id))
        conversion.task_id = task.id
        conversion.save()
        
        return JsonResponse({
            'success': True,
            'conversion_id': str(conversion.id),
            'message': 'File uploaded successfully. Conversion started.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def conversion_status(request, conversion_id):
    """Get conversion status"""
    try:
        conversion = get_object_or_404(FileConversion, id=conversion_id)
        
        data = {
            'id': str(conversion.id),
            'status': conversion.status,
            'original_filename': conversion.original_filename,
            'original_format': conversion.original_format,
            'target_format': conversion.target_format,
            'created_at': conversion.created_at.isoformat(),
            'updated_at': conversion.updated_at.isoformat(),
        }
        
        if conversion.status == 'completed':
            data['download_url'] = f'/api/download/{conversion.id}/'
            data['completed_at'] = conversion.completed_at.isoformat()
            data['processing_time'] = conversion.get_processing_time()
        elif conversion.status == 'failed':
            data['error_message'] = conversion.error_message
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def download_file(request, conversion_id):
    """Download converted file"""
    try:
        conversion = get_object_or_404(FileConversion, id=conversion_id)
        
        if conversion.status != 'completed':
            return JsonResponse({
                'error': 'File conversion not completed yet'
            }, status=400)
        
        if not conversion.converted_file:
            return JsonResponse({
                'error': 'Converted file not found'
            }, status=404)
        
        # Get file path
        file_path = conversion.converted_file.path
        
        if not os.path.exists(file_path):
            return JsonResponse({
                'error': 'File not found on server'
            }, status=404)
        
        # Prepare filename
        base_name = os.path.splitext(conversion.original_filename)[0]
        download_filename = f"{base_name}_converted.{conversion.target_format}"
        
        # Return file
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=download_filename
        )
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def conversion_history(request):
    """Get conversion history"""
    try:
        # Check if it's an API request (JSON)
        if request.headers.get('Accept') == 'application/json' or request.GET.get('format') == 'json':
            limit = int(request.GET.get('limit', 10))
            conversions = FileConversion.objects.all()[:limit]
            
            data = {
                'conversions': [
                    {
                        'id': str(c.id),
                        'original_filename': c.original_filename,
                        'original_format': c.original_format,
                        'target_format': c.target_format,
                        'status': c.status,
                        'conversion_type': c.conversion_type,
                        'created_at': c.created_at.isoformat(),
                        'file_size_mb': c.get_file_size_mb(),
                    }
                    for c in conversions
                ]
            }
            
            return JsonResponse(data)
        
        # Render HTML page
        limit = int(request.GET.get('limit', 50))
        conversions = FileConversion.objects.all()[:limit]
        
        context = {
            'conversions': conversions,
            'total_count': FileConversion.objects.count(),
        }
        
        return render(request, 'converter/history.html', context)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_conversion(request, conversion_id):
    """Delete a conversion record and its files"""
    try:
        conversion = get_object_or_404(FileConversion, id=conversion_id)
        
        # Delete files from storage
        if conversion.original_file:
            if os.path.exists(conversion.original_file.path):
                os.remove(conversion.original_file.path)
        
        if conversion.converted_file:
            if os.path.exists(conversion.converted_file.path):
                os.remove(conversion.converted_file.path)
        
        # Delete database record
        conversion.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Conversion deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

