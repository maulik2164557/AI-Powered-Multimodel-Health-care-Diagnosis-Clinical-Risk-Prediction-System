from . import db
from datetime import datetime

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='doctor') # doctor, admin, researcher

class Patient(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Diagnosis(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    result = db.Column(db.String(200)) # e.g., 'Glioblastoma Detected'
    risk_score = db.Column(db.Float) # Clinical Risk Prediction
    image_path = db.Column(db.String(255)) # Path to scan in static/uploads
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)