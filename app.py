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
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT NOT NULL
    )
    """)

    # cars table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        license_plate TEXT NOT NULL
    )
    """)

    # services table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        cost REAL NOT NULL
    )
    """)

    # technicians table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS technicians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    )
    """)

    # appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        appointment_datetime TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (car_id) REFERENCES cars(id)
    )
    """)

    # appointment_services table (many-to-many: services per appointment)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointment_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        technician_id INTEGER NOT NULL,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id),
        FOREIGN KEY (service_id) REFERENCES services(id),
        FOREIGN KEY (technician_id) REFERENCES technicians(id)
    )
    """)

    # customer_cars association table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        car_id INTEGER NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (car_id) REFERENCES cars(id)
    )
    """)
    
    # technician_services association table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS technician_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        technician_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        FOREIGN KEY (technician_id) REFERENCES technicians(id),
        FOREIGN KEY (service_id) REFERENCES services(id)
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
    cursor.execute("SELECT id, first_name, last_name, phone_number FROM customers")
    customers = cursor.fetchall()
    conn.close()

    return jsonify([{'id': customer[0], 'first_name': customer[1], 'last_name': customer[2], 'phone_number': customer[3]} for customer in customers])


@app.route('/add_customer', methods=['POST'])
def add_customer():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    phone_number = data.get("phone_number")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (first_name, last_name, phone_number) VALUES (?, ?, ?)", (first_name, last_name, phone_number))
    conn.commit()
    conn.close()

    return jsonify({"message": "Customer added successfully"}), 201    

@app.route('/get_cars', methods=['GET'])
def get_cars():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, make, model, license_plate FROM cars")
    cars = cursor.fetchall()
    conn.close()

    return jsonify([{'id': car[0], 'make': car[1], 'model': car[2], 'license_plate': car[3]} for car in cars])
    

@app.route('/add_car', methods=['POST'])
def add_car():
    data = request.json
    make = data.get("make")
    model = data.get("model")
    license_plate = data.get("license_plate")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cars (make, model, license_plate) VALUES (?, ?, ?)",
                   (make, model, license_plate))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Car added successfully"}), 201


@app.route('/get_services', methods=['GET'])
def get_services():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, cost FROM services")
    services = cursor.fetchall()
    conn.close()

    return jsonify([{'id': service[0], 'title': service[1], 'cost': service[2]} for service in services])


@app.route('/add_service', methods=['POST'])
def add_service():
    data = request.json
    title = data.get("title")
    cost = data.get("cost")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services (title, cost) VALUES (?, ?)", (title, cost))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Service added successfully"}), 201



@app.route('/get_technicians', methods=['GET'])
def get_technicians():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name FROM technicians")
    technicians = cursor.fetchall()
    conn.close()

    return jsonify([{'id': tech[0], 'first_name': tech[1], 'last_name': tech[2]} for tech in technicians])

@app.route('/add_technician', methods=['POST'])
def add_technician():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO technicians (first_name, last_name) VALUES (?, ?)", (first_name, last_name))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Technician added successfully"}), 201



@app.route('/associate_customer_car', methods=['POST'])
def associate_customer_car():
    data = request.json
    customer_id = data.get("customer_id")
    car_id = data.get("car_id")

    if not customer_id or not car_id:
        return jsonify({"error": "Missing customer_id or car_id"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT first_name, last_name FROM customers WHERE id = ?", (customer_id,))
    customer = cursor.fetchone()

    cursor.execute("SELECT make, model FROM cars WHERE id = ?", (car_id,))
    car = cursor.fetchone()

    # Insert association
    cursor.execute("INSERT INTO customer_cars (customer_id, car_id) VALUES (?, ?)", (customer_id, car_id))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Car {car[0]} {car[1]} associated with customer {customer[0]} {customer[1]} successfully"}), 201



@app.route('/associate_technician_service', methods=['POST'])
def associate_technician_service():
    data = request.json
    technician_id = data.get("technician_id")
    service_id = data.get("service_id")

    if not technician_id or not service_id:
        return jsonify({"error": "Missing technician_id or service_id"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT first_name, last_name FROM technicians WHERE id = ?", (technician_id,))
    technician = cursor.fetchone()

    cursor.execute("SELECT title FROM services WHERE id = ?", (service_id,))
    service = cursor.fetchone()

    # Insert association
    cursor.execute("INSERT INTO technician_services (technician_id, service_id) VALUES (?, ?)", (technician_id, service_id))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Technician {technician[0]} {technician[1]} associated with service {service[0]} successfully"}), 201


@app.route('/schedule_appointment', methods=['POST'])
def schedule_appointment():
    data = request.json
    appointment_datetime = data.get("appointment_datetime")
    customer_id = data.get("customer_id")
    car_id = data.get("car_id")
    services = data.get("services", [])

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Insert appointment
    cursor.execute("INSERT INTO appointments (customer_id, car_id, appointment_datetime) VALUES (?, ?, ?)",
                   (customer_id, car_id, appointment_datetime))
    appointment_id = cursor.lastrowid

    # Insert services + technicians
    for svc in services:
        cursor.execute("INSERT INTO appointment_services (appointment_id, service_id, technician_id) VALUES (?, ?, ?)",
                       (appointment_id, svc["service_id"], svc["technician_id"]))

    conn.commit()
    conn.close()

    return jsonify({"message": "Appointment scheduled successfully"}), 201


@app.route('/get_customer_cars')
def get_customer_cars():
    customer_id = request.args.get("customer_id")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT car_id FROM customer_cars WHERE customer_id = ?", (customer_id,))
    cars = cursor.fetchall()
    conn.close()
    return jsonify([{"car_id": car[0]} for car in cars])



if __name__ == '__main__':
    app.run(debug=True)
