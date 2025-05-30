import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from plyer import notification
import json
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import threading
import csv

REMINDER_FILE = "reminders.json"

def load_reminders():
    try:
        with open(REMINDER_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as file:
        json.dump(reminders, file, indent=2)

def send_email_notification(to_email, subject, body):
    try:
        sender_email = "mabdullahsaleem810@example.com"
        sender_password = "A_policy!123"  # Use app password if using Gmail

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print("Email error:", e)

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⏰ Auto Reminder App")
        self.root.geometry("600x400")
        self.dark_mode = False

        self.reminders = load_reminders()

        self.create_widgets()
        self.refresh_reminder_list()
        self.schedule_checker()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.title_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.email_var = tk.StringVar()

        ttk.Label(self.frame, text="Title").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.title_var, width=40).grid(row=0, column=1, columnspan=2)

        ttk.Label(self.frame, text="Time (YYYY-MM-DD HH:MM)").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.time_var).grid(row=1, column=1)

        ttk.Label(self.frame, text="Email (optional)").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.email_var).grid(row=2, column=1)

        ttk.Button(self.frame, text="Add Reminder", command=self.add_reminder).grid(row=3, column=0, pady=5)
        ttk.Button(self.frame, text="Export to CSV", command=self.export_csv).grid(row=3, column=1)
        ttk.Button(self.frame, text="🌓 Toggle Dark Mode", command=self.toggle_dark_mode).grid(row=3, column=2)

        self.tree = ttk.Treeview(self.frame, columns=("title", "time", "email"), show="headings")
        self.tree.heading("title", text="Title")
        self.tree.heading("time", text="Time")
        self.tree.heading("email", text="Email")
        self.tree.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")

        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure((0, 1, 2), weight=1)

    def toggle_dark_mode(self):
        style = ttk.Style(self.root)
        self.dark_mode = not self.dark_mode
        theme = "alt" if self.dark_mode else "default"
        bg = "#333" if self.dark_mode else "#fff"
        fg = "#eee" if self.dark_mode else "#000"
        style.theme_use(theme)
        self.root.configure(bg=bg)
        self.frame.configure(style="Dark.TFrame" if self.dark_mode else "TFrame")

    def add_reminder(self):
        title = self.title_var.get().strip()
        time = self.time_var.get().strip()
        email = self.email_var.get().strip()

        if not title or not time:
            messagebox.showerror("Input Error", "Title and time are required.")
            return

        try:
            datetime.strptime(time, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Time Format Error", "Use YYYY-MM-DD HH:MM format.")
            return

        self.reminders.append({"title": title, "time": time, "email": email})
        save_reminders(self.reminders)
        self.refresh_reminder_list()

        self.title_var.set("")
        self.time_var.set("")
        self.email_var.set("")

    def refresh_reminder_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in self.reminders:
            self.tree.insert("", "end", values=(r["title"], r["time"], r.get("email", "")))

    def check_reminders(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        updated_reminders = []

        for r in self.reminders:
            if r["time"] == now:
                notification.notify(
                    title="Reminder: " + r["title"],
                    message="Scheduled at " + r["time"],
                    timeout=10
                )
                if r.get("email"):
                    send_email_notification(
                        r["email"],
                        f"Reminder: {r['title']}",
                        f"This is your reminder scheduled at {r['time']}."
                    )
            else:
                updated_reminders.append(r)

        self.reminders = updated_reminders
        save_reminders(self.reminders)
        self.refresh_reminder_list()

    def schedule_checker(self):
        self.check_reminders()
        self.root.after(60000, self.schedule_checker)  # check every minute

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Time", "Email"])
            for r in self.reminders:
                writer.writerow([r["title"], r["time"], r.get("email", "")])
        messagebox.showinfo("Export Successful", f"Reminders exported to {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()
