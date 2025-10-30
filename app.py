import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def get_db_connection():
    conn = sqlite3.connect('ev_requisition.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['name'] = user['name']
            session['department'] = user['department']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') == 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    requisitions = conn.execute(
        'SELECT * FROM requisitions WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('student_dashboard.html', requisitions=requisitions)

@app.route('/student/submit', methods=['POST'])
def submit_requisition():
    if 'user_id' not in session or session.get('role') == 'admin':
        return redirect(url_for('login'))
    
    name = request.form['name']
    department = request.form['department']
    purpose = request.form['purpose']
    date = request.form['date']
    from_location = request.form['from_location']
    to_location = request.form['to_location']
    vehicle_type = request.form['vehicle_type']
    
    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO requisitions (user_id, name, department, purpose, date, 
           from_location, to_location, vehicle_type) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (session['user_id'], name, department, purpose, date, 
         from_location, to_location, vehicle_type)
    )
    conn.commit()
    conn.close()
    
    flash('Requisition submitted successfully!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    requisitions = conn.execute(
        '''SELECT r.*, u.username 
           FROM requisitions r 
           JOIN users u ON r.user_id = u.id 
           ORDER BY r.created_at DESC'''
    ).fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', requisitions=requisitions)

@app.route('/admin/update_status/<int:req_id>/<status>')
def update_status(req_id, status):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if status not in ['Approved', 'Rejected']:
        flash('Invalid status', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    conn.execute('UPDATE requisitions SET status = ? WHERE id = ?', (status, req_id))
    conn.commit()
    conn.close()
    
    flash(f'Requisition {status.lower()} successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
