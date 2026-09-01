import csv
import os
import re
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- CRITICAL IMPORTS FOR PYINSTALLER ---
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ----------------------------------------


class BulkLoginApp:

    def __init__(self, root):
        self.root = root
        self.root.title("CELL LEADERS Bulk Login Suite")
        self.root.geometry("680x520")
        self.root.minsize(600, 450)

        # State variables
        self.txt_file_path = ""
        self.csv_file_path = ""
        self.is_running = False

        self.setup_ui()

    def setup_ui(self):
        # Configuration Style
        style = ttk.Style()
        style.theme_use("clam")

        # Main Layout notebook tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Workspace Dash
        dash_frame = ttk.Frame(notebook, padding=15)
        notebook.add(dash_frame, text="Automation Panel")

        # --- SECTION 1: CONVERT TXT TO CSV ---
        convert_lf = ttk.LabelFrame(
            dash_frame, text=" Step 1: Parse Raw Data File (.txt) ", padding=10
        )
        convert_lf.pack(fill="x", pady=(0, 10))

        self.txt_label = ttk.Label(
            convert_lf, text="No .txt file selected", foreground="gray"
        )
        self.txt_label.pack(side="left", fill="x", expand=True, padx=(5, 10))

        btn_browse_txt = ttk.Button(
            convert_lf, text="Browse TXT", command=self.browse_txt
        )
        btn_browse_txt.pack(side="right", padx=5)

        self.btn_convert = ttk.Button(
            convert_lf,
            text="Convert to CSV",
            state="disabled",
            command=self.convert_txt_to_csv,
        )
        self.btn_convert.pack(side="right", padx=5)

        # --- SECTION 2: SELECT CSV & RUN AUTOMATION ---
        run_lf = ttk.LabelFrame(
            dash_frame,
            text=" Step 2: Target & Execute Automation (.csv) ",
            padding=10,
        )
        run_lf.pack(fill="x", pady=(0, 10))

        self.csv_label = ttk.Label(
            run_lf, text="No .csv file selected", foreground="gray"
        )
        self.csv_label.pack(side="left", fill="x", expand=True, padx=(5, 10))

        btn_browse_csv = ttk.Button(
            run_lf, text="Browse CSV", command=self.browse_csv
        )
        btn_browse_csv.pack(side="right", padx=5)

        # Interval Delay Configuration
        delay_frame = ttk.Frame(run_lf)
        delay_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ttk.Label(delay_frame, text="Delay Per Login (secs):").pack(
            side="left", padx=5
        )
        self.delay_spin = ttk.Spinbox(
            delay_frame, from_=1, to=60, width=5, justify="center"
        )
        self.delay_spin.set(10)
        self.delay_spin.pack(side="left", padx=5)

        self.btn_run = ttk.Button(
            delay_frame,
            text="Start Bulk Login",
            state="disabled",
            command=self.start_automation_thread,
        )
        self.btn_run.pack(side="right", padx=5)

        # --- SECTION 3: LIVE OUTPUT TERMINAL ---
        terminal_lf = ttk.LabelFrame(
            dash_frame, text=" Live Status Logs ", padding=5
        )
        terminal_lf.pack(fill="both", expand=True)

        self.log_text = tk.Text(
            terminal_lf,
            height=12,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            font=("Consolas", 10),
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            terminal_lf, orient="vertical", command=self.log_text.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    # ------------------ CORE FUNCTIONALITIES ------------------

    def log(self, message):
        """Thread-safe terminal printing tool."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def browse_txt(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            self.txt_file_path = file_path
            self.txt_label.config(
                text=os.path.basename(file_path), foreground="black"
            )
            self.btn_convert.config(state="normal")

    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.csv_file_path = file_path
            self.csv_label.config(
                text=os.path.basename(file_path), foreground="black"
            )
            self.btn_run.config(state="normal")

    def convert_txt_to_csv(self):
        """Your precise data conversion logic."""
        if not self.txt_file_path:
            return

        # Automatically determine path for saving the CSV alongside txt
        output_csv = os.path.splitext(self.txt_file_path)[0] + "_extracted.csv"
        extracted_data = []

        try:
            with open(self.txt_file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Split data records cleanly
            records = re.split(r"\d{4}-\d{2}-\d{2},?|\n", content)

            for record in records:
                record = record.strip()
                if not record:
                    continue

                email_match = re.search(r"([\w\.-]+@[\w\.-]+\.\w+)", record)
                if email_match:
                    email = email_match.group(1)
                    text_before_email = record.split(email)[0].strip()

                    if "\t" in text_before_email:
                        name_part = text_before_email.split("\t")[1]
                    else:
                        name_part = text_before_email

                    name_part = re.sub(r"\(.*?\)", "", name_part).strip()

                    if (
                        not name_part
                        or re.match(r"^[a-z0-9]+$", name_part)
                        or name_part.lower() == "please select a zone"
                    ):
                        name_part = "()"

                    extracted_data.append({"Name": name_part, "Email": email})

            with open(output_csv, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["Name", "Email"])
                writer.writeheader()
                writer.writerows(extracted_data)

            self.log(
                f"[SYSTEM]: Cleaned and generated CSV format: {len(extracted_data)} entries stored."
            )
            messagebox.showinfo(
                "Parser Complete", f"Saved successfully to:\n{output_csv}"
            )

            # Auto-load the freshly baked CSV directly into step 2 targets
            self.csv_file_path = output_csv
            self.csv_label.config(
                text=os.path.basename(output_csv), foreground="black"
            )
            self.btn_run.config(state="normal")

        except Exception as e:
            messagebox.showerror("Parsing Error", f"Could not format data: {e}")

    def start_automation_thread(self):
        """Spawns the selenium worker loop in a background thread to prevent GUI freezing."""
        if self.is_running:
            return

        try:
            delay = int(self.delay_spin.get())
        except ValueError:
            delay = 10

        self.is_running = True
        self.btn_run.config(state="disabled")
        self.btn_convert.config(state="disabled")

        # Spin thread
        threading.Thread(
            target=self.run_bulk_login, args=(delay,), daemon=True
        ).start()

    def run_bulk_login(self, wait_time):
        URL = "https://cell-leaders.rhapsodyofrealities.org"

        self.log("[SELENIUM]: Starting Chrome Web Driver...")

        try:
            # Explicitly set up the service and options using top-level imports
            chrome_service = Service()
            chrome_service.creation_flags = 0x08000000  # Stops CMD freeze

            options = Options()
            options.add_argument("--log-level=3")

            # Initialize driver using our configured service and options
            driver = webdriver.Chrome(service=chrome_service, options=options)
            driver.maximize_window()

            with open(self.csv_file_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                user_count = 1
                for row in reader:
                    user_name = row["Name"].strip()
                    user_email = row["Email"].strip()

                    if (
                        user_name == "N/A"
                        or not user_name
                    ):
                        self.log(
                            f"[SKIP]: Row {user_count} omitted due to unvalidated name field ({user_email})."
                        )
                        user_count += 1
                        continue

                    self.log(
                        f"[RUNNING] Account {user_count}: Attempting login for {user_name}..."
                    )

                    try:
                        driver.get(URL)
                        wait = WebDriverWait(driver, 10)

                        name_field = wait.until(
                            EC.presence_of_element_located((By.ID, "names"))
                        )
                        name_field.clear()
                        name_field.send_keys(user_name)

                        email_field = wait.until(
                            EC.presence_of_element_located((By.ID, "email"))
                        )
                        email_field.clear()
                        email_field.send_keys(user_email)

                        login_form = driver.find_element(By.ID, "loginForm_id")
                        login_form.submit()

                        self.log(
                            f"[SUCCESS]: Form submitted. Resting profile for {wait_time}s..."
                        )
                        time.sleep(wait_time)

                    except Exception as entry_error:
                        self.log(f"[WARNING]: Error on current profile submission.")

                    user_count += 1

        except Exception as global_err:
            self.log(f"[CRITICAL ERROR]: {global_err}")
        finally:
            self.log("[SYSTEM]: Automation workflow sequence complete.")
            try:
                driver.quit()
            except NameError:
                pass
            self.is_running = False
            self.btn_run.config(state="normal")
            self.btn_convert.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = BulkLoginApp(root)
    root.mainloop()