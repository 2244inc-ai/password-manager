import tkinter as tk
from tkinter import messagebox
import random
import sqlite3

# ---------- DATABASE ----------

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

# ---------- DATA ----------

categories = ["TikTok","YouTube","Gmail","WiFi","Bank"]

words = [
"tiger","panda","rocket","coffee","cookie",
"storm","dragon","falcon","river","forest"
]

# ---------- FUNCTIONS ----------

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
        messagebox.showwarning("Warning","Fill login and password")
        return

    cursor.execute(
        "INSERT INTO passwords(category,login,password) VALUES (?,?,?)",
        (category,login,password)
    )

    conn.commit()

    messagebox.showinfo("Saved","Password saved")

    login_entry.delete(0,tk.END)
    password_entry.delete(0,tk.END)


def show_passwords():

    cursor.execute("SELECT category,login,password FROM passwords")

    rows = cursor.fetchall()

    text=""

    for row in rows:
        text+=f"{row[0]} | {row[1]} | {row[2]}\n"

    if text=="":
        text="No passwords saved"

    messagebox.showinfo("Saved Passwords",text)

# ---------- GUI ----------

root=tk.Tk()
root.title("Password Manager")
root.geometry("1000x800")

title=tk.Label(root,text="🔐 Password Manager",font=("Arial",18))
title.pack(pady=10)

category_var=tk.StringVar(root)
category_var.set(categories[0])

category_menu=tk.OptionMenu(root,category_var,*categories)
category_menu.pack(pady=5)

login_label=tk.Label(root,text="Login / Email")
login_label.pack()

login_entry=tk.Entry(root,width=30)
login_entry.pack(pady=5)

password_label=tk.Label(root,text="Password")
password_label.pack()

password_entry=tk.Entry(root,width=30)
password_entry.pack(pady=5)

generate_button=tk.Button(root,text="Suggest Password",command=generate_password)
generate_button.pack(pady=10)

save_button=tk.Button(root,text="Save Password",command=save_password)
save_button.pack(pady=5)

show_button=tk.Button(root,text="Show Saved Passwords",command=show_passwords)
show_button.pack(pady=5)

root.mainloop()