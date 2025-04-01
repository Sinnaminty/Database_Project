from flask import Blueprint, render_template, jsonify
from models import db, Customer, Vehicle, Appointment, Service, Technician  # Import db from models.py

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/customers')
def get_customers():
    customers = Customer.query.all()
    return jsonify([{"id": c.id, "name": c.name, "phone": c.phone} for c in customers])
