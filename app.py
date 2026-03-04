from flask import Flask, render_template, jsonify, request
import csv
import os

app = Flask(__name__)

def find_plot_in_csv(plot_id):
    # Get absolute path to the CSV in the current folder
    csv_path = os.path.join(os.path.dirname(__file__), 'plots.csv')
    try:
        if not os.path.exists(csv_path):
            return None
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Strip spaces to ensure a match even with messy CSV data
                if str(row['plot_id']).strip() == str(plot_id).strip():
                    return row
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_plot_details')
def get_plot_details():
    plot_id = request.args.get('id')
    details = find_plot_in_csv(plot_id)
    if details:
        return jsonify(details)
    return jsonify({"error": "Plot not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)