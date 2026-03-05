import tkinter as tk
from tkinter import messagebox
import random
import sqlite3

# ---------------- БАЗА ДАННЫХ ----------------

conn = sqlite3.connect("passwords.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords(
id INTEGER PRIMARY KEY AUTOINCREMENT,
category TEXT,
login TEXT,
password TEXT
)
""")

# ---------------- ДАННЫЕ ----------------

categories = ["TikTok", "YouTube", "Gmail", "WiFi", "Bank"]

words = [
"tiger","panda","rocket","coffee","cookie",
"storm","dragon","falcon","river","forest"
]

# ---------------- ФУНКЦИИ ----------------

def generate_password():

    word1 = random.choice(words)
    word2 = random.choice(words)
    number = random.randint(10,99)

    password = word1.capitalize() + word2.capitalize() + str(number)

    password_label.config(text=password)


def save_password():

    category = category_var.get()
    login = login_entry.get()
    password = password_label.cget("text")

    if login == "":
        messagebox.showwarning("Warning","Please enter login")
        return

    if password == "No password yet":
        messagebox.showwarning("Warning","Generate a password first")
        return

    cursor.execute(
        "INSERT INTO passwords(category,login,password) VALUES (?,?,?)",
        (category,login,password)
    )

    conn.commit()

    messagebox.showinfo("Saved","Password saved successfully")

    login_entry.delete(0, tk.END)
    password_label.config(text="No password yet")


def show_passwords():

    cursor.execute("SELECT category,login,password FROM passwords")

    rows = cursor.fetchall()

    text = ""

    for row in rows:
        text += f"{row[0]} | {row[1]} | {row[2]}\n"

    if text == "":
        text = "No saved passwords"

    messagebox.showinfo("Saved passwords", text)

# ---------------- ИНТЕРФЕЙС ----------------

root = tk.Tk()
root.title("Simple Password Manager")
root.geometry("420x350")

title = tk.Label(root,text="🔐 Password Manager",font=("Arial",18))
title.pack(pady=10)

category_var = tk.StringVar(root)
category_var.set(categories[0])

category_menu = tk.OptionMenu(root,category_var,*categories)
category_menu.pack(pady=5)

login_label = tk.Label(root,text="Login or Email")
login_label.pack()

login_entry = tk.Entry(root,width=30)
login_entry.pack(pady=5)

generate_button = tk.Button(root,text="Suggest Password",command=generate_password)
generate_button.pack(pady=10)

password_label = tk.Label(root,text="No password yet",font=("Arial",12))
password_label.pack()

save_button = tk.Button(root,text="Save Password",command=save_password)
save_button.pack(pady=10)

show_button = tk.Button(root,text="Show Saved Passwords",command=show_passwords)
show_button.pack(pady=5)

root.mainloop()