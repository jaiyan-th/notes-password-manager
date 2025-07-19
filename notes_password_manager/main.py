# main.py
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext, ttk
import db
import auth
from db import init_db
import time

class App:
    def __init__(self, root, user_id, username):
        self.user_id = user_id
        self.username = username
        self.root = root
        self.root.title(f"🔐 Notes & Password Manager - {username}")
        self.root.geometry("800x600")
        self.root.configure(bg='#2C3E50')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Title with animation effect
        self.title_frame = tk.Frame(root, bg='#34495E', height=80)
        self.title_frame.pack(fill='x', pady=(0, 10))
        self.title_frame.pack_propagate(False)
        
        self.title_label = tk.Label(self.title_frame, 
                                   text=f"Welcome, {username}!", 
                                   font=('Arial', 20, 'bold'),
                                   fg='#ECF0F1', bg='#34495E')
        self.title_label.pack(expand=True)
        
        # Animate title
        self.animate_title()

        # Text area with styling
        text_frame = tk.Frame(root, bg='#2C3E50')
        text_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, 
                                                  width=80, height=20,
                                                  bg='#ECF0F1', fg='#2C3E50',
                                                  font=('Consolas', 11),
                                                  insertbackground='#3498DB',
                                                  selectbackground='#3498DB',
                                                  selectforeground='white')
        self.text_area.pack(fill='both', expand=True)

        # Buttons with colors and hover effects
        button_frame = tk.Frame(root, bg='#2C3E50')
        button_frame.pack(pady=15)

        # Button configurations
        buttons = [
            ("📝 Add Note", self.add_note, '#E74C3C', '#C0392B'),
            ("👁️ View Notes", self.view_notes, '#3498DB', '#2980B9'),
            ("🔑 Save Password", self.save_password, '#27AE60', '#229954'),
            ("🔓 Retrieve Passwords", self.retrieve_passwords, '#F39C12', '#E67E22')
        ]
        
        self.buttons = []
        for i, (text, command, color, hover_color) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, command=command,
                           bg=color, fg='white', font=('Arial', 10, 'bold'),
                           relief='flat', padx=20, pady=10,
                           cursor='hand2')
            btn.grid(row=0, column=i, padx=8)
            
            # Add hover effects
            self.add_hover_effect(btn, color, hover_color)
            self.buttons.append(btn)

    def add_hover_effect(self, button, normal_color, hover_color):
        def on_enter(e):
            button.config(bg=hover_color)
        def on_leave(e):
            button.config(bg=normal_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def animate_title(self):
        colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6']
        self.color_index = 0
        
        def change_color():
            self.title_label.config(fg=colors[self.color_index])
            self.color_index = (self.color_index + 1) % len(colors)
            self.root.after(1500, change_color)
        
        change_color()

    def animate_text_display(self, text):
        self.text_area.delete("1.0", tk.END)
        
        def type_text(index=0):
            if index < len(text):
                self.text_area.insert(tk.END, text[index])
                self.text_area.see(tk.END)
                self.root.after(30, lambda: type_text(index + 1))
        
        type_text()

    def add_note(self):
        note = simpledialog.askstring("Add Note", "Enter your note:")
        if note:
            db.add_note(self.user_id, note)
            messagebox.showinfo("Success", "Note saved.")

    def view_notes(self):
        notes = db.get_notes_by_user(self.user_id)
        display_text = "🗒️ === YOUR NOTES ===\n\n"
        if notes:
            for i, (_, content) in enumerate(notes, 1):
                display_text += f"📝 {i}. {content}\n"
        else:
            display_text += "📭 No notes found.\n"
        
        self.animate_text_display(display_text)

    def save_password(self):
        account = simpledialog.askstring("Save Password", "Enter account name:")
        password = simpledialog.askstring("Save Password", f"Enter password for {account}:")
        if account and password:
            db.add_password(self.user_id, account, password)
            messagebox.showinfo("Success", "Password saved.")

    def retrieve_passwords(self):
        passwords = db.get_passwords_by_user(self.user_id)
        display_text = "🔐 === STORED PASSWORDS ===\n\n"
        if passwords:
            for account_id, account, password in passwords:
                display_text += f"🔑 {account}: {password}\n"
        else:
            display_text += "🔒 No passwords found.\n"
        
        self.animate_text_display(display_text)


class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Secure Login")
        self.root.geometry("400x300")
        self.root.configure(bg='#2C3E50')
        
        # Title
        title_label = tk.Label(root, text="🔒 Welcome", 
                              font=('Arial', 24, 'bold'),
                              fg='#ECF0F1', bg='#2C3E50')
        title_label.pack(pady=20)
        
        # Create frame for form
        form_frame = tk.Frame(root, bg='#34495E', padx=30, pady=20)
        form_frame.pack(pady=20)
        
        # Username
        tk.Label(form_frame, text="👤 Username", 
                font=('Arial', 12, 'bold'),
                fg='#ECF0F1', bg='#34495E').pack(pady=5)
        self.username_entry = tk.Entry(form_frame, font=('Arial', 11),
                                     bg='#ECF0F1', fg='#2C3E50',
                                     insertbackground='#3498DB')
        self.username_entry.pack(pady=5, ipady=5)

        # Password
        tk.Label(form_frame, text="🔑 Password", 
                font=('Arial', 12, 'bold'),
                fg='#ECF0F1', bg='#34495E').pack(pady=5)
        self.password_entry = tk.Entry(form_frame, show="*", font=('Arial', 11),
                                     bg='#ECF0F1', fg='#2C3E50',
                                     insertbackground='#3498DB')
        self.password_entry.pack(pady=5, ipady=5)
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='#34495E')
        button_frame.pack(pady=15)
        
        login_btn = tk.Button(button_frame, text="🚀 Login", command=self.login,
                             bg='#3498DB', fg='white', font=('Arial', 11, 'bold'),
                             relief='flat', padx=20, pady=8, cursor='hand2')
        login_btn.pack(side='left', padx=5)
        
        signup_btn = tk.Button(button_frame, text="📝 Signup", command=self.signup,
                              bg='#27AE60', fg='white', font=('Arial', 11, 'bold'),
                              relief='flat', padx=20, pady=8, cursor='hand2')
        signup_btn.pack(side='left', padx=5)
        
        # Add hover effects
        self.add_hover_effect(login_btn, '#3498DB', '#2980B9')
        self.add_hover_effect(signup_btn, '#27AE60', '#229954')
    
    def add_hover_effect(self, button, normal_color, hover_color):
        def on_enter(e):
            button.config(bg=hover_color)
        def on_leave(e):
            button.config(bg=normal_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, user_id = auth.login(username, password)
        if success:
            # Clear the current window
            for widget in self.root.winfo_children():
                widget.destroy()
            # Create the main app in the same window
            App(self.root, user_id, username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, msg = auth.signup(username, password)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Signup Failed", msg)




if __name__ == "__main__":
    try:
        init_db()  # Ensure tables exist
        root = tk.Tk()
        root.resizable(True, True)  # Make window resizable
        AuthWindow(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

