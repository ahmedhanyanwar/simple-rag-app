# from .file import class
from fastapi import UploadFile
import re
import os

from models import ResponseSignal
from .BaseController import BaseController
from .ProjectController import ProjectController

class DataController(BaseController): # inhirts from it
    
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024 # convert MB to bytes
    
    def validate_uploaded_file(self, file: UploadFile):
    
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_UPLOADED_SUCCESS.value
    
    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        
        cleaned_filename = self.get_clean_filename(orig_file_name)
        
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_filename
        )

        # Make sure that new_file_oath is unique
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_filename
            )

        return new_file_path, random_key + "_" + cleaned_filename

    def get_clean_filename(self, orig_filename: str):

        cleaned_filename = re.sub(r'[^\w.]', '',orig_filename.strip())
        cleaned_filename = cleaned_filename.replace(" ", "_")
        
        return cleaned_filename

