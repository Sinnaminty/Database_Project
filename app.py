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


@app.route('/get_messages', methods=['GET'])
def get_messages():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)


@app.route('/get_message/<int:msg_id>', methods=['GET'])
def get_message(msg_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
    message = cursor.fetchone()
    conn.close()
    
    if message:
        return jsonify({"id": message[0], "content" : message[1]})
    else:
        return jsonify({"error": "No entry found for this ID"}), 404


if __name__ == '__main__':
    app.run(debug=True)
