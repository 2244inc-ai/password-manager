import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import hashlib
import re

BG = "#E8F5E9"
BTN = "#8BC34A"

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

categories = ["TikTok","YouTube","Email","WiFi","Другие"]

words = [
"tiger","panda","rocket","coffee","cookie",
"storm","dragon","falcon","river","forest"
]

current_user = None
current_category = None


def center_window(window,w,h):

    window.update_idletasks()

    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()

    x = int((sw-w)/2)
    y = int((sh-h)/2)

    window.geometry(f"{w}x{h}+{x}+{y}")


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


def check_strength(password):

    if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=-]*$',password):
        return "Только латиница"

    length = len(password) >= 8
    digit = bool(re.search(r"\d",password))

    score = sum([length,digit])

    if score == 2:
        return "Надёжный"
    elif score == 1:
        return "Средний"
    else:
        return "Слабый"


def update_strength(event=None):

    p = password_entry.get()

    strength_label.config(text=f"Надёжность: {check_strength(p)}")


def generate_password():

    w1 = random.choice(words)
    w2 = random.choice(words)
    n = random.randint(10,99)

    p = w1.capitalize()+w2.capitalize()+str(n)

    password_entry.delete(0,tk.END)
    password_entry.insert(0,p)

    update_strength()


def save_password():

    category = category_var.get()
    login = login_entry.get()
    password = password_entry.get()

    if login == "" or password == "":
        messagebox.showwarning("Ошибка","Заполните поля")
        return

    cursor.execute(
        "INSERT INTO passwords(user_id,category,login,password) VALUES (?,?,?,?)",
        (current_user,category,login,password)
    )

    conn.commit()

    load_passwords(category)


def load_passwords(category):

    global current_category
    current_category = category

    for i in tree.get_children():
        tree.delete(i)

    cursor.execute(
        "SELECT id,login,password FROM passwords WHERE user_id=? AND category=?",
        (current_user,category)
    )

    for row in cursor.fetchall():
        tree.insert("",tk.END,values=row)


def copy_password():

    sel = tree.selection()

    if not sel:
        return

    password = tree.item(sel[0])["values"][2]

    manager.clipboard_clear()
    manager.clipboard_append(password)


def delete_password():

    sel = tree.selection()

    if not sel:
        return

    rid = tree.item(sel[0])["values"][0]

    cursor.execute("DELETE FROM passwords WHERE id=?", (rid,))
    conn.commit()

    load_passwords(current_category)


def register():

    u = username_entry.get()
    p = password_reg.get()

    if u == "" or p == "":
        return

    try:

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (u,hash_password(p))
        )

        conn.commit()

        messagebox.showinfo("Успех","Пользователь создан")

    except:

        messagebox.showerror("Ошибка","Пользователь уже существует")


def login():

    global current_user

    u = username_entry.get()
    p = hash_password(password_reg.get())

    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (u,p)
    )

    r = cursor.fetchone()

    if r:

        current_user = r[0]
        open_manager()

    else:

        messagebox.showerror("Ошибка","Неверный логин")


def logout():

    manager.destroy()
    build_login()


def open_manager():

    global manager

    login_window.destroy()

    manager = tk.Tk()

    manager.title("Secure Password Manager")

    center_window(manager,1400,900)

    manager.configure(bg=BG)

    tk.Label(
        manager,
        text="🔐 Secure Password Manager",
        font=("Arial",28,"bold"),
        bg=BG
    ).pack(pady=15)

    top = tk.Frame(manager,bg=BG)
    top.pack()

    global category_var
    category_var = tk.StringVar()
    category_var.set(categories[0])

    tk.OptionMenu(top,category_var,*categories).grid(row=0,column=0,padx=10)

    tk.Label(top,text="Аккаунт",bg=BG).grid(row=1,column=1)
    tk.Label(top,text="Пароль",bg=BG).grid(row=1,column=2)

    global login_entry
    login_entry = tk.Entry(top,width=25,font=("Arial",14))
    login_entry.grid(row=2,column=1,padx=10)

    global password_entry
    password_entry = tk.Entry(top,width=25,font=("Arial",14))
    password_entry.grid(row=2,column=2,padx=10)

    password_entry.bind("<KeyRelease>",update_strength)

    global strength_label
    strength_label = tk.Label(manager,text="Надёжность:",bg=BG)
    strength_label.pack()

    tk.Button(top,text="Сгенерировать",bg=BTN,width=15,command=generate_password).grid(row=2,column=3,padx=10)
    tk.Button(top,text="Сохранить",bg=BTN,width=15,command=save_password).grid(row=2,column=4,padx=10)

    main = tk.Frame(manager,bg=BG)
    main.pack(pady=20)

    left = tk.Frame(main,bg=BG)
    left.grid(row=0,column=0,padx=30)

    tk.Label(left,text="Категории",font=("Arial",16),bg=BG).pack(pady=10)

    for c in categories:

        tk.Button(
            left,
            text=c,
            width=15,
            height=2,
            bg=BTN,
            command=lambda cat=c: load_passwords(cat)
        ).pack(pady=5)

    right = tk.Frame(main,bg=BG)
    right.grid(row=0,column=1)

    global tree

    tree = ttk.Treeview(right)

    tree["columns"] = ("ID","Login","Password")

    tree.column("#0",width=0)
    tree.column("ID",width=80)
    tree.column("Login",width=250)
    tree.column("Password",width=250)

    tree.heading("ID",text="ID")
    tree.heading("Login",text="Login")
    tree.heading("Password",text="Password")

    tree.pack()

    bottom = tk.Frame(manager,bg=BG)
    bottom.pack(pady=15)

    tk.Button(bottom,text="Копировать",bg=BTN,width=15,command=copy_password).grid(row=0,column=0,padx=10)
    tk.Button(bottom,text="Удалить",bg=BTN,width=15,command=delete_password).grid(row=0,column=1,padx=10)

    tk.Button(bottom,text="Выйти из аккаунта",bg=BTN,width=15,command=logout).grid(row=0,column=2,padx=10)

    tk.Button(bottom,text="Закрыть",bg=BTN,width=15,command=manager.destroy).grid(row=0,column=3,padx=10)

    tk.Label(
        manager,
        text="Владислав Попельский | Python | Tkinter | SQLite | VS Code | GitHub",
        bg=BG
    ).pack(side="bottom",pady=10)

    manager.mainloop()


def build_login():

    global login_window

    login_window = tk.Tk()

    login_window.title("Secure Password Manager")

    center_window(login_window,1400,800)

    login_window.configure(bg=BG)

    tk.Label(
        login_window,
        text="Secure Password Manager — это программа для безопасного хранения паролей.\n"
             "Она позволяет сохранять, генерировать и управлять паролями пользователей.\n"
             "Приложение помогает создавать более надёжные пароли и хранить их в одном месте.",
        font=("Arial",14),
        bg=BG
    ).pack(pady=20)

    main = tk.Frame(login_window,bg=BG)
    main.pack(expand=True,fill="both")

    main.grid_columnconfigure(0,weight=1)
    main.grid_columnconfigure(1,weight=1)
    main.grid_columnconfigure(2,weight=1)

    info = tk.Frame(main,bg=BG)
    info.grid(row=0,column=0,padx=40,sticky="nsew")

    tk.Label(
        info,
        text="Пароль — это секретная последовательность символов,\n"
             "используемая для подтверждения личности пользователя.\n\n"
             "Надёжность пароля — это степень его защищённости\n"
             "от подбора или взлома.\n\n"
             "Рекомендуется использовать длинные пароли,\n"
             "содержащие латиницу и цифры.",
        font=("Arial",13),
        bg=BG,
        justify="left",
        wraplength=350
    ).pack(expand=True)

    center = tk.Frame(main,bg=BG)
    center.grid(row=0,column=1,padx=40,sticky="nsew")

    tk.Label(center,text="🔐 Secure Password Manager",font=("Arial",24,"bold"),bg=BG).pack(pady=20)

    tk.Label(center,text="Имя пользователя",bg=BG).pack()

    global username_entry
    username_entry = tk.Entry(center,width=30,font=("Arial",14))
    username_entry.pack(pady=5)

    tk.Label(center,text="Пароль",bg=BG).pack()

    global password_reg
    password_reg = tk.Entry(center,show="*",width=30,font=("Arial",14))
    password_reg.pack(pady=5)

    tk.Button(center,text="Войти",bg=BTN,width=20,height=2,command=login).pack(pady=10)
    tk.Button(center,text="Зарегистрироваться",bg=BTN,width=20,height=2,command=register).pack()

    author = tk.Frame(main,bg=BG)
    author.grid(row=0,column=2,padx=40,sticky="nsew")

    tk.Label(
        author,
        text="Автор:\nВладислав Попельский\n\n"
             "Python\nTkinter\nSQLite\n"
             "Visual Studio Code\nGit\nGitHub",
        font=("Arial",13),
        bg=BG,
        justify="left",
        wraplength=350
    ).pack(expand=True)

    login_window.mainloop()


build_login()