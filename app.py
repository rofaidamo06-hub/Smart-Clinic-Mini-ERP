from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    
    conn.execute('CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, phone TEXT)')
   
    conn.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, date TEXT, doctor TEXT, FOREIGN KEY(patient_id) REFERENCES patients(id))')
    
    conn.execute('CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY AUTOINCREMENT, appointment_id INTEGER, amount REAL, status TEXT, FOREIGN KEY(appointment_id) REFERENCES appointments(id))')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return redirect(url_for('patients'))



@app.route('/patients', methods=['GET', 'POST'])
def patients():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        conn.execute('INSERT INTO patients (name, age, phone) VALUES (?, ?, ?)', (name, age, phone))
        conn.commit()
    all_patients = conn.execute('SELECT * FROM patients').fetchall()
    conn.close()
    return render_template('patients.html', patients=all_patients)

@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM patients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('patients'))

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone = request.form['phone']
        conn.execute('UPDATE patients SET name = ?, age = ?, phone = ? WHERE id = ?', (name, age, phone, id))
        conn.commit()
        conn.close()
        return redirect(url_for('patients'))
    return render_template('edit_patient.html', patient=patient)



@app.route('/booking', methods=['GET', 'POST'])
def booking():
    conn = get_db_connection()
    if request.method == 'POST':
        p_id = request.form['patient_id']
        app_date = request.form['date']
        doctor = request.form['doctor']
        amount = request.form['amount']
        
       
        cursor = conn.execute('INSERT INTO appointments (patient_id, date, doctor) VALUES (?, ?, ?)', (p_id, app_date, doctor))
        app_id = cursor.lastrowid
        
     
        conn.execute('INSERT INTO bills (appointment_id, amount, status) VALUES (?, ?, ?)', (app_id, amount, 'Unpaid'))
        conn.commit()

    all_patients = conn.execute('SELECT * FROM patients').fetchall()
   
    all_bookings = conn.execute('''
        SELECT b.id, p.name, b.date, b.doctor, bi.amount, bi.status 
        FROM appointments b 
        JOIN patients p ON b.patient_id = p.id 
        JOIN bills bi ON bi.appointment_id = b.id
    ''').fetchall()
    conn.close()
    return render_template('booking.html', patients=all_patients, bookings=all_bookings)

@app.route('/pay_bill/<int:id>')
def pay_bill(id):
    conn = get_db_connection()
    conn.execute('UPDATE bills SET status = ? WHERE id = ?', ('Paid', id))
    conn.commit()
    conn.close()
    return redirect(url_for('booking'))


if __name__ == '__main__':
    init_db() 
    app.run(debug=True)