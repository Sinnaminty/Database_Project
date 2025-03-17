from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def insert_message(content):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    insert_message(data['content'])
    return jsonify({"message": "Data saved!"})

if __name__ == '__main__':
    app.run(debug=True)
