from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize the database object - we will configure it fully tomorrow
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Link the database to the app
    db.init_app(app)

    # Placeholder for routes - your team will add these here later
    with app.app_context():
        # This is where we will import your login and diagnosis logic
        pass

    return app