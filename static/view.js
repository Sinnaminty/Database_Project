
function formatDate(isoString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(isoString).toLocaleString(undefined, options);
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

function createTable(headers, data) {
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
    const date = document.getElementById('jobs-date').value;
    const res = await fetch(`/api/jobs_by_day?date=${date}`);
    const data = await res.json();
    document.getElementById('jobs-output').innerHTML = createTable(headers, data);
}

async function fetchServiceCount() {
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
    const id = document.getElementById('serviceSelect').value;
    const start = document.getElementById('service-start').value;
    const end = document.getElementById('service-end').value;
    const res = await fetch(`/api/service_count?service_id=${id}&start=${start}&end=${end}`);
    const data = await res.json();
    document.getElementById('service-count-output').innerHTML = createTable(headers,data);
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
    const id = document.getElementById('tech-id').value;
    const start = document.getElementById('tech-start').value;
    const end = document.getElementById('tech-end').value;
    const res = await fetch(`/api/tech_jobs?tech_id=${id}&start=${start}&end=${end}`);
    const data = await res.json();
    document.getElementById('tech-jobs-output').innerHTML = createTable(data);
}

async function fetchCustomerServices() {
    const id = document.getElementById('cust-id').value;
    const res = await fetch(`/api/customer_services?customer_id=${id}`);
    const data = await res.json();
    document.getElementById('cust-services-output').innerHTML = createTable(data);
}

async function fetchIdleTechs() {
    const res = await fetch('/api/idle_techs');
    const data = await res.json();
    document.getElementById('idle-techs-output').innerHTML = createTable(data);
}

async function fetchTopTech() {
    const start = document.getElementById('top-start').value;
    const end = document.getElementById('top-end').value;
    const res = await fetch(`/api/top_tech?start=${start}&end=${end}`);
    const data = await res.json();
    document.getElementById('top-tech-output').innerHTML = data.name ? `<strong>${data.name}</strong> - $${data.total}` : '<em>No data</em>';
}

async function fetchServicePercentages() {
    const start = document.getElementById('percent-start').value;
    const end = document.getElementById('percent-end').value;
    const res = await fetch(`/api/service_percentages?start=${start}&end=${end}`);
    const data = await res.json();
    const ctx = document.getElementById('percentChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(row => row.name),
            datasets: [{
                label: 'Service Percentages',
                data: data.map(row => row.percent),
                backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6f42c1']
            }]
        }
    });
}