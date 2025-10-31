"""
Custom storage backend for Supabase Storage
"""

from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client, Client
from io import BytesIO
import mimetypes
import os


class SupabaseStorage(Storage):
    """
    Custom Django storage backend for Supabase Storage.
    Allows storing uploaded and converted files in Supabase buckets.
    """
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
        
        # Initialize Supabase client
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            # Try to get bucket info
            buckets = self.client.storage.list_buckets()
            bucket_exists = any(b.name == self.bucket_name for b in buckets)
            
            if not bucket_exists:
                # Create public bucket
                self.client.storage.create_bucket(
                    self.bucket_name,
                    options={"public": True}
                )
                print(f"Created Supabase bucket: {self.bucket_name}")
        except Exception as e:
            print(f"Note: Could not verify/create bucket: {e}")
            # Bucket might already exist, continue anyway
    
    def _save(self, name, content):
        """
        Save file to Supabase Storage
        
        Args:
            name: File path/name
            content: File content (file object or bytes)
            
        Returns:
            str: The name of the saved file
        """
        try:
            # Read content
            if hasattr(content, 'read'):
                file_content = content.read()
                # Reset file pointer if possible
                if hasattr(content, 'seek'):
                    content.seek(0)
            else:
                file_content = content
            
            # Determine content type
            content_type = self._guess_content_type(name)
            
            # Upload to Supabase
            # Remove existing file if it exists
            try:
                self.client.storage.from_(self.bucket_name).remove([name])
            except:
                pass  # File doesn't exist, that's fine
            
            # Upload new file
            self.client.storage.from_(self.bucket_name).upload(
                name,
                file_content,
                file_options={"content-type": content_type, "upsert": "true"}
            )
            
            return name
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            raise
    
    def _open(self, name, mode='rb'):
        """
        Download and open file from Supabase Storage
        
        Args:
            name: File path/name
            mode: File open mode (default 'rb')
            
        Returns:
            BytesIO: File-like object
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(name)
            return BytesIO(response)
        except Exception as e:
            print(f"Error downloading from Supabase: {e}")
            raise IOError(f"File not found: {name}")
    
    def exists(self, name):
        """
        Check if file exists in Supabase Storage
        
        Args:
            name: File path/name
            
        Returns:
            bool: True if file exists
        """
        try:
            # Try to get file info by listing the directory
            path_parts = name.split('/')
            if len(path_parts) > 1:
                directory = '/'.join(path_parts[:-1])
                filename = path_parts[-1]
            else:
                directory = ''
                filename = name
            
            files = self.client.storage.from_(self.bucket_name).list(directory)
            return any(f['name'] == filename for f in files)
        except:
            return False
    
    def url(self, name):
        """
        Get public URL for file
        
        Args:
            name: File path/name
            
        Returns:
            str: Public URL or signed URL
        """
        try:
            # Try to get public URL first
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(name)
            return public_url
        except:
            # Fallback: create signed URL (valid for 1 hour)
            try:
                response = self.client.storage.from_(self.bucket_name).create_signed_url(
                    name,
                    expires_in=3600  # 1 hour
                )
                return response.get('signedURL', '')
            except Exception as e:
                print(f"Error getting URL from Supabase: {e}")
                return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"
    
    def delete(self, name):
        """
        Delete file from Supabase Storage
        
        Args:
            name: File path/name
        """
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except Exception as e:
            print(f"Error deleting from Supabase: {e}")
    
    def size(self, name):
        """
        Get file size
        
        Args:
            name: File path/name
            
        Returns:
            int: File size in bytes
        """
        try:
            path_parts = name.split('/')
            if len(path_parts) > 1:
                directory = '/'.join(path_parts[:-1])
                filename = path_parts[-1]
            else:
                directory = ''
                filename = name
            
            files = self.client.storage.from_(self.bucket_name).list(directory)
            for f in files:
                if f['name'] == filename:
                    return f.get('metadata', {}).get('size', 0)
            return 0
        except:
            return 0
    
    def listdir(self, path):
        """
        List contents of a directory
        
        Args:
            path: Directory path
            
        Returns:
            tuple: (directories, files)
        """
        try:
            files = self.client.storage.from_(self.bucket_name).list(path)
            directories = []
            file_list = []
            
            for f in files:
                if f.get('id') is None:  # It's a directory
                    directories.append(f['name'])
                else:
                    file_list.append(f['name'])
            
            return (directories, file_list)
        except:
            return ([], [])
    
    def _guess_content_type(self, name):
        """
        Guess content type from filename
        
        Args:
            name: Filename
            
        Returns:
            str: MIME type
        """
        content_type, _ = mimetypes.guess_type(name)
        return content_type or 'application/octet-stream'
    
    def get_valid_name(self, name):
        """
        Return a filename suitable for use with the storage system
        """
        # Clean the filename
        name = name.replace('\\', '/')
        return name
    
    def get_available_name(self, name, max_length=None):
        """
        Return a filename that's available in the storage mechanism
        """
        # For Supabase, we can overwrite files, so just return the name
        return name

