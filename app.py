from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DB_FILE = "database.db"

def create_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_messages', methods=['GET'])
def get_messages():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return jsonify(messages)


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    messages = data.get("content", [])

    if messages:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for message in messages:
            cursor.execute("INSERT INTO messages (content) VALUES (?)", (message.strip(),))

        conn.commit()
        conn.close()
        return jsonify({"message": f"{len(messages)} message(s) added successfully"}), 201

    return jsonify({"error": "Message content is required"}), 400


@app.route('/get_message/<int:msg_id>', methods=['GET'])
def get_message(msg_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
    message = cursor.fetchone()
    conn.close()
 
    if message:
        return jsonify({"id" : message[0], "content" : message[1]})
    else:
        return jsonify({"error": "Message not found"}), 404


@app.route('/delete_messages', methods=['POST'])
def delete_messages():
    data = request.json
    ids = data.get("ids", [])

    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    # Convert all IDs to integers
    try:
        ids = [int(id_str) for id_str in ids]
    except ValueError:
        return jsonify({"error": "All IDs must be valid integers"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if all provided IDs exist in the database
    cursor.execute("SELECT id FROM messages WHERE id IN ({})".format(",".join("?" for _ in ids)), ids)
    existing_ids = [row[0] for row in cursor.fetchall()]

    # Find the missing IDs
    missing_ids = set(ids) - set(existing_ids)

    if missing_ids:
        conn.close()
        return jsonify({"error": f"Message(s) with IDs {', '.join(map(str, missing_ids))} not found"}), 404

    # Delete messages with the specified IDs
    cursor.execute("DELETE FROM messages WHERE id IN ({})".format(",".join("?" for _ in ids)), ids)
    conn.commit()

    # Re-enumerate the IDs
    cursor.execute("SELECT id FROM messages ORDER BY id")
    rows = cursor.fetchall()
    for index, row in enumerate(rows, start=1):
        cursor.execute("UPDATE messages SET id = ? WHERE id = ?", (index, row[0]))

    conn.commit()

    # Reset the auto-increment counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
    conn.commit()

    conn.close()
    return jsonify({"message": "Messages deleted successfully"})


@app.route('/update_message/<int:msg_id>', methods=['PUT'])
def update_message(msg_id):
    data = request.json
    new_content = data.get("content")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
    message = cursor.fetchone()

    if not message:
        conn.close()
        return jsonify({"error": "Message not found"}), 404

    if new_content:
        cursor.execute("UPDATE messages SET content=? WHERE id=?", (new_content, msg_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Message updated successfully"})
    return jsonify({"error" : "New content is required"}), 400


if __name__ == '__main__':
    app.run(debug=True)
