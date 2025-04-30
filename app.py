from flask import Flask, render_template, request, url_for ,jsonify,send_file,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_jwt_extended import JWTManager , create_access_token , jwt_required ,get_jwt_identity
import paho.mqtt.client as mqtt
from config import Config
from init import NewUsers, User
import base64
from datetime import datetime,timedelta
import os
import io
from werkzeug.utils import secure_filename
import ssl
from PIL import Image

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['JWT_ACCESS_TOKEN_EXPIRES']=timedelta(minutes=10)
CORS(app)
# Database connection setup

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:gnSSUHvTPjzHEqvYxUXJeYlurycjbiZF@yamabiko.proxy.rlwy.net:41235/railway?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("database url",app.config['SQLALCHEMY_DATABASE_URI'])

jwt= JWTManager(app)
print(app.config['MQTT_BROKER'])
# تخزين بيانات الحساسات
sensor_data = {
    "living room": {"temperature": 0, "humidity": 0},
    "kitchen": {"temperature": 0, "humidity": 0, "gas": 0},
    "garden": {"temperature": 0, "humidity": 0, "soil": 0},
}

# دالة استلام الرسائل من MQTT
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    

    if topic == "home/living room/temp":
        sensor_data["livingroom"]["temperature"] = float(payload)
    elif topic == "home/living room/humidity":
        sensor_data["livingroom"]["humidity"] = float(payload)

    elif topic == "home/kitchen/temp":
        sensor_data["kitchen"]["temperature"] = float(payload)
    elif topic == "home/kitchen/humidity":
        sensor_data["kitchen"]["humidity"] = float(payload)
    elif topic == "home/kitchen/gas":
        sensor_data["kitchen"]["gas"] = float(payload)

    elif topic == "home/garden/temp":
        sensor_data["garden"]["temperature"] = float(payload)
    elif topic == "home/garden/humidity":
        sensor_data["garden"]["humidity"] = float(payload)
    elif topic == "home/garden/soil":
        sensor_data["garden"]["soil"] = float(payload) # Good أو Need to water

    print(f"Received message: {topic} -> {payload}")
    # socketio.emit('mqtt_message',{'topic':topic, 'payload':payload})
# mqtt setup

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(app.config['MQTT_USER'],app.config['MQTT_PASSWORD'])
mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
mqtt_client.on_message = on_message
mqtt_client.connect(app.config['MQTT_BROKER'], app.config['MQTT_PORT'],6000)
mqtt_client.loop_start()

# الاشتراك في المواضيع
mqtt_client.subscribe("home/living room/temp")
mqtt_client.subscribe("home/living room/humidity")
mqtt_client.subscribe("home/kitchen/temp")
mqtt_client.subscribe("home/kitchen/humidity")
mqtt_client.subscribe("home/kitchen/gas")
mqtt_client.subscribe("home/garden/temp")
mqtt_client.subscribe("home/garden/humidity")
mqtt_client.subscribe("home/garden/soil")


# Create tables in the database
with app.app_context():
    db.create_all()

# Image model (user)
class security_db(db.Model):
    __table_name__ = 'ai_security_images'
    id = db.Column(db.Integer, primary_key=True)

    image_data = db.Column(db.LargeBinary)
    timestamp = db.Column(db.DateTime)

 



# Login page
@app.route('/', methods=['GET'])
def loginPage():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
        
    if user and check_password_hash(user.password, password):
        access_token=create_access_token(identity=username)
        return jsonify({"success": True , "token":access_token}) 
    else:
        return jsonify({"success": False , "message":"Invalid username or password"}) ,401


# Registration page

@app.route('/register', methods=['GET', 'POST'])
@jwt_required()
def register():

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"success": False , "message":" Username already exists"}) 
        
        password = generate_password_hash(data.get('password'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({ "success": True ,"redirect": url_for('loginPage')})
    
    return render_template('register.html')
@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    return render_template("index.html")  # Serves the static dashboard page 



 # Logout 
@app.route('/logout' ,methods=['POST']) 
def logout():
    return jsonify({"message":"User logged out " ,"redirect": url_for('loginPage')}),200

@app.route('/control' )
@jwt_required()
def control():
    return render_template("control.html")

@app.route('/monitor' )
@jwt_required()
def monitor():
    return render_template("monitor.html")

@app.route("/sensor-data")
@jwt_required()
def get_sensor_data():
    return jsonify(sensor_data)

@app.route('/upload', methods=['GET', 'POST'])
@jwt_required()
def upload_files():
    if request.method == 'POST':
        username = request.form['username']
        files = request.files.getlist('images')

        if len(files) != 3:
            return "You must upload exactly 3 images!", 400

        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
        os.makedirs(user_folder, exist_ok=True)

        image_data = []
        image_filenames = []

        for file in files:
            file.seek(0)
            image_binary = file.read()
            image_data.append(image_binary)

            filename = secure_filename(file.filename)
            file_path = os.path.join(user_folder, filename)
            with open(file_path, "wb") as f:
                f.write(image_binary)

            image_filenames.append(filename)

        new_user = NewUsers(
            username=username,
            folder_path=user_folder,
            image1=image_data[0],
            image2=image_data[1],
            image3=image_data[2],
            image1_filename=image_filenames[0],
            image2_filename=image_filenames[1],
            image3_filename=image_filenames[2]
        )
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)

        return jsonify({"message":f"Images saved successfully in database and folder: {user_folder}"})

    
    return render_template("upload.html")
@app.route('/gallery/<username>')
@jwt_required()
def gallery(username):
    user = db.session.query(NewUsers).filter_by(username=username).first()
    if not user:
        return {"error": "User not found!"}, 404

    def get_image_data(image_bytes, filename):
        if image_bytes and filename:
            return {
                "filename": filename,
                "data": base64.b64encode(image_bytes).decode('utf-8')  # تحويل الصورة إلى Base64
            }
        return None

    images = list(filter(None, [
        get_image_data(user.image1, user.image1_filename),
        get_image_data(user.image2, user.image2_filename),
        get_image_data(user.image3, user.image3_filename)
    ]))

    user_data = {
        "id": user.id,
        "username": user.username,
        "folder_path": user.folder_path,
        "images": images
    }

    return render_template('gallery.html', user_data=user_data)

@app.route('/uploads/<username>/<filename>')
@jwt_required()
def uploaded_file(username, filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    return send_from_directory(user_folder, filename)







@app.route('/upload_image', methods=['POST'])
@jwt_required()
def upload_image():
    # Get the image data from Postman (or from the frontend)
    data = request.get_json()  # Assuming JSON data is sent
    image_data_base64 = data.get('image_data')

    # Check if image data exists
    if not image_data_base64:
        return "Image data missing", 400
 # Decode the image from Base64
    image_data = base64.b64decode(image_data_base64)
    print(f"Decoded image data length: {len(image_data)}")



    # Create an Image object
    new_image = security_db(
        image_data=image_data,
       
        timestamp=datetime.now()
    )

    # Add and commit the image to the database
    db.session.add(new_image)
    db.session.commit()
    db.session.refresh(new_image)
    print(f"Image uploaded: {new_image.id}, {new_image.timestamp}")

    try:
        return "Image uploaded successfully!", 200
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/view_image/<int:image_id>')
@jwt_required()
def view_image(image_id):
    image = security_db.query.get(image_id)
    if not image:
        return "Image not found!", 404

    # حملي الصورة من البيانات المخزنة في الذاكرة
    image_stream = io.BytesIO(image.image_data)
    try:
        img = Image.open(image_stream)
        try:
            r, g, b = img.split()
            rgb_img = Image.merge("RGB", (b, g, r))
        except:
            rgb_img = img.convert("RGB")
       
        output_stream = io.BytesIO()
        rgb_img.save(output_stream, format="JPEG")
        output_stream.seek(0)
        return send_file(output_stream, mimetype='image/jpeg')
    except Exception as e:
        return f"Failed to process image: {str(e)}", 500


@app.route('/warning')
@jwt_required()
def warning(): 
    # Retrieve images from the database
    images = security_db.query.all()
    
    return render_template('warning.html', images=images)



    
# التحكم بالأضواء
@app.route("/api/lights", methods=["POST"])
@jwt_required()
def toggleLights():
    data = request.json
    room = data.get("room")
    state = data.get("state")

    # نشر رسالة MQTT
    topic = f"home/{room}/lamp"
    mqtt_client.publish(topic, state)
    print(f"Published to {topic}: {state}")

    return jsonify({"message": f"Light in {room} is now {state}", "state": state})

# التحكم بالمراوح
@app.route("/api/fans/state", methods=["POST"])
@jwt_required()
def toggleFans():
    data = request.json
    room = data.get("room")
    state = data.get("state")
    
    # نشر رسالة MQTT
    topic = f"home/{room}/fan"
    mqtt_client.publish(topic, state)
    print(f"Published to {topic}: {state}")

    # print(f"Fan in {room} is {state} ")

    return jsonify({"message": f"Fan in {room} is {state}" ,"state": state})

# التحكم بسرعة المراوح

@app.route("/api/fans/speed", methods=["POST"])
@jwt_required()
def adjustFans():
    data = request.json
    room = data.get("room")
    speed = data.get("speed")

 # نشر رسالة MQTT
    topic = f"home/{room}/fan"
    mqtt_client.publish(topic, speed)
    print(f"Published to {topic}: {speed}")
    # print(f"Fan in {room}  set to  speed {speed}")

    return jsonify({"message": f"Fan in {room}  set to speed {speed}", "speed": speed })

# heater control
@app.route("/api/heater/state", methods=["POST"])
@jwt_required()
def toggleHeater():
    data = request.json
    room = data.get("room")
    state = data.get("state")
    

   
    # نشر رسالة MQTT
    topic = f"home/{room}/heater"
    mqtt_client.publish(topic, state)
    print(f"Published to {topic}: {state}")

    # print(f"Heater in {room} is {state} ")

    return jsonify({"message": f"Heater in {room} is {state}" ,"state": state})

# heater speed control

@app.route("/api/heater/speed", methods=["POST"])
@jwt_required()
def adjustHeater():
    data = request.json
    room = data.get("room")
    speed = data.get("speed")

    # نشر رسالة MQTT
    topic = f"home/{room}/heater"
    mqtt_client.publish(topic, speed)
    print(f"Published to {topic}: {speed}")

    #    print(f"Heater in {room} set to speed {speed}")

    return jsonify({"message": f"Heater in {room}  set to speed {speed}", "speed": speed })

from flask import request

@app.before_request
def log_request_headers():
    print("Request Headers:", request.headers)
    print("Authorization Header:", request.headers.get("Authorization"))

if __name__ == "__main__":
    app.run(debug=True, port=8000)
