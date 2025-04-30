from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

app = Flask(__name__)

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:gnSSUHvTPjzHEqvYxUXJeYlurycjbiZF@yamabiko.proxy.rlwy.net:41235/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

if __name__ == '__main__':
    with app.app_context():
        # Use the inspect function to check if the table exists
        inspector = inspect(db.engine)
        if not inspector.has_table('new_users'):
            db.create_all()
            print("Database table created successfully!")
        else:
            print("Database table already exists!")
