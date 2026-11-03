from flask import Flask, render_template, request, jsonify
import mysql.connector
from ml_predictor import wait_time_model  # <--- Imported from your ml_predictor.py file

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Chayan@18042004',  # Add your MySQL password if you have one
    'database': 'smart_healthcare_queue'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Departments")
    departments = cursor.fetchall()
    cursor.execute("SELECT * FROM Patients")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('adbms_dashboard.html', departments=departments, patients=patients)

@app.route('/check-in', methods=['POST'])
def check_in():
    patient_id = request.form.get('patient_id')
    department_id = request.form.get('department_id')
    priority_score = int(request.form.get('priority_score'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Call stored procedure
        args = cursor.callproc('sp_check_in_patient', [patient_id, department_id, priority_score, 0, 0, 0])
        
        appointment_id = args[3]
        assigned_doctor_id = args[4]
        queue_position = args[5]
        
        # 2. Get active doctor load for ML features
        cursor.execute("SELECT COUNT(*) FROM Appointments WHERE doctor_id = %s AND status IN ('Waiting', 'In Progress')", (assigned_doctor_id,))
        doctor_load = cursor.fetchone()[0]
        
        # 3. Predict wait time using Scikit-Learn
        estimated_wait = wait_time_model.predict_wait_time(queue_position, priority_score, doctor_load)
        
        # 4. Save estimated wait time back to database
        cursor.execute("UPDATE Appointments SET estimated_wait_minutes = %s WHERE appointment_id = %s", (estimated_wait, appointment_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "Patient checked in and AI wait-time predicted successfully!",
            "appointment_id": appointment_id,
            "assigned_doctor_id": assigned_doctor_id,
            "queue_position": queue_position,
            "estimated_wait_minutes": estimated_wait
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)