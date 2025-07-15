from flask import Flask, jsonify, send_from_directory, render_template_string
import os
import json

app = Flask(__name__)
JSON_FILE = "detections.json"
IMAGES_FOLDER = "images"

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def get_data():
    if not os.path.exists(JSON_FILE):
        return jsonify([])
    with open(JSON_FILE, "r") as f:
        try:
            return jsonify(json.load(f))
        except json.JSONDecodeError:
            return jsonify([])

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Fire/Smoke Detection</title>
    <style>
        table {
            border-collapse: collapse;
            width: 95%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f04;
            color: white;
        }
        img {
            max-width: 300px;
        }
    </style>
</head>
<body>
    <h1>Fire/Smoke Detection Table</h1>
    <table id="detection-table">
        <thead>
            <tr>
                <th>Status</th>
                <th>Timestamp</th>
                <th>Thumbnail</th>
            </tr>
        </thead>
        <tbody id="table-body">
            <tr><td colspan="3">Loading...</td></tr>
        </tbody>
    </table>

    <script>
        function updateTable() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('table-body');
                    tbody.innerHTML = '';
                    if (data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="3">No data</td></tr>';
                        return;
                    }
                    for (let item of data) {
                        const row = document.createElement('tr');
                        const status = item.status || 'Unknown';
                        const timestamp = item.timestamp || 'N/A';
                        const thumb = item.thumbnail ? 
                            `<img src="${item.thumbnail}">` : 'No Image';

                        row.innerHTML = `<td>${status}</td><td>${timestamp}</td><td>${thumb}</td>`;
                        tbody.appendChild(row);
                    }
                });
        }

        updateTable(); // initial load
        setInterval(updateTable, 5000); // refresh every 5 seconds
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
