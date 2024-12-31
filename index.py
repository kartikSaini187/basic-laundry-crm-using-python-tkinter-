import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog

def connect_db():
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    # Create table for laundry orders
    c.execute('''
    CREATE TABLE IF NOT EXISTS laundry_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        item_name TEXT,
        service_name TEXT,
        quantity INTEGER,
        status TEXT
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    conn.commit()
    conn.close()

def check_users_exist():
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def register_user(username, password):
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
        return True
    except sqlite3.IntegrityError:
        messagebox.showwarning("Error", "Username already exists!")
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

def show_registration_screen():
    # Hide the main window
    window.withdraw()
    
    reg_window = tk.Toplevel(window)
    reg_window.title("First User Registration")
    reg_window.geometry("300x250")
    reg_window.grab_set()  

    tk.Label(reg_window, text="Welcome!\nCreate First User Account", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(reg_window, text="Username:").grid(row=1, column=0, padx=10, pady=5)
    username_entry = tk.Entry(reg_window)
    username_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(reg_window, text="Password:").grid(row=2, column=0, padx=10, pady=5)
    password_entry = tk.Entry(reg_window, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(reg_window, text="Confirm Password:").grid(row=3, column=0, padx=10, pady=5)
    confirm_password_entry = tk.Entry(reg_window, show="*")
    confirm_password_entry.grid(row=3, column=1, padx=10, pady=5)

    def attempt_registration():
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        # Validate inputs
        if not username:
            messagebox.showwarning("Error", "Username cannot be empty!")
            return
        if not password:
            messagebox.showwarning("Error", "Password cannot be empty!")
            return
        if password != confirm_password:
            messagebox.showwarning("Error", "Passwords do not match!")
            return
        if register_user(username, password):
            reg_window.destroy()
            show_login_screen()

    
    def show_login():
        reg_window.destroy()
        show_login_screen()

    tk.Button(reg_window, text="Login", command=show_login).grid(row=4, column=0, columnspan=1, pady=5)
    tk.Button(reg_window, text="Register", command=attempt_registration).grid(row=4, column=1, columnspan=2, pady=10)
    

    def on_closing():
        window.quit()

    reg_window.protocol("WM_DELETE_WINDOW", on_closing)
    reg_window.focus_force() 

def show_login_screen():
    if not check_users_exist():
        show_registration_screen()
        return

    window.withdraw()
    
    login_window = tk.Toplevel(window)
    login_window.title("Login")
    login_window.geometry("300x200")
    login_window.grab_set()

    tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(login_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    def attempt_login():
        username = username_entry.get()
        password = password_entry.get()
        if login_user(username, password):
            messagebox.showinfo("Success", "Login successful!")
            login_window.destroy()
            window.deiconify()
            refresh_orders()
        else:
            messagebox.showwarning("Error", "Invalid username or password!")

    def show_registration():
        login_window.destroy()
        show_registration_screen()

    def on_closing():
        window.quit()

    tk.Button(login_window, text="Register", command=show_registration).grid(row=2, column=0, columnspan=1, pady=10)
    tk.Button(login_window, text="Login", command=attempt_login).grid(row=2, column=1, columnspan=1, pady=10)

    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    login_window.focus_force() 

def logout():
    messagebox.showinfo("Logout", "You have been logged out!")
    show_login_screen()

def add_order():
    customer_name = customer_name_entry.get()
    service_name = service_name_entry.get()  # New field
    item_name = item_name_entry.get()
    quantity = quantity_entry.get()

    if not customer_name or not service_name or not item_name or not quantity:
        messagebox.showwarning("Input Error", "All fields must be filled!")
        return

    quantity = int(quantity)
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO laundry_orders (customer_name, service_name, item_name, quantity, status)
    VALUES (?, ?, ?, ?, ?)''', (customer_name, service_name, item_name, quantity, 'Pending'))
    conn.commit()
    conn.close()

    customer_name_entry.delete(0, tk.END)
    service_name_entry.delete(0, tk.END)
    item_name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

    messagebox.showinfo("Success", "Order added successfully!")
    refresh_orders()


def mark_completed():
    selected_order_index = order_listbox.curselection()
    if not selected_order_index:
        messagebox.showwarning("Selection Error", "Please select an order to mark as completed.")
        return
    selected_order_id = order_listbox.get(selected_order_index)
    order_id = selected_order_id.split()[1].strip(',')
    status = selected_order_id.split()[9].strip(',')
    if status == "Completed":
        messagebox.showwarning("Selection Error", "Please select an pending order only")
        return
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('''
    UPDATE laundry_orders
    SET status = ?
    WHERE id = ?''', ('Completed', order_id))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Order marked as completed!")
    refresh_orders()

def refresh_orders():
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('SELECT * FROM laundry_orders')
    orders = c.fetchall()
    conn.close()

    order_listbox.delete(0, tk.END)
    for order in orders:
        order_listbox.insert(
            tk.END,
            f"ID: {order[0]}, {order[1]} - {order[2]} ({order[3]}) - Qty: {order[4]} - Status: {order[5]}"
        )


def delete_orders():
    selected_order_index = order_listbox.curselection()
    if not selected_order_index:
        messagebox.showwarning("Selection Error", "Please select an order to mark as completed.")
        return
    selected_order_id = order_listbox.get(selected_order_index)
    order_id = selected_order_id.split()[1].strip(',')
    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('''
    DELETE FROM laundry_orders
    WHERE id = ?''', (order_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Order deleted successfully")
    refresh_orders()

def load_order_data():
    selected_index = order_listbox.curselection()

    if not selected_index:
        messagebox.showwarning("Selection Error", "Please select an order to edit.")
        return

    selected_order = order_listbox.get(selected_index)

    order_id = selected_order.split()[1].strip(',')

    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute("SELECT * FROM laundry_orders WHERE id = ?", (order_id,))
    order_details = c.fetchone()
    conn.close()

    if order_details:
        customer_name_entry.delete(0, tk.END)
        customer_name_entry.insert(0, order_details[1])

        service_name_entry.delete(0, tk.END)
        service_name_entry.insert(0, order_details[2])

        
        item_name_entry.delete(0, tk.END)
        item_name_entry.insert(0, order_details[3])
        
        quantity_entry.delete(0, tk.END)
        quantity_entry.insert(0, order_details[4])

        update_button.grid(row=3, column=1, columnspan=2, pady=10)

        global current_order_id
        current_order_id = order_id
    else:
        messagebox.showwarning("Error", "Order not found.")
        
def update_order():
    customer_name = customer_name_entry.get()
    service_name = service_name_entry.get()
    item_name = item_name_entry.get()
    quantity = quantity_entry.get()

    if not customer_name or not item_name or not quantity:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return

    conn = sqlite3.connect('laundry_management.db')
    c = conn.cursor()
    c.execute('''
        UPDATE laundry_orders
        SET customer_name = ?, service_name = ?, item_name = ?, quantity = ?
        WHERE id = ?''', (customer_name, service_name, item_name, quantity, current_order_id))


    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Order updated successfully.")

    update_button.grid_forget()
    customer_name_entry.delete(0, tk.END)
    service_name_entry.delete(0, tk.END)
    item_name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    
    refresh_orders()

window = tk.Tk()
window.title("Laundry Management System")

customer_name_label = tk.Label(window, text="Customer Name:")
customer_name_label.grid(row=0, column=0, padx=10, pady=10)
customer_name_entry = tk.Entry(window)
customer_name_entry.grid(row=0, column=1, padx=10, pady=10)

service_name_label = tk.Label(window, text="Service Name:")
service_name_label.grid(row=1, column=0, padx=10, pady=10)
service_name_entry = tk.Entry(window)
service_name_entry.grid(row=1, column=1, padx=10, pady=10)

item_name_label = tk.Label(window, text="Item Name:")
item_name_label.grid(row=2, column=0, padx=10, pady=10)
item_name_entry = tk.Entry(window)
item_name_entry.grid(row=2, column=1, padx=10, pady=10)


quantity_label = tk.Label(window, text="Quantity:")
quantity_label.grid(row=3, column=0, padx=10, pady=10)
quantity_entry = tk.Entry(window)
quantity_entry.grid(row=3, column=1, padx=10, pady=10)

add_order_button = tk.Button(window, text="Add Order", command=add_order)
add_order_button.grid(row=4, column=0, columnspan=2, pady=10)

logout_button = tk.Button(window, text="Logout", command=logout)
logout_button.grid(row=4, column=2, padx=10, pady=10)

update_button = tk.Button(window, text="Update", command=update_order)
update_button.grid(row=4, column=1, columnspan=2, pady=10)
update_button.grid_forget()

order_listbox_label = tk.Label(window, text="Order list:")
order_listbox_label.grid(row=5, column=0, columnspan=2, pady=10)

order_listbox = tk.Listbox(window, height=10, width=70)
order_listbox.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

window.grid_columnconfigure(0, weight=0)
window.grid_columnconfigure(1, weight=0)
window.grid_columnconfigure(2, weight=0)

button_width = 15

mark_completed_button = tk.Button(window, text="Mark Completed", command=mark_completed, width=button_width)
mark_completed_button.grid(row=7, column=0)

delete_button = tk.Button(window, text="Delete", command=delete_orders, width=button_width)
delete_button.grid(row=7, column=1, padx=2, pady=2)

edit_button = tk.Button(window, text="Edit", command=load_order_data, width=button_width)
edit_button.grid(row=7, column=2, padx=2, pady=2)



connect_db()
show_login_screen()


window.mainloop()
