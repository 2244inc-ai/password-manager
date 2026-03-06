import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import hashlib
import re

# ---------- COLORS ----------

BG_COLOR = "#E8F5E9"
BTN_COLOR = "#8BC34A"
BTN_HOVER = "#7CB342"

# ---------- DATABASE ----------

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

# ---------- DATA ----------

categories = ["TikTok","YouTube","Email","WiFi","Другие"]

words = [
"tiger","panda","rocket","coffee","cookie",
"storm","dragon","falcon","river","forest"
]

current_user = None
current_category = None

# ---------- SECURITY ----------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- PASSWORD CHECK ----------

def check_password_strength(password):

    if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=-]*$', password):
        return "Только латиница"

    length = len(password) >= 8
    digit = bool(re.search(r"\d", password))

    score = sum([length,digit])

    if score == 2:
        return "Надёжный"
    elif score == 1:
        return "Средний"
    else:
        return "Слабый"

# ---------- PASSWORD FUNCTIONS ----------

def update_strength(event=None):

    password = password_entry.get()

    strength = check_password_strength(password)

    strength_label.config(text=f"Надёжность: {strength}")

def generate_password():

    word1 = random.choice(words)
    word2 = random.choice(words)
    number = random.randint(10,99)

    password = word1.capitalize()+word2.capitalize()+str(number)

    password_entry.delete(0,tk.END)
    password_entry.insert(0,password)

    update_strength()

def save_password():

    category = category_var.get()
    login = login_entry.get()
    password = password_entry.get()

    if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=-]+$', password):
        messagebox.showwarning("Ошибка","Пароль должен быть на латинице")
        return

    if login == "" or password == "":
        messagebox.showwarning("Ошибка","Заполните поля")
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
        messagebox.showwarning("Ошибка","Выберите пароль")
        return

    password = tree.item(selected[0])["values"][2]

    manager.clipboard_clear()
    manager.clipboard_append(password)

    messagebox.showinfo("Скопировано","Пароль скопирован")

def delete_password():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Ошибка","Выберите пароль")
        return

    row_id = tree.item(selected[0])["values"][0]

    cursor.execute("DELETE FROM passwords WHERE id=?", (row_id,))
    conn.commit()

    load_passwords(current_category)

# ---------- AUTH ----------

def register():

    username = username_entry.get()
    password = password_reg_entry.get()

    if username == "" or password == "":
        messagebox.showwarning("Ошибка","Заполните поля")
        return

    hashed = hash_password(password)

    try:

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username,hashed)
        )

        conn.commit()

        messagebox.showinfo("Успех","Пользователь создан")

    except:

        messagebox.showerror("Ошибка","Пользователь уже существует")

def login():

    global current_user

    username = username_entry.get()
    password = hash_password(password_reg_entry.get())

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username,password)
    )

    result = cursor.fetchone()

    if result:

        current_user = result[0]
        open_manager()

    else:

        messagebox.showerror("Ошибка","Неверный логин или пароль")

# ---------- LOGOUT ----------

def logout():

    manager.destroy()
    build_login()

# ---------- PASSWORD MANAGER WINDOW ----------

def open_manager():

    global manager

    login_window.destroy()

    manager = tk.Tk()

    manager.title("Secure Password Manager")

    manager.geometry("1920x1080")
    manager.configure(bg=BG_COLOR)

    title=tk.Label(
        manager,
        text="🔐 Secure Password Manager",
        font=("Arial",30,"bold"),
        bg=BG_COLOR
    )

    title.pack(pady=25)

    global category_var
    category_var = tk.StringVar(manager)
    category_var.set(categories[0])

    category_menu=tk.OptionMenu(manager,category_var,*categories)
    category_menu.pack(pady=10)

    tk.Label(manager,text="Логин / Email",bg=BG_COLOR).pack()

    global login_entry
    login_entry=tk.Entry(manager,width=40,font=("Arial",16))
    login_entry.pack(pady=5)

    tk.Label(manager,text="Пароль",bg=BG_COLOR).pack()

    global password_entry
    password_entry=tk.Entry(manager,width=40,font=("Arial",16))
    password_entry.pack(pady=5)

    password_entry.bind("<KeyRelease>",update_strength)

    global strength_label
    strength_label = tk.Label(manager,text="Надёжность:",bg=BG_COLOR)
    strength_label.pack()

    tk.Button(
        manager,
        text="Сгенерировать пароль",
        command=generate_password,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack(pady=10)

    tk.Button(
        manager,
        text="Сохранить пароль",
        command=save_password,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack(pady=5)

    category_frame=tk.Frame(manager,bg=BG_COLOR)
    category_frame.pack(pady=15)

    for cat in categories:

        tk.Button(
            category_frame,
            text=cat,
            width=15,
            height=2,
            bg=BTN_COLOR,
            command=lambda c=cat: load_passwords(c)
        ).pack(side="left",padx=10)

    global tree

    tree = ttk.Treeview(manager)

    tree["columns"]=("ID","Login","Password")

    tree.column("#0",width=0)
    tree.column("ID",width=80)
    tree.column("Login",width=350)
    tree.column("Password",width=350)

    tree.heading("ID",text="ID")
    tree.heading("Login",text="Login")
    tree.heading("Password",text="Password")

    tree.pack(pady=20)

    tk.Button(
        manager,
        text="Копировать пароль",
        command=copy_password,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack(pady=5)

    tk.Button(
        manager,
        text="Удалить пароль",
        command=delete_password,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack(pady=5)

    tk.Button(
        manager,
        text="Выйти из аккаунта",
        command=logout,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack(pady=10)

    tk.Button(
        manager,
        text="Закрыть программу",
        command=manager.destroy,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack()

    manager.mainloop()

# ---------- LOGIN WINDOW ----------

def build_login():

    global login_window

    login_window=tk.Tk()

    login_window.title("Secure Password Manager")
    login_window.geometry("1920x1080")
    login_window.configure(bg=BG_COLOR)

    title=tk.Label(
        login_window,
        text="🔐 Secure Password Manager",
        font=("Arial",32,"bold"),
        bg=BG_COLOR
    )

    title.pack(pady=30)

    description = tk.Label(
        login_window,
        text="Программа для безопасного хранения паролей.\n"
             "Позволяет сохранять, генерировать и управлять паролями.",
        font=("Arial",16),
        bg=BG_COLOR
    )

    description.pack(pady=10)

    requirements = tk.Label(
        login_window,
        text="Требования к паролю:\n"
             "- минимум 8 символов\n"
             "- латиница\n"
             "- желательно наличие цифр",
        font=("Arial",14),
        bg=BG_COLOR
    )

    requirements.pack(pady=15)

    tk.Label(login_window,text="Имя пользователя",bg=BG_COLOR).pack()

    global username_entry
    username_entry=tk.Entry(login_window,width=40,font=("Arial",16))
    username_entry.pack(pady=5)

    tk.Label(login_window,text="Пароль",bg=BG_COLOR).pack()

    global password_reg_entry
    password_reg_entry=tk.Entry(login_window,show="*",width=40,font=("Arial",16))
    password_reg_entry.pack(pady=5)

    tk.Button(
        login_window,
        text="Войти",
        command=login,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack(pady=10)

    tk.Button(
        login_window,
        text="Зарегистрироваться",
        command=register,
        width=25,
        height=2,
        bg=BTN_COLOR
    ).pack()

    login_window.mainloop()

# ---------- START ----------

build_login()