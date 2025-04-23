document.addEventListener('DOMContentLoaded', function () {
    function updateResponseBox(message) {
        const box = document.getElementById("responseBox");
        if (box) box.innerText = message;
    }

    function fetchCustomers() {
        fetch('/get_customers')
            .then(res => res.json())
            .then(data => {
                const selects = [document.getElementById('customerSelect'), document.getElementById('appointmentCustomerSelect')];
                selects.forEach(select => {
                    if (!select) return;
                    select.innerHTML = '<option value="" disabled selected>Select a customer</option>';
                    data.forEach(c => {
                        const opt = document.createElement('option');
                        opt.value = c.id;
                        opt.textContent = `${c.first_name} ${c.last_name}`;
                        select.appendChild(opt);
                    });
                });
            });
    }

    function fetchCars() {
        fetch('/get_cars')
            .then(res => res.json())
            .then(data => {
                const select = document.getElementById('carSelect');
                if (select) {
                    select.innerHTML = '<option value="" disabled selected>Select a car</option>';
                    data.forEach(car => {
                        const opt = document.createElement('option');
                        opt.value = car.id;
                        opt.textContent = `${car.make} ${car.model}`;
                        select.appendChild(opt);
                    });
                }
            });
    }

    function fetchCarsForCustomer(customerId) {
        fetch(`/get_customer_cars?customer_id=${customerId}`)
            .then(res => res.json())
            .then(customerCars => {
                fetch('/get_cars')
                    .then(res => res.json())
                    .then(allCars => {
                        const select = document.getElementById('appointmentCarSelect');
                        select.innerHTML = '<option value="" disabled selected>Select a car</option>';
                        allCars.forEach(car => {
                            if (customerCars.some(cc => cc.car_id === car.id)) {
                                const opt = document.createElement('option');
                                opt.value = car.id;
                                opt.textContent = `${car.make} ${car.model} (${car.license_plate})`;
                                select.appendChild(opt);
                            }
                        });
                    });
            });
    }

    function fetchServiceAndTechniciansAssociations() {
        fetch('/get_service_technicians')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('servicesTechniciansContainer');
                container.innerHTML = '';
                Object.entries(data).forEach(([serviceId, { title, technicians }]) => {
                    const div = document.createElement('div');
                    div.innerHTML = `
                        <input type="checkbox" class="serviceCheckbox" value="${serviceId}"> ${title}
                        <select class="technicianSelect">
                            <option value="" disabled selected>Select technician</option>
                            ${technicians.map(t => `<option value="${t.id}">${t.name}</option>`).join('')}
                        </select><br>`;
                    container.appendChild(div);
                });
            });
    }

    function fetchAll() {
        fetchCustomers();
        fetchCars();
        fetchServiceAndTechniciansAssociations();
    }

    document.getElementById('appointmentCustomerSelect')?.addEventListener('change', e => {
        fetchCarsForCustomer(e.target.value);
    });

    // Reusable function for form submissions
    function submitForm(formId, endpoint, getPayload, onSuccess) {
        document.getElementById(formId).addEventListener('submit', function (e) {
            e.preventDefault();
            const payload = getPayload();
            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
                .then(res => res.json())
                .then(data => {
                    updateResponseBox(data.message || data.error);
                    if (onSuccess) onSuccess();
                });
        });
    }

    submitForm('addCustomerForm', '/add_customer', () => ({
        first_name: document.getElementById('customerFirstName').value,
        last_name: document.getElementById('customerLastName').value,
        phone_number: document.getElementById('customerPhoneNumber').value
    }), fetchCustomers);

    submitForm('addCarForm', '/add_car', () => ({
        make: document.getElementById('carMake').value,
        model: document.getElementById('carModel').value,
        license_plate: document.getElementById('carLicensePlate').value
    }), fetchCars);

    submitForm('addServiceForm', '/add_service', () => ({
        title: document.getElementById('serviceTitle').value,
        cost: document.getElementById('serviceCost').value
    }), fetchServiceAndTechniciansAssociations);

    submitForm('addTechnicianForm', '/add_technician', () => ({
        first_name: document.getElementById('technicianFirstName').value,
        last_name: document.getElementById('technicianLastName').value
    }), fetchServiceAndTechniciansAssociations);

    submitForm('associateCustomerCarForm', '/associate_customer_car', () => ({
        customer_id: document.getElementById('customerSelect').value,
        car_id: document.getElementById('carSelect').value
    }));

    submitForm('associateTechnicianServiceForm', '/associate_technician_service', () => ({
        technician_id: document.getElementById('technicianSelect').value,
        service_id: document.getElementById('serviceSelect').value
    }), fetchServiceAndTechniciansAssociations);

    submitForm('scheduleAppointmentForm', '/schedule_appointment', () => {
        const services = Array.from(document.querySelectorAll('.serviceCheckbox:checked')).map(cb => {
            const techSelect = cb.nextElementSibling;
            return {
                service_id: cb.value,
                technician_id: techSelect.value
            };
        });

        return {
            appointment_datetime: document.getElementById('appointmentDatetime').value,
            customer_id: document.getElementById('appointmentCustomerSelect').value,
            car_id: document.getElementById('appointmentCarSelect').value,
            services
        };
    });

    fetchAll();
});
