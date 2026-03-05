import tkinter as tk
import random
import sqlite3

# база данных
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

categories = ["TikTok", "YouTube", "Gmail", "WiFi", "Bank"]

words = [
"tiger","panda","rocket","coffee","cookie",
"storm","dragon","falcon","river","forest"
]

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

    cursor.execute(
        "INSERT INTO passwords(category,login,password) VALUES (?,?,?)",
        (category,login,password)
    )

    conn.commit()

# окно
root = tk.Tk()
root.title("Password Manager")
root.geometry("400x300")

title = tk.Label(root,text="Password Manager",font=("Arial",16))
title.pack(pady=10)

category_var = tk.StringVar(root)
category_var.set(categories[0])

category_menu = tk.OptionMenu(root,category_var,*categories)
category_menu.pack()

login_entry = tk.Entry(root,width=30)
login_entry.pack(pady=10)

generate_button = tk.Button(root,text="Suggest Password",command=generate_password)
generate_button.pack()

password_label = tk.Label(root,text="No password yet")
password_label.pack(pady=10)

save_button = tk.Button(root,text="Save Password",command=save_password)
save_button.pack()

root.mainloop()