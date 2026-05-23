import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.engine import URL
from urllib.parse import quote_plus
from argon2 import PasswordHasher

from extensions import db
from models import User, Ingredient, FridgeItem 

load_dotenv()

app = Flask(__name__)
cors = CORS(app, origins="*")


db_username = os.getenv('DB_USERNAME', 'root')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'Mealmate')
db_port = os.getenv('DB_PORT', '5432')
jwt_secret_key = os.getenv('JWT_SECRET_KEY', 'super_duper_secret_key_that_should_be_changed_in_production')

encoded_password = quote_plus(db_password)

db_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_username,
    password=db_password,  # pass raw, no encoding needed
    host=db_host,
    port=int(db_port),
    database=db_name
)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = jwt_secret_key
jwt = JWTManager(app)

db.init_app(app)

with app.app_context():
    db.create_all()

# Authorization

@app.route('/api/users', methods=['GET'])
def users():
    return jsonify(
    {"users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
        ]
    }
    )

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    ph = PasswordHasher()

    hashed_password = ph.hash(password)

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    ph = PasswordHasher()

    access_token = create_access_token(identity=user.id)

    try:
        ph.verify(user.password_hash, password)
        return jsonify({"access_token": access_token, "message": "Login successful."}), 200
    except Exception as e:
        return jsonify({"error": "Invalid username or password."}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout successful."}), 200

@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token}), 200

@app.route('/test-db')
def test_db():
    user = User.query.first()
    return "Database connection successful! First user: " + (user.username if user else "No users found.")

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    port = int(os.getenv('FLASK_PORT', 6767))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    app.run(debug=debug_mode, port=port, host=host)