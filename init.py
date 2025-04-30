from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy import Column, Integer, String,LargeBinary, DateTime


app = Flask(__name__)   

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:SSfdfvxFddLIXGgTLoqqkthDHUOnlgJb@shinkansen.proxy.rlwy.net:45778/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class NewUsers(db.Model):
    __tablename__ = 'new_users'  # Optional, you can explicitly set the table name
    id = Column(Integer, primary_key=True)
    username =Column(String(255), unique=True, nullable=False)
    folder_path = Column(String(255), nullable=False)

    image1 = Column(LargeBinary, nullable=False)
    image2 = Column(LargeBinary, nullable=False)
    image3 = Column(LargeBinary, nullable=False)

    image1_filename = Column(String(255), nullable=False)
    image2_filename = Column(String(255), nullable=False)
    image3_filename = Column(String(255), nullable=False)

    # Database model
class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)


# Image model (user)
class security_db(db.Model):
    __table_name__ = 'ai_security_images'
    id = Column(Integer, primary_key=True)

    image_data = Column(LargeBinary)
    timestamp = Column(DateTime)

def create_user(username, password):
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return user

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
        # create_user('admin', 'your_password')
