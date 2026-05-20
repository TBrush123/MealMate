from flask import Flask, request, jsonify

app = Flask(__name__)


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

if __name__ == '__main__':
    app.run(debug=True, port=6767)