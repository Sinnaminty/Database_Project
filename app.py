from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DB_FILE = "database.db"

def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # customer table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_first_name TEXT NOT NULL,
        customer_last_name TEXT NOT NULL,
        customer_phone_number TEXT NOT NULL
    )
    """)

    # cars table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_make TEXT NOT NULL,
        car_model TEXT NOT NULL,
        car_license_plate TEXT NOT NULL,
        customer_id INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)

    # services table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_title TEXT NOT NULL,
        service_cost REAL NOT NULL
    )
    """)

    # technicians table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS technicians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        technician_first_name TEXT NOT NULL,
        technician_last_name TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_first_name, customer_last_name, customer_phone_number FROM customers")
    customers = cursor.fetchall()
    conn.close()

    # Return customer data as JSON
    return jsonify([{'id': customer[0], 'customer_first_name': customer[1], 'customer_last_name': customer[2], 'customer_phone_number': customer[3]} for customer in customers])


@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    customer_first_name = data.get("customer_first_name")
    customer_last_name = data.get("customer_last_name")
    customer_phone_number = data.get("customer_phone_number")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (customer_first_name, customer_last_name, customer_phone_number) VALUES (?, ?, ?)", (customer_first_name, customer_last_name, customer_phone_number))
    conn.commit()
    conn.close()
    return jsonify({"message": "Customer added successfully"}), 201

        

@app.route('/add_car', methods=['POST'])
def add_car():
    data = request.json
    car_make = data.get("car_make")
    car_model = data.get("car_model")
    car_license_plate = data.get("car_license_plate")
    customer_id = data.get("customer_id")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cars (car_make, car_model, car_license_plate, customer_id) VALUES (?, ?, ?, ?)",
                   (car_make, car_model, car_license_plate, customer_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Car added successfully"}), 201

@app.route('/add_service', methods=['POST'])
def add_service():
    data = request.json
    service_name = data.get("service_title")
    service_cost = data.get("service_cost")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services (service_name, service_cost) VALUES (?, ?)", (service_name, service_cost))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Service added successfully"}), 201

@app.route('/add_technician', methods=['POST'])
def add_technician():
    data = request.json
    technician_first_name = data.get("technician_first_name")
    technician_last_name = data.get("technician_last_name")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO technicians (technician_first_name, technician_last_name) VALUES (?, ?)", (technician_first_name, technician_last_name))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Technician added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
