import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.engine import URL
from urllib.parse import quote_plus
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from extensions import db
from models import User, Ingredient, FridgeItem, RevokedToken

load_dotenv()

app = Flask(__name__)
cors = CORS(app, origins="*")


db_username = os.getenv('DB_USERNAME', 'root')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'Mealmate')
db_port = os.getenv('DB_PORT', '5432')
jwt_secret_key = os.getenv('JWT_SECRET_KEY')

if not jwt_secret_key:
    raise ValueError("JWT_SECRET_KEY is not set in the environment variables.")

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

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload.get('jti')
    if not jti:
        return True
    return RevokedToken.query.filter_by(jti=jti).first() is not None

# Authorization

@app.route('/api/users', methods=['GET'])
def users():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400

    ph = PasswordHasher()
    hashed_password = ph.hash(password)

    

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists."}), 400
    ph = PasswordHasher()

    hashed_password = ph.hash(password)

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


    try:
        ph.verify(user.password_hash, password)
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "message": "Login successful."}), 200
    except (VerifyMismatchError, InvalidHashError):
        return jsonify({"error": "Invalid username or password."}), 401

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt().get('jti')
    if not jti:
        return jsonify({"error": "Invalid token."}), 401

    expires_timestamp = get_jwt().get('exp')
    expires_at = datetime.utcfromtimestamp(expires_timestamp) if expires_timestamp else datetime.utcnow()
    revoked_token = RevokedToken(
        jti=jti,
        user_id=get_jwt_identity(),
        expires_at=expires_at,
        revoked_at=datetime.utcnow()
    )
    db.session.add(revoked_token)
    db.session.commit()

    return jsonify({"message": "Logout successful."}), 200

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
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