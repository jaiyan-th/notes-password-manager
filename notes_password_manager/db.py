# db.py

import mysql.connector
import bcrypt

def connect_db(use_database=True):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jaiyanth@123"
    )
    if use_database:
        connection.database = "notes_manager"
    return connection

def init_db():
    # Create database if not exists
    db = connect_db(use_database=False)
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS notes_manager")
    db.commit()
    db.close()

    # Connect to notes_manager DB
    db = connect_db()
    cursor = db.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    # Create notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create passwords table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            account VARCHAR(255),
            password TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()

def get_user_by_username(username):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    db.close()
    return user

def create_user(username, password):
    db = connect_db()
    cursor = db.cursor()

    # Hash the password before storing
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        db.commit()
        return True
    except mysql.connector.Error as e:
        print("Error:", e)
        return False
    finally:
        db.close()

def add_note(user_id, content):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO notes (user_id, content) VALUES (%s, %s)",
        (user_id, content)
    )
    db.commit()
    db.close()

def get_notes_by_user(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, content FROM notes WHERE user_id=%s ORDER BY id ASC",
        (user_id,)
    )
    notes = cursor.fetchall()
    db.close()
    return notes

def add_password(user_id, account, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO passwords (user_id, account, password) VALUES (%s, %s, %s)",
        (user_id, account, password)
    )
    db.commit()
    db.close()

def get_passwords_by_user(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, account, password FROM passwords WHERE user_id=%s",
        (user_id,)
    )
    passwords = cursor.fetchall()
    db.close()
    return passwords
