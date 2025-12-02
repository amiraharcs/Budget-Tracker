import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests

DATA_FILE = "transactions.json"

# --- Load transactions from file ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        transactions = json.load(f)
else:
    transactions = []

# --- Save transactions to file ---
def save_transactions():
    with open(DATA_FILE, "w") as f:
        json.dump(transactions, f, indent=4)

# --- Update the table and balance ---
def refresh_ui(filter_type=None, min_amount=None, max_amount=None):
    for item in table.get_children():
        table.delete(item)

    income_total = 0
    expense_total = 0

    for t in transactions:
        if filter_type and filter_type != "all" and t["type"] != filter_type:
            continue
        if min_amount is not None and t["amount"] < min_amount:
            continue
        if max_amount is not None and t["amount"] > max_amount:
            continue

        table.insert("", "end", values=(t["type"].capitalize(), f"£{t['amount']:.2f}", t["desc"]))
        if t["type"] == "income":
            income_total += t["amount"]
        elif t["type"] == "expense":
            expense_total += t["amount"]

    balance = income_total - expense_total
    balance_label.config(
        text=f"Income: £{income_total:.2f}   Expense: £{expense_total:.2f}   Balance: £{balance:.2f}"
    )


# --- Add transaction ---
def add_transaction():
    t_type = type_var.get().lower()
    try:
        amount = float(amount_entry.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number for amount.")
        return

    desc = desc_entry.get().strip()
    if not desc:
        messagebox.showerror("Missing Description", "Please enter a description.")
        return

    transactions.append({"type": t_type, "amount": amount, "desc": desc})
    save_transactions()
    refresh_ui()

    # Clear inputs
    amount_entry.delete(0, tk.END)
    desc_entry.delete(0, tk.END)

# --- Main Window ---
root = tk.Tk()
root.title("💰 Budget Tracker")
root.geometry("600x400")

# --- Input Fields ---
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

type_var = tk.StringVar(value="income")
type_menu = ttk.Combobox(input_frame, textvariable=type_var, values=["income", "expense"], width=10)
type_menu.grid(row=0, column=0, padx=5)

amount_entry = tk.Entry(input_frame, width=15)
amount_entry.grid(row=0, column=1, padx=5)
amount_entry.insert(0, "Amount")

desc_entry = tk.Entry(input_frame, width=30)
desc_entry.grid(row=0, column=2, padx=5)
desc_entry.insert(0, "Description")

add_button = tk.Button(input_frame, text="Add", command=add_transaction)
add_button.grid(row=0, column=3, padx=5)

# --- Table to Display Transactions ---
table = ttk.Treeview(root, columns=("Type", "Amount", "Description"), show="headings")
table.heading("Type", text="Type")
table.heading("Amount", text="Amount")
table.heading("Description", text="Description")
table.pack(expand=True, fill="both", padx=10)

# --- Delete Button ---
def delete_transaction():
    selected = table.selection()
    if not selected:
        messagebox.showinfo("No selection", "Please select a transaction to delete.")
        return

    index = table.index(selected[0])
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
    if confirm:
        transactions.pop(index)
        save_transactions()
        refresh_ui()

delete_button = tk.Button(root, text="Delete Selected", command=delete_transaction)
delete_button.pack(pady=5)

# --- Filter Section ---
filter_frame = tk.Frame(root)
filter_frame.pack(pady=5)

filter_type_var = tk.StringVar(value="all")
tk.Label(filter_frame, text="Type:").grid(row=0, column=0)
ttk.Combobox(filter_frame, textvariable=filter_type_var, values=["all", "income", "expense"], width=10).grid(row=0, column=1)

tk.Label(filter_frame, text="Min Amount:").grid(row=0, column=2)
min_amount_entry = tk.Entry(filter_frame, width=10)
min_amount_entry.grid(row=0, column=3)

tk.Label(filter_frame, text="Max Amount:").grid(row=0, column=4)
max_amount_entry = tk.Entry(filter_frame, width=10)
max_amount_entry.grid(row=0, column=5)

def apply_filter():
    f_type = filter_type_var.get()
    try:
        min_val = float(min_amount_entry.get()) if min_amount_entry.get() else None
        max_val = float(max_amount_entry.get()) if max_amount_entry.get() else None
    except ValueError:
        messagebox.showerror("Invalid input", "Min/Max amount must be a number.")
        return
    refresh_ui(filter_type=f_type, min_amount=min_val, max_amount=max_val)

def clear_filter():
    filter_type_var.set("all")
    min_amount_entry.delete(0, tk.END)
    max_amount_entry.delete(0, tk.END)
    refresh_ui()

tk.Button(filter_frame, text="Apply Filter", command=apply_filter).grid(row=0, column=6, padx=5)
tk.Button(filter_frame, text="Clear Filter", command=clear_filter).grid(row=0, column=7)


# --- Balance Summary ---
balance_label = tk.Label(root, text="Income: £0.00   Expense: £0.00   Balance: £0.00", font=("Arial", 12))
balance_label.pack(pady=5)

# --- Start UI ---
refresh_ui()
root.mainloop()


 
