from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import csv
import os

app = Flask(__name__)
# Secure secret key for session management
app.secret_key = "techunited_secure_key_2026"

# --- CONFIGURATION ---
# Admin Credentials (Update these for your security)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# Folder names in /data and /static/ must match these keys exactly
CITIES_CONFIG = {
    "Khandwa": ["muffadal_park", "smart_city"],
    "Shujalpur": ["green_valley", "royal_residency"]
}

# --- ROUTES ---

@app.route('/')
def index():
    # Pass the admin status to the HTML template
    is_admin = session.get('is_admin', False)
    return render_template('index.html', cities=CITIES_CONFIG.keys(), is_admin=is_admin)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == ADMIN_USERNAME and data.get('password') == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid Credentials"})

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
    try:
        if os.path.exists(csv_path):
            with open(csv_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # FIX: Handle NoneType objects and empty cells to prevent .strip() errors
                    clean_row = {
                        str(k).strip(): str(v).strip() 
                        for k, v in row.items() 
                        if k is not None and v is not None
                    }
                    
                    # Ensure coordinates are clean (no double quotes) for SVG rendering
                    if 'coords' in clean_row:
                        clean_row['coords'] = clean_row['coords'].replace('"', '')
                    
                    plots.append(clean_row)
            return jsonify(plots)
        return jsonify({"error": "CSV file not found"}), 404
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/save_plot_details', methods=['POST'])
def save_plot_details():
    # SECURITY: Only allow logged-in admins to save data
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.json
    city = data.get('city')
    project = data.get('project')
    plot_id = str(data.get('plot_id')).strip()
    
    csv_path = os.path.join('data', city, f"{project}.csv")
    updated_rows = []
    
    try:
        # Read the existing file
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for row in reader:
                if str(row['plot_id']).strip() == plot_id:
                    # Update row data from the request
                    row['status'] = data.get('status')
                    row['owner'] = data.get('owner')
                    row['size'] = data.get('size')
                    row['customer_number'] = data.get('customer_number')
                    row['booking_date'] = data.get('booking_date')  # NEWLY ADDED
                    row['registry_date'] = data.get('registry_date')
                updated_rows.append(row)

        # Write back to the CSV
        with open(csv_path, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)