from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

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
