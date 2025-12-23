import os

SECRET_KEY = os.environ.get('FLASK_KEY', 'super-secret-key')
DB_URL = os.environ.get("DB_URI", "sqlite:///posts.db")
UPLOAD_DESTINATION = 'files/'

APP_ROOT_PATH = os.getcwd() 
