import os
import random
import string

from helpers.config import get_settings

class BaseController:
    
    def __init__(self):
        
        self.app_settings = get_settings()
        
        my_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(my_dir) 
        self.files_dir = os.path.join(self.base_dir, "assets", "files")
    
    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
