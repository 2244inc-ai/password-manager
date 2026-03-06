import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import hashlib

# ---------------- DATABASE ----------------

conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
category TEXT,
login TEXT,
password TEXT
)
""")

# ---------------- DATA ----------------

categories = ["TikTok","YouTube","Gmail","WiFi","Bank"]

words = [
"tiger","panda","rocket","coffee","cookie",
"storm","dragon","falcon","river","forest"
]

current_user = None
current_category = None

# ---------------- CENTER WINDOW ----------------

def center_window(window,width,height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width/2)-(width/2))
    y = int((screen_height/2)-(height/2))

    window.geometry(f"{width}x{height}+{x}+{y}")

# ---------------- SECURITY ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- AUTH ----------------

def register():

    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showwarning("Error","Fill all fields")
        return

    hashed = hash_password(password)

    try:

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username,hashed)
        )

        conn.commit()

        messagebox.showinfo("Success","User created")

    except:

        messagebox.showerror("Error","User already exists")

def login():

    global current_user

    username = username_entry.get()
    password = hash_password(password_entry.get())

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username,password)
    )

    result = cursor.fetchone()

    if result:

        current_user = result[0]
        open_manager()

    else:

        messagebox.showerror("Error","Wrong login or password")

# ---------------- PASSWORD FUNCTIONS ----------------

def generate_password():

    word1 = random.choice(words)
    word2 = random.choice(words)
    number = random.randint(10,99)

    password = word1.capitalize()+word2.capitalize()+str(number)

    password_entry.delete(0,tk.END)
    password_entry.insert(0,password)

def save_password():

    category = category_var.get()
    login = login_entry.get()
    password = password_entry.get()

    if login == "" or password == "":
        messagebox.showwarning("Error","Fill fields")
        return

    cursor.execute(
        "INSERT INTO passwords(user_id,category,login,password) VALUES (?,?,?,?)",
        (current_user,category,login,password)
    )

    conn.commit()

    login_entry.delete(0,tk.END)
    password_entry.delete(0,tk.END)

    load_passwords(category)

def load_passwords(category):

    global current_category
    current_category = category

    for row in tree.get_children():
        tree.delete(row)

    cursor.execute(
        "SELECT id,login,password FROM passwords WHERE user_id=? AND category=?",
        (current_user,category)
    )

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("",tk.END,values=row)

def copy_password():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Error","Select password")
        return

    password = tree.item(selected[0])["values"][2]

    manager.clipboard_clear()
    manager.clipboard_append(password)

    messagebox.showinfo("Copied","Password copied")

def delete_password():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Error","Select password")
        return

    row_id = tree.item(selected[0])["values"][0]

    cursor.execute(
        "DELETE FROM passwords WHERE id=?",
        (row_id,)
    )

    conn.commit()

    load_passwords(current_category)

# ---------------- LOGOUT ----------------

def logout():

    manager.destroy()
    build_login()

# ---------------- PASSWORD MANAGER ----------------

def open_manager():

    global manager

    login_window.destroy()

    manager = tk.Tk()

    manager.title("Password Manager")

    center_window(manager,800,800)

    manager.configure(bg="#1e1e2f")

    title=tk.Label(
        manager,
        text="🔐 Password Manager",
        font=("Arial",20,"bold"),
        fg="white",
        bg="#1e1e2f"
    )

    title.pack(pady=15)

    # CATEGORY SELECT

    global category_var
    category_var = tk.StringVar(manager)
    category_var.set(categories[0])

    category_menu=tk.OptionMenu(manager,category_var,*categories)
    category_menu.pack(pady=5)

    # LOGIN

    tk.Label(manager,text="Login / Email",bg="#1e1e2f",fg="white").pack()

    global login_entry
    login_entry=tk.Entry(manager,width=35)
    login_entry.pack(pady=5)

    # PASSWORD

    tk.Label(manager,text="Password",bg="#1e1e2f",fg="white").pack()

    global password_entry
    password_entry=tk.Entry(manager,width=35)
    password_entry.pack(pady=5)

    tk.Button(
        manager,
        text="Suggest Password",
        command=generate_password,
        bg="#4CAF50",
        fg="white",
        width=20
    ).pack(pady=10)

    tk.Button(
        manager,
        text="Save Password",
        command=save_password,
        bg="#2196F3",
        fg="white",
        width=20
    ).pack(pady=5)

    # CATEGORY BUTTONS

    category_frame=tk.Frame(manager,bg="#1e1e2f")
    category_frame.pack(pady=10)

    for cat in categories:

        tk.Button(
            category_frame,
            text=cat,
            width=10,
            command=lambda c=cat: load_passwords(c)
        ).pack(side="left",padx=5)

    # TABLE

    global tree

    tree = ttk.Treeview(manager)

    tree["columns"]=("ID","Login","Password")

    tree.column("#0",width=0,stretch=tk.NO)
    tree.column("ID",width=50)
    tree.column("Login",width=220)
    tree.column("Password",width=220)

    tree.heading("#0",text="")
    tree.heading("ID",text="ID")
    tree.heading("Login",text="Login")
    tree.heading("Password",text="Password")

    tree.pack(pady=20)

    # ACTION BUTTONS

    tk.Button(
        manager,
        text="Copy Password",
        command=copy_password,
        bg="#4CAF50",
        fg="white",
        width=20
    ).pack(pady=3)

    tk.Button(
        manager,
        text="Delete Password",
        command=delete_password,
        bg="#f44336",
        fg="white",
        width=20
    ).pack(pady=3)

    tk.Button(
        manager,
        text="Logout",
        command=logout,
        bg="#ff9800",
        fg="white",
        width=20
    ).pack(pady=8)

    tk.Button(
        manager,
        text="Close",
        command=manager.destroy,
        bg="#9e9e9e",
        fg="white",
        width=20
    ).pack()

    manager.mainloop()

# ---------------- LOGIN WINDOW ----------------

def build_login():

    global login_window

    login_window=tk.Tk()

    login_window.title("Secure Password Manager")

    center_window(login_window,500,400)

    login_window.configure(bg="#1e1e2f")

    title=tk.Label(
        login_window,
        text="🔐 Secure Password Manager",
        font=("Arial",20,"bold"),
        fg="white",
        bg="#1e1e2f"
    )

    title.pack(pady=25)

    tk.Label(login_window,text="Username",bg="#1e1e2f",fg="white").pack()

    global username_entry
    username_entry=tk.Entry(login_window,width=30)
    username_entry.pack(pady=5)

    tk.Label(login_window,text="Password",bg="#1e1e2f",fg="white").pack()

    global password_entry
    password_entry=tk.Entry(login_window,show="*",width=30)
    password_entry.pack(pady=5)

    tk.Button(
        login_window,
        text="Login",
        command=login,
        bg="#4CAF50",
        fg="white",
        width=20
    ).pack(pady=10)

    tk.Button(
        login_window,
        text="Register",
        command=register,
        bg="#2196F3",
        fg="white",
        width=20
    ).pack()

    login_window.mainloop()

# ---------------- START ----------------

build_login()