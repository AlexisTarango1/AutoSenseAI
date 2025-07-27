# Backend logic (Python)

from flask import send_from_directory
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os


app = Flask(__name__)

# Initialize or reset the database
DB_PATH = 'devices.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            category TEXT DEFAULT 'General'  -- <-- NEW FIELD
        )
    ''')
    # readings stays the same...
    ...

    # Readings (timestamped data)
    c.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            temperature REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (device_id) REFERENCES devices(id)
        )
    ''')
    conn.commit()
    conn.close()


# Helper: validate device input
def validate_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"
    return True, ""


@app.route('/devices', methods=['GET'])
def get_devices():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM devices')
    devices = c.fetchall()  # ← define it here
    conn.close()
    return jsonify([
        {
            'id': d[0],
            'name': d[1],
            'type': d[2],
            'location': d[3],
            'status': d[4],
            'category': d[5]
        } for d in devices  # ← use it here
    ])

    return jsonify({'error': 'Device not found'}), 404


@app.route('/devices', methods=['POST'])
def add_device():
    data = request.get_json()
    valid, msg = validate_fields(data, ['name', 'type', 'location', 'status', 'category'])
    if not valid:
        return jsonify({'error': msg}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO devices (name, type, location, status, category) VALUES (?, ?, ?, ?, ?)',
          (data['name'], data['type'], data['location'], data['status'], data['category']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Device added successfully'}), 201


@app.route('/readings', methods=['POST'])
def add_reading():
    data = request.get_json()
    valid, msg = validate_fields(data, ['device_id', 'status', 'temperature'])
    if not valid:
        return jsonify({'error': msg}), 400

    timestamp = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM devices WHERE id=?', (data['device_id'],))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Device ID not found'}), 404

    c.execute('''
        INSERT INTO readings (device_id, status, temperature, timestamp)
        VALUES (?, ?, ?, ?)''',
              (data['device_id'], data['status'], data['temperature'], timestamp))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Reading recorded'})


@app.route('/readings/<int:reading_id>', methods=['PUT'])
def update_reading(reading_id):
    data = request.get_json()
    # Allowed fields to update — adjust as needed
    allowed_fields = ['status', 'temperature']
    update_fields = {key: data[key] for key in allowed_fields if key in data}

    if not update_fields:
        return jsonify({'error': 'No valid fields to update provided'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if reading exists
    c.execute('SELECT * FROM readings WHERE id = ?', (reading_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Reading not found'}), 404

    # Build the SET part dynamically
    set_clause = ", ".join(f"{field} = ?" for field in update_fields.keys())
    values = list(update_fields.values())
    values.append(reading_id)

    c.execute(f'UPDATE readings SET {set_clause} WHERE id = ?', values)
    conn.commit()
    conn.close()

    return jsonify({'message': f'Reading {reading_id} updated successfully'})


@app.route('/readings', methods=['GET'])
def get_all_readings():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM readings ORDER BY timestamp DESC')
    readings = c.fetchall()
    conn.close()
    return jsonify([
        {
            'id': r[0],
            'device_id': r[1],
            'status': r[2],
            'temperature': r[3],
            'timestamp': r[4]
        } for r in readings
    ])


@app.route('/readings/<int:device_id>', methods=['GET'])
def get_readings(device_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM readings WHERE device_id=? ORDER BY timestamp DESC', (device_id,))
    readings = c.fetchall()
    conn.close()
    return jsonify([
        {
            'id': r[0],
            'device_id': r[1],
            'status': r[2],
            'temperature': r[3],
            'timestamp': r[4]
        } for r in readings
    ])

@app.route('/devices/<int:device_id>/details', methods=['GET'])
def get_device_with_readings(device_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch device info
    c.execute('SELECT * FROM devices WHERE id=?', (device_id,))
    device = c.fetchone()

    if not device:
        conn.close()
        return jsonify({'error': 'Device not found'}), 404

    # Fetch readings for the device
    c.execute('SELECT * FROM readings WHERE device_id=? ORDER BY timestamp DESC', (device_id,))
    readings = c.fetchall()
    conn.close()

    return jsonify({
        'device': {
            'device_id': device[0],  # renamed from 'id'
            'name': device[1],
            'type': device[2],
            'status': device[3],
            'location': device[4],
            # Remove Temperature field if you want, or keep if present
        },
        'readings': [
            {
                'reading_id': r[0],  # renamed from 'id'
                'device_id': r[1],
                'status': r[2],
                'temperature': r[3],
                'timestamp': r[4]
            } for r in readings
        ]
    })


@app.route('/devices/<int:device_id>/diagnostics', methods=['GET'])
def run_diagnostics(device_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if device exists
    c.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
    device = c.fetchone()
    if not device:
        conn.close()
        return jsonify({'error': 'Device not found'}), 404

    # Fetch recent readings (latest 5)
    c.execute('''
        SELECT status, temperature, timestamp 
        FROM readings 
        WHERE device_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 5
    ''', (device_id,))
    recent_readings = c.fetchall()
    conn.close()

    # Simple simulated AI logic
    high_temp_count = sum(1 for r in recent_readings if r[1] >= 80.0)
    status_fault_count = sum(1 for r in recent_readings if 'fault' in r[0].lower())

    recommendation = "Device is operating normally."
    if high_temp_count >= 3:
        recommendation = "High temperature detected in multiple readings. Recommend checking HVAC system."
    elif status_fault_count >= 2:
        recommendation = "Frequent fault status reported. Consider inspecting the device."

    return jsonify({
        'device_id': device_id,
        'recent_readings_count': len(recent_readings),
        'high_temperature_flags': high_temp_count,
        'fault_flags': status_fault_count,
        'recommendation': recommendation
    })

@app.route('/ai/diagnose/<int:device_id>', methods=['GET'])
def ai_diagnose(device_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if device exists
    c.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
    device = c.fetchone()
    if not device:
        conn.close()
        return jsonify({'error': 'Device not found'}), 404

    # Fetch latest 10 readings
    c.execute('''
        SELECT status, temperature, timestamp 
        FROM readings 
        WHERE device_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''', (device_id,))
    readings = c.fetchall()
    conn.close()

    if not readings:
        return jsonify({'error': 'No readings found for this device'}), 404

    # Simulated AI logic: check temperature and status patterns
    high_temp_count = sum(1 for r in readings if r[1] >= 80.0)
    fault_count = sum(1 for r in readings if 'fault' in r[0].lower())

    # Basic recommendation logic
    if high_temp_count > 3:
        recommendation = "High temperature detected. Suggest checking cooling system and ventilation."
    elif fault_count > 2:
        recommendation = "Multiple fault statuses detected. Recommend inspecting device hardware."
    else:
        recommendation = "Device is operating normally."

    return jsonify({
        'device_id': device_id,
        'recent_readings_count': len(readings),
        'high_temperature_events': high_temp_count,
        'fault_events': fault_count,
        'recommendation': recommendation
    })




if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5512)
