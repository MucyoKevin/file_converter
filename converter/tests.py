from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import FileConversion
import io
from PIL import Image


class FileConversionTestCase(TestCase):
    """Test cases for file conversion"""
    
    def setUp(self):
        self.client = Client()
    
    def test_create_conversion(self):
        """Test creating a conversion record"""
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            img_io.getvalue(),
            content_type="image/jpeg"
        )
        
        conversion = FileConversion.objects.create(
            original_file=uploaded_file,
            original_filename="test.jpg",
            original_format="jpg",
            target_format="png",
            conversion_type="image",
            file_size=len(img_io.getvalue())
        )
        
        self.assertEqual(conversion.status, 'pending')
        self.assertEqual(conversion.original_format, 'jpg')
        self.assertEqual(conversion.target_format, 'png')
    
    def test_index_page(self):
        """Test index page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_convert_page(self):
        """Test convert page loads"""
        response = self.client.get('/convert/image/')
        self.assertEqual(response.status_code, 200)

        

