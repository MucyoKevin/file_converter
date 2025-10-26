from django import forms
from django.conf import settings


class FileUploadForm(forms.Form):
    """Form for uploading files to convert"""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': ','.join([f'.{ext}' for ext in 
                               settings.SUPPORTED_IMAGE_FORMATS + 
                               settings.SUPPORTED_DOCUMENT_FORMATS + 
                               settings.SUPPORTED_VIDEO_FORMATS]),
            'id': 'file-upload'
        })
    )
    target_format = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={
            'class': 'format-select',
            'id': 'target-format'
        })
    )
    
    def __init__(self, *args, **kwargs):
        conversion_type = kwargs.pop('conversion_type', None)
        super().__init__(*args, **kwargs)
        
        if conversion_type == 'image':
            self.fields['target_format'].choices = [
                ('jpg', 'JPG'),
                ('png', 'PNG'),
                ('gif', 'GIF'),
                ('bmp', 'BMP'),
                ('webp', 'WebP'),
                ('tiff', 'TIFF'),
            ]
        elif conversion_type == 'document':
            self.fields['target_format'].choices = [
                ('pdf', 'PDF'),
                ('docx', 'DOCX'),
                ('txt', 'TXT'),
            ]
        elif conversion_type == 'video':
            self.fields['target_format'].choices = [
                ('mp4', 'MP4'),
                ('avi', 'AVI'),
                ('mov', 'MOV'),
                ('mkv', 'MKV'),
            ]
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size
            if file.size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError(
                    f'File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB'
                )
        return file

