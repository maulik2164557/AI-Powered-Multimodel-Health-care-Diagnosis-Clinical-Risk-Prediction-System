import os
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

class Config:
    """Base configuration class for the Healthcare System."""
    
    # Security: Used for session signing and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-placeholder-123'
    
    # Database: SQLAlchemy connection URI for PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Management: SRS requirement for medical image storage
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(_file_)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit uploads to 16MB for security
    
    # AI Models: Path to pre-trained weights
    MODEL_PATH = os.path.join(os.path.abspath(os.path.dirname(_file_)), 'models_weights')