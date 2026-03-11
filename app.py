from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import csv
import os

app = Flask(__name__)
# Change this secret key to something unique for your deployment
app.secret_key = "techunited_plot_locator_secure_2026"

# --- CONFIGURATION ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

CITIES_CONFIG = {
    "Khandwa": ["muffadal_park", "smart_city"],
    "Shujalpur": ["green_valley", "royal_residency"]
}

# --- ROUTES ---

@app.route('/')
def index():
    is_admin = session.get('is_admin', False)
    return render_template('index.html', cities=CITIES_CONFIG.keys(), is_admin=is_admin)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/get_projects')
def get_projects():
    city = request.args.get('city')
    return jsonify(CITIES_CONFIG.get(city, []))

@app.route('/get_all_plots')
def get_all_plots():
    city = request.args.get('city')
    project = request.args.get('project')
    csv_path = os.path.join('data', city, f"{project}.csv")
    
    plots = []
    if os.path.exists(csv_path):
        try:
            with open(csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # SAFETY: Strip spaces and ignore None values to prevent crashes
                    clean_row = {str(k).strip(): str(v).strip() for k, v in row.items() if k and v}
                    if 'coords' in clean_row:
                        clean_row['coords'] = clean_row['coords'].replace('"', '')
                    plots.append(clean_row)
            return jsonify(plots)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "CSV not found"}), 404

@app.route('/save_plot_details', methods=['POST'])
def save_plot_details():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    csv_path = os.path.join('data', data['city'], f"{data['project']}.csv")
    updated_rows = []
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if str(row['plot_id']).strip() == str(data['plot_id']).strip():
                    row.update({
                        'status': data['status'],
                        'owner': data['owner'],
                        'size': data['size'],
                        'customer_number': data['customer_number'],
                        'booking_date': data['booking_date'],
                        'registry_date': data['registry_date']
                    })
                updated_rows.append(row)

        with open(csv_path, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)