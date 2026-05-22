import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.engine import URL
from urllib.parse import quote_plus

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

encoded_password = quote_plus(db_password)

db_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_username,
    password=db_password,  # pass raw, no encoding needed
    host=db_host,
    port=int(db_port),
    database=db_name
)
print(repr(db_name))

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(app.config["SQLALCHEMY_DATABASE_URI"])

db.init_app(app)

with app.app_context():
    db.create_all()

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

@app.route('/test-db')
def test_db():
    user = User.query.first()
    return "Database connection successful! First user: " + (user.name if user else "No users found.")

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    port = int(os.getenv('FLASK_PORT', 6767))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    app.run(debug=debug_mode, port=port, host=host)