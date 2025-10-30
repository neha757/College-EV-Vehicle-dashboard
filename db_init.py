import sqlite3
from werkzeug.security import generate_password_hash

def init_database():
    conn = sqlite3.connect('ev_requisition.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            department TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            purpose TEXT NOT NULL,
            date TEXT NOT NULL,
            from_location TEXT NOT NULL,
            to_location TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    admin_password = generate_password_hash('admin123')
    student_password = generate_password_hash('student123')
    
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password, role, name, department) VALUES (?, ?, ?, ?, ?)',
        ('admin', admin_password, 'admin', 'Administrator', 'Administration')
    )
    
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password, role, name, department) VALUES (?, ?, ?, ?, ?)',
        ('student', student_password, 'student', 'John Doe', 'Computer Science')
    )
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")
    print("Default Admin - Username: admin, Password: admin123")
    print("Default Student - Username: student, Password: student123")

if __name__ == '__main__':
    init_database()
