# auth.py

import bcrypt
from db import connect_db

# -------------------------
# USER AUTHENTICATION
# -------------------------

def signup(username, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        db.close()
        return False, "User already exists"
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, hashed.decode())  # decode to store as string
    )
    db.commit()
    db.close()
    return True, "User created successfully"

def login(username, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    db.close()
    if user and bcrypt.checkpw(password.encode(), user[1].encode()):
        return True, user[0]  # user[0] = user_id
    return False, "Invalid username or password"



# -------------------------
# PASSWORD STORAGE
# -------------------------

def save_password(user_id, account, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO passwords (user_id, account, password)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE password = VALUES(password)
    """, (user_id, account, password))
    db.commit()
    db.close()

def get_passwords(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT account, password FROM passwords WHERE user_id = %s", (user_id,))
    results = cursor.fetchall()
    db.close()
    return results

def delete_password(user_id, account):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM passwords WHERE user_id = %s AND account = %s", (user_id, account))
    db.commit()
    db.close()
