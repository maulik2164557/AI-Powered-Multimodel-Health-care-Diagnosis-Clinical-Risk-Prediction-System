import os
from dotenv import load_dotenv

# Load environment variables (useful for SECRET_KEY)
load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuration for SQLite3 and Healthcare App."""
    
    # Security key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hc-dev-secret-key-999'
    
    # DATABASE: Points to app.db in your project root folder
    # SQLite format: sqlite:/// (three slashes for relative path)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Folders for medical images
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    MODEL_PATH = os.path.join(basedir, 'models_weights')