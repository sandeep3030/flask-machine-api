from flask import Flask, request, jsonify
import mysql.connector
import uuid

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'test'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def get_machine_id():
    return str(uuid.UUID(int=uuid.getnode()))

# Register machine route
@app.route('/register', methods=['POST'])
def register_machine():
    data = request.json
    username = data.get('username')
    machine_id = data.get('machine_id')

    if not username or not machine_id:
        return jsonify({'status': 'error', 'message': 'Missing username or machine_id'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO machines (username, machine_id) VALUES (%s, %s)", (username, machine_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Machine registered successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'status': 'exists', 'message': 'Machine ID already registered'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Check access route
@app.route('/check_access', methods=['POST'])
def check_access():
    data = request.json
    machine_id = data.get('machine_id')

    if not machine_id:
        return jsonify({'status': 'error', 'message': 'Missing machine_id'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM machines WHERE machine_id = %s", (machine_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return jsonify({'status': 'authorized', 'user': result['username']})
        else:
            return jsonify({'status': 'unauthorized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
