from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash
from config import Config

app = Flask(__name__)

# Configure application using Config class
app.config.from_object(Config)

db = SQLAlchemy(app)

class NewUsers(db.Model):
    __tablename__ = 'new_users'  # Optional, you can explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    folder_path = db.Column(db.String(255), nullable=False)

    image1 = db.Column(db.LargeBinary, nullable=False)
    image2 = db.Column(db.LargeBinary, nullable=False)
    image3 = db.Column(db.LargeBinary, nullable=False)

    image1_filename = db.Column(db.String(255), nullable=False)
    image2_filename = db.Column(db.String(255), nullable=False)
    image3_filename = db.Column(db.String(255), nullable=False)

    # Database model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

def create_user(username, password):
    password = generate_password_hash(password)
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

# Image model (user)
class security_db(db.Model):
    __table_name__ = 'ai_security_images'
    id = db.Column(db.Integer, primary_key=True)

    image_data = db.Column(db.LargeBinary)
    timestamp = db.Column(db.DateTime)


if __name__ == '__main__':
    with app.app_context():
        # Use the inspect function to check if the table exists
        inspector = inspect(db.engine)
        if not inspector.has_table('new_users'):
            db.create_all()
            print("Database table created successfully!")
        else:
            print("Database table already exists!")
        # Example: create a user
        # Uncomment and edit the following line to create a user
        create_user('admin', '1234')
