from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from datetime import datetime

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

def query_db(query, args=(), one=False):
    with sqlite3.connect(DB_FILE) as con:
        cur = con.execute(query, args)
        rv = cur.fetchall()

    return (rv[0] if rv else None) if one else rv

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


@app.route('/get_service_technicians', methods=['GET'])
def get_service_technicians():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id AS service_id, s.title AS service_title,
               t.id AS technician_id, t.first_name, t.last_name
        FROM technician_services ts
        JOIN technicians t ON ts.technician_id = t.id
        JOIN services s ON ts.service_id = s.id
    """)
    rows = cursor.fetchall()
    conn.close()

    # Organize data by service
    service_map = {}
    for service_id, service_title, tech_id, tech_first, tech_last in rows:
        if service_id not in service_map:
            service_map[service_id] = {
                "title": service_title,
                "technicians": []
            }
        service_map[service_id]["technicians"].append({
            "id": tech_id,
            "name": f"{tech_first} {tech_last}"
        })

    return jsonify(service_map)


# VIEW #

@app.route('/view')
def view():
    return render_template('view.html')

@app.route('/api/jobs_by_day')
def jobs_by_day():
    date = request.args.get('date')
    query = '''
        SELECT a.appointment_datetime, 
            cust.first_name || ' ' || cust.last_name AS customer_name,
            tech.first_name || ' ' || tech.last_name AS technician_name,
            s.title AS service_title, 
            c.make, c.model, c.license_plate, s.cost
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN cars c ON a.car_id = c.id
        JOIN customers cust ON a.customer_id = cust.id
        JOIN services s ON aps.service_id = s.id
        JOIN technicians tech ON aps.technician_id = tech.id
        WHERE DATE(a.appointment_datetime) = ?
        ORDER BY a.appointment_datetime, c.id
    '''

    result = query_db(query, [date])
    return jsonify([{"appointment_datetime": r[0],
                     "customer_name" : r[1],
                     "technician_name" : r[2],
                     "service_title" : r[3],
                     "make" : r[4],
                     "model" : r[5],
                     "license_plate" : r[6],
                     "cost" : r[7]}
                    for r in result])

@app.route('/api/service_count')
def service_count():
    service_id = request.args.get('service_id')
    start = request.args.get('start')
    end = request.args.get('end')

    query = '''
        SELECT a.appointment_datetime,
            cust.first_name || ' ' || cust.last_name AS customer_name,
            tech.first_name || ' ' || tech.last_name AS technician_name,
            s.title AS service_title, 
            c.make, c.model, c.license_plate, s.cost
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN cars c ON a.car_id = c.id
        JOIN customers cust ON a.customer_id = cust.id
        JOIN services s ON aps.service_id = s.id
        JOIN technicians tech ON aps.technician_id = tech.id
        WHERE aps.service_id = ? AND a.appointment_datetime BETWEEN ? AND ?
        GROUP BY a.appointment_datetime
        ORDER BY a.appointment_datetime
    '''
    result = query_db(query, [service_id, start, end])
    return jsonify([{"appointment_datetime": r[0],
                     "customer_name" : r[1],
                     "technician_name" : r[2],
                     "service_title" : r[3],
                     "make" : r[4],
                     "model" : r[5],
                     "license_plate" : r[6],
                     "cost" : r[7]}
                    for r in result])

@app.route('/api/total_cost')
def total_cost():
    start = request.args.get('start')
    end = request.args.get('end')
    query = '''
        SELECT SUM(s.cost) AS total_cost
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN services s ON aps.service_id = s.id
        WHERE DATE(a.appointment_datetime) BETWEEN ? AND ?
    '''
    return jsonify(query_db(query, [start, end] ))

@app.route('/api/tech_jobs')
def tech_jobs():
    tech_id = request.args.get('tech_id')
    start = request.args.get('start')
    end = request.args.get('end')
    query = '''
        SELECT a.appointment_datetime,
            cust.first_name || ' ' || cust.last_name AS customer_name,
            tech.first_name || ' ' || tech.last_name AS technician_name,
            s.title AS service_title, 
            c.make, c.model, c.license_plate, s.cost
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN cars c ON a.car_id = c.id
        JOIN customers cust ON a.customer_id = cust.id
        JOIN services s ON aps.service_id = s.id
        JOIN technicians tech ON aps.technician_id = tech.id
        WHERE aps.technician_id = ? AND DATE(a.appointment_datetime) BETWEEN ? AND ?
        GROUP BY a.appointment_datetime
        ORDER BY a.appointment_datetime, c.id
    '''

    result = query_db(query, [tech_id, start, end])
    return jsonify([{"appointment_datetime": r[0],
                     "customer_name" : r[1],
                     "technician_name" : r[2],
                     "service_title" : r[3],
                     "make" : r[4],
                     "model" : r[5],
                     "license_plate" : r[6],
                     "cost" : r[7]}
                    for r in result])

@app.route('/api/customer_services')
def customer_services():
    customer_id = request.args.get('customer_id')
    query = '''
        SELECT a.appointment_datetime,
            cust.first_name || ' ' || cust.last_name AS customer_name,
            tech.first_name || ' ' || tech.last_name AS technician_name,
            s.title AS service_title, 
            c.make, c.model, c.license_plate, s.cost
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN cars c ON a.car_id = c.id
        JOIN customers cust ON a.customer_id = cust.id
        JOIN services s ON aps.service_id = s.id
        JOIN technicians tech ON aps.technician_id = tech.id
        WHERE c.id IN (SELECT car_id FROM customer_cars WHERE customer_id = ?)
        GROUP BY a.appointment_datetime
        ORDER BY a.appointment_datetime, c.id
    '''
    result = query_db(query, [customer_id])
    return jsonify([{"appointment_datetime": r[0],
                     "customer_name" : r[1],
                     "technician_name" : r[2],
                     "service_title" : r[3],
                     "make" : r[4],
                     "model" : r[5],
                     "license_plate" : r[6],
                     "cost" : r[7]}
                    for r in result])
    

@app.route('/api/idle_techs')
def idle_techs():
    query = '''
        SELECT first_name || ' ' || last_name AS name FROM technicians
        WHERE id NOT IN (
            SELECT DISTINCT technician_id FROM appointment_services
            WHERE technician_id IS NOT NULL
        )
    '''
    return jsonify(query_db(query))

@app.route('/api/top_tech')
def top_tech():
    start = request.args.get('start')
    end = request.args.get('end')
    query = '''
        SELECT tech.first_name || ' ' || tech.last_name AS name, SUM(s.cost) AS total
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN technicians tech ON aps.technician_id = tech.id
        JOIN services s ON aps.service_id = s.id
        WHERE DATE(a.appointment_datetime) BETWEEN ? AND ?
        GROUP BY tech.id
        ORDER BY total DESC
        LIMIT 1
    '''
    result = query_db(query, [start, end], one=True)
    return jsonify(result if result else {})

@app.route('/api/service_percentages')
def service_percentages():
    start = request.args.get('start')
    end = request.args.get('end')
    total_query = '''
        SELECT COUNT(*) AS total
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        WHERE DATE(a.appointment_datetime) BETWEEN ? AND ?
    '''
    total_result = query_db(total_query, [start, end], one=True)
    total = total_result[0] if total_result else 1

    query = '''
        SELECT s.title AS name, COUNT(*) * 100.0 / ? AS percent
        FROM appointment_services aps
        JOIN appointments a ON aps.appointment_id = a.id
        JOIN services s ON aps.service_id = s.id
        WHERE DATE(a.appointment_datetime) BETWEEN ? AND ?
        GROUP BY s.title
        ORDER BY percent DESC
    '''
    return jsonify(query_db(query, [total, start, end]))


if __name__ == '__main__':
    app.run(debug=True)
