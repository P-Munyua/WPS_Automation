# utils/file_handlers.py
import os
from django.conf import settings
from django.http import HttpResponse
from wsgiref.util import FileWrapper

class FileHandler:
    @staticmethod
    def get_file_path(file_field):
        """Get absolute file path from FileField"""
        if file_field and file_field.name:
            return os.path.join(settings.MEDIA_ROOT, file_field.name)
        return None
    
    @staticmethod
    def file_exists(file_field):
        """Check if file exists"""
        file_path = FileHandler.get_file_path(file_field)
        return file_path and os.path.exists(file_path)
    
    @staticmethod
    def get_file_size(file_field):
        """Get file size in bytes"""
        file_path = FileHandler.get_file_path(file_field)
        if file_path and os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    @staticmethod
    def delete_file(file_field):
        """Delete physical file"""
        if file_field:
            file_path = FileHandler.get_file_path(file_field)
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return True
                except OSError:
                    return False
        return False
    
    @staticmethod
    def create_download_response(file_field, filename=None):
        """Create HTTP response for file download"""
        if not FileHandler.file_exists(file_field):
            return None
        
        file_path = FileHandler.get_file_path(file_field)
        if not filename:
            filename = os.path.basename(file_path)
        
        try:
            wrapper = FileWrapper(open(file_path, 'rb'))
            response = HttpResponse(wrapper, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = os.path.getsize(file_path)
            return response
        except IOError:
            return None