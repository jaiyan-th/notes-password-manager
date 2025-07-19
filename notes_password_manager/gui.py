import tkinter as tk
from tkinter import messagebox, simpledialog
from auth import (
    signup, login, add_note, get_notes, delete_note,
    edit_note_by_id, save_password, get_passwords, delete_password
)

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notes & Password Manager")
        self.user_id = None
        self.show_login()
        self.root.mainloop()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        tk.Label(self.root, text="Login", font=('Arial', 16)).pack(pady=10)

        tk.Label(self.root, text="Username").pack()
        self.login_username = tk.Entry(self.root)
        self.login_username.pack()

        tk.Label(self.root, text="Password").pack()
        self.login_password = tk.Entry(self.root, show='*')
        self.login_password.pack()

        tk.Button(self.root, text="Login", command=self.login_user).pack(pady=5)
        tk.Button(self.root, text="Sign Up", command=self.show_signup).pack()

    def show_signup(self):
        self.clear_window()
        tk.Label(self.root, text="Sign Up", font=('Arial', 16)).pack(pady=10)

        tk.Label(self.root, text="Username").pack()
        self.signup_username = tk.Entry(self.root)
        self.signup_username.pack()

        tk.Label(self.root, text="Password").pack()
        self.signup_password = tk.Entry(self.root, show='*')
        self.signup_password.pack()

        tk.Button(self.root, text="Register", command=self.register_user).pack(pady=5)
        tk.Button(self.root, text="Back to Login", command=self.show_login).pack()

    def login_user(self):
        username = self.login_username.get()
        password = self.login_password.get()
        user_id = login(username, password)
        if user_id:
            self.user_id = user_id
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def register_user(self):
        username = self.signup_username.get()
        password = self.signup_password.get()
        if signup(username, password):
            messagebox.showinfo("Success", "Account created successfully")
            self.show_login()
        else:
            messagebox.showerror("Signup Failed", "Username already exists")

    def show_dashboard(self):
        self.clear_window()
        tk.Label(self.root, text="Dashboard", font=('Arial', 16)).pack(pady=10)

        tk.Button(self.root, text="Notes", width=20, command=self.show_notes).pack(pady=5)
        tk.Button(self.root, text="Passwords", width=20, command=self.show_passwords).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=self.show_login).pack(pady=10)

    def show_notes(self):
        self.clear_window()
        tk.Label(self.root, text="Your Notes", font=('Arial', 16)).pack(pady=10)

        notes = get_notes(self.user_id)
        for note in notes:
            note_id, content = note
            tk.Label(self.root, text=content, wraplength=300).pack()
            tk.Button(self.root, text="Edit", command=lambda nid=note_id: self.edit_note(nid)).pack()
            tk.Button(self.root, text="Delete", command=lambda nid=note_id: self.delete_note(nid)).pack()

        tk.Button(self.root, text="Add Note", command=self.add_note).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_dashboard).pack()

    def add_note(self):
        content = simpledialog.askstring("New Note", "Enter note content:")
        if content:
            add_note(self.user_id, content)
            self.show_notes()

    def edit_note(self, note_id):
        new_content = simpledialog.askstring("Edit Note", "Enter new content:")
        if new_content:
            edit_note_by_id(note_id, new_content)
            self.show_notes()

    def delete_note(self, note_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this note?"):
            delete_note(note_id)
            self.show_notes()

    def show_passwords(self):
        self.clear_window()
        tk.Label(self.root, text="Saved Passwords", font=('Arial', 16)).pack(pady=10)

        passwords = get_passwords(self.user_id)
        for pwd in passwords:
            pwd_id, account, password = pwd
            tk.Label(self.root, text=f"{account}: {password}").pack()
            tk.Button(self.root, text="Delete", command=lambda pid=pwd_id: self.delete_pwd(pid)).pack()

        tk.Button(self.root, text="Add Password", command=self.add_pwd).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_dashboard).pack()

    def add_pwd(self):
        account = simpledialog.askstring("Account", "Enter account name:")
        password = simpledialog.askstring("Password", "Enter password:")
        if account and password:
            save_password(self.user_id, account, password)
            self.show_passwords()

    def delete_pwd(self, pwd_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this password?"):
            delete_password(pwd_id)
            self.show_passwords()
