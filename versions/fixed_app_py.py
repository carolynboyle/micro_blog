from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sys
import os

# Create Flask app instance
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///microblog.db'  # Adjust if you use a different DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Make db available for routes.py imports
sys.modules[__name__].db = db

# Import models to ensure they're registered
from models import User, Post

# Import and register the Blueprint
# Note: This assumes routes.py is in the same directory and uses relative imports
import routes
app.register_blueprint(routes.main)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)