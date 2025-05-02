
function formatDate(isoString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(isoString).toLocaleString(undefined, options);
}
function fetchAll() {
    fetchServices();
    fetchTechnicians();
    fetchCustomers();
}

function fetchServices() {
    fetch('/get_services')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('serviceSelect');
            if (select) {
                select.innerHTML = '<option value="" disabled selected>Select a service</option>';
                data.forEach(service => {
                    const opt = document.createElement('option');
                    opt.value = service.id;
                    opt.textContent = `${service.title}`;
                    select.appendChild(opt);
                });
            }
        });
}

function fetchTechnicians() {
    fetch('/get_technicians')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('technicianSelect');
            if (select) {
                select.innerHTML = '<option value="" disabled selected>Select a technician</option>';
                data.forEach(tech => {
                    const opt = document.createElement('option');
                    opt.value = tech.id;
                    opt.textContent = `${tech.first_name} ${tech.last_name}`;
                    select.appendChild(opt);
                });
            }
        });
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

function createTable(data) {

    const headers = [
        "appointment_datetime",
        "customer_name",
        "technician_name",
        "service_title",
        "make",
        "model",
        "license_plate",
        "cost"
    ];
    if (!data.length) return '<em>No results</em>';
    console.log(headers);
    console.log(data);

    let table = '<table class="table table-bordered table-striped"><thead><tr>';
    headers.forEach(h => {
        const headerText = h.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        table += `<th>${headerText}</th>`;
    });
    table += '</tr></thead><tbody>';

    data.forEach(row => {
        table += '<tr>' + headers.map(h => {
            let val = row[h];
            if (typeof val === 'string' && (h.includes('date') || h.includes('time'))) {
                try {
                    const date = new Date(val);
                    if (!isNaN(date.getTime())) {
                        val = date.toLocaleString(undefined, {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }
                } catch (e) { }
            }
            return `<td>${val !== undefined ? val : ''}</td>`;
        }).join('') + '</tr>';
    });

    return table + '</tbody></table>';
}



async function fetchJobsByDay() {

    const date = document.getElementById('jobs-date').value;
    const res = await fetch(`/api/jobs_by_day?date=${date}`);
    const data = await res.json();
    document.getElementById('jobs-output').innerHTML = createTable(data);
}

async function fetchServiceCount() {
    const id = document.getElementById('serviceSelect').value;
    const start = document.getElementById('service-start').value;
    const end = document.getElementById('service-end').value;
    const res = await fetch(`/api/service_count?service_id=${id}&start=${start}&end=${end}`);
    const data = await res.json();
    document.getElementById('service-count-output').innerHTML = createTable(data);
}

async function fetchTotalCost() {
    const start = document.getElementById('cost-start').value;
    const end = document.getElementById('cost-end').value;
    const res = await fetch(`/api/total_cost?start=${start}&end=${end}`);
    const data = await res.json();
    console.log(data)
    document.getElementById('total-cost-output').innerHTML = `<strong>Total Cost:</strong> $${data[0]}`;
}

async function fetchTechJobs() {
    const id = document.getElementById('technicianSelect').value
    const start = document.getElementById('tech-start').value;
    const end = document.getElementById('tech-end').value;
    const res = await fetch(`/api/tech_jobs?tech_id=${id}&start=${start}&end=${end}`);
    const data = await res.json();
    document.getElementById('tech-jobs-output').innerHTML = createTable(data);
}

async function fetchCustomerServices() {
    const id = document.getElementById('customerSelect').value;
    const res = await fetch(`/api/customer_services?customer_id=${id}`);
    const data = await res.json();
    document.getElementById('cust-services-output').innerHTML = createTable(data);
}

async function fetchIdleTechs() {
    const res = await fetch('/api/idle_techs');
    const data = await res.json();
    document.getElementById('idle-techs-output').innerHTML = `<strong>Idle Techs</strong> ${data[0]}`;
}

async function fetchTopTech() {
    const start = document.getElementById('top-start').value;
    const end = document.getElementById('top-end').value;
    const res = await fetch(`/api/top_tech?start=${start}&end=${end}`);
    const data = await res.json();
    console.log(data);
    document.getElementById('top-tech-output').innerHTML = data[0] ? `<strong>${data[0]}</strong> - $${data[1]}` : '<em>No data</em>';
}
