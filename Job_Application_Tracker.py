import csv
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
CSV_FILE = "job_applications.csv"

# Ensure CSV file exists with headers
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Job Title", "Company", "Location", "Status", "Package", "Experience(Years)", "Qualification"])

# Load applications from CSV file
def load_applications():
    applications = []
    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            applications.append(row)
    return applications

# Save applications to CSV file
def save_applications(applications):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Job Title", "Company", "Location", "Status", "Package", "Experience(Years)", "Qualification"])
        writer.writeheader()
        writer.writerows(applications)

# HTML template with search and sort feature
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Application Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; cursor: pointer; }
        .form-container, .search-container { margin: 20px 0; padding: 15px; background: #f9f9f9; }
        .form-container input, .form-container select, .search-container input { margin: 5px; padding: 5px; }
        button { padding: 5px 10px; margin: 5px; }
    </style>
    <script>
        let sortAscending = true;

        function filterTable() {
            let titleFilter = document.getElementById('searchJobTitle').value.toLowerCase();
            let locationFilter = document.getElementById('searchLocation').value.toLowerCase();
            let qualificationFilter = document.getElementById('searchQualification').value.toLowerCase();
            
            let rows = document.querySelectorAll('.jobRow');
            
            rows.forEach(row => {
                let jobTitle = row.children[0].innerText.toLowerCase();
                let location = row.children[2].innerText.toLowerCase();
                let qualification = row.children[6].innerText.toLowerCase();

                if (jobTitle.includes(titleFilter) && location.includes(locationFilter) && qualification.includes(qualificationFilter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        function sortTableByPackage() {
            let rows = Array.from(document.querySelectorAll('.jobRow'));
            rows.sort((a, b) => {
                let packageA = parseFloat(a.children[4].innerText.replace(/[^0-9.]/g, '')) || 0;
                let packageB = parseFloat(b.children[4].innerText.replace(/[^0-9.]/g, '')) || 0;
                return sortAscending ? packageA - packageB : packageB - packageA;
            });

            let tbody = document.getElementById('jobTableBody');
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));
            sortAscending = !sortAscending;
        }

        function fillForm(jobTitle, company, location, status, package, experience, qualification) {
            document.getElementById('jobTitle').value = jobTitle;
            document.getElementById('company').value = company;
            document.getElementById('location').value = location;
            document.getElementById('status').value = status;
            document.getElementById('package').value = package;
            document.getElementById('experience').value = experience;
            document.getElementById('qualification').value = qualification;
        }

        async function addOrUpdateJob() {
            const job = {
                "Job Title": document.getElementById('jobTitle').value,
                "Company": document.getElementById('company').value,
                "Location": document.getElementById('location').value,
                "Status": document.getElementById('status').value,
                "Package": document.getElementById('package').value,
                "Experience(Years)": document.getElementById('experience').value,
                "Qualification": document.getElementById('qualification').value
            };
            await fetch('/add_update_job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(job)
            });
            location.reload();
        }

        async function deleteJob(jobTitle) {
            await fetch('/delete_job', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ "Job Title": jobTitle })
            });
            location.reload();
        }
    </script>
</head>
<body>
    <h1>Job Application Tracker</h1>
    
    <div class="search-container">
        <h3>Search Jobs</h3>
        <input type="text" id="searchJobTitle" onkeyup="filterTable()" placeholder="Search by Job Title">
        <input type="text" id="searchLocation" onkeyup="filterTable()" placeholder="Search by Location">
        <input type="text" id="searchQualification" onkeyup="filterTable()" placeholder="Search by Qualification">
    </div>

    <button onclick="sortTableByPackage()">Sort by Package</button>

    <div class="form-container">
        <h3>Add/Update Job</h3>
        <input type="text" id="jobTitle" placeholder="Job Title" required>
        <input type="text" id="company" placeholder="Company" required>
        <input type="text" id="location" placeholder="Location" required>
        <input type="text" id="package" placeholder="Package" required>
        <input type="text" id="experience" placeholder="Experience (Years)" required>
        <input type="text" id="qualification" placeholder="Qualification" required>
        <select id="status" required>
            <option value="Applied">Applied</option>
            <option value="Interview">Interview</option>
            <option value="Rejected">Rejected</option>
            <option value="Accepted">Accepted</option>
        </select>
        <button onclick="addOrUpdateJob()">Add/Update Job</button>
    </div>

    <table>
        <tr>
            <th>Job Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Status</th>
            <th onclick="sortTableByPackage()">Package ⬍</th>
            <th>Experience (Years)</th>
            <th>Qualification</th>
            <th>Actions</th>
        </tr>
        <tbody id="jobTableBody">
        {% for job in applications %}
        <tr class="jobRow">
            <td>{{ job['Job Title'] }}</td>
            <td>{{ job['Company'] }}</td>
            <td>{{ job['Location'] }}</td>
            <td>{{ job['Status'] }}</td>
            <td>{{ job['Package'] }}</td>
            <td>{{ job['Experience(Years)'] }}</td>
            <td>{{ job['Qualification'] }}</td>
            <td>
                <button onclick='fillForm("{{ job['Job Title'] }}", "{{ job['Company'] }}", "{{ job['Location'] }}", "{{ job['Status'] }}", "{{ job['Package'] }}", "{{ job['Experience(Years)'] }}", "{{ job['Qualification'] }}")'>Update</button>
                <button onclick='deleteJob("{{ job['Job Title'] }}")'>Delete</button>
            </td>
        </tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


@app.route('/')
def index():
    applications = load_applications()
    return render_template_string(HTML_TEMPLATE, applications=applications)

@app.route('/add_update_job', methods=['POST'])
def add_update_job():
    job = request.json
    applications = load_applications()
    
    job_exists = False
    for i, existing_job in enumerate(applications):
        if existing_job["Job Title"] == job["Job Title"]:
            applications[i] = job
            job_exists = True
            break

    if not job_exists:
        applications.append(job)
    
    save_applications(applications)
    return jsonify({"success": True})

@app.route('/delete_job', methods=['POST'])
def delete_job():
    job_title = request.json["Job Title"]
    applications = [j for j in load_applications() if j["Job Title"] != job_title]
    save_applications(applications)
    return jsonify({"success": True})

if __name__ == "__main__":
    initialize_csv()
    app.run(debug=True, port=5000)
