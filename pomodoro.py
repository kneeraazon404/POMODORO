import customtkinter as ctk
from tkinter import messagebox, simpledialog
import datetime
import sqlite3

# Set the overall theme and color scheme
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class PomodoroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro & Goals Ledger")
        self.geometry("900x700")
        self.today = str(datetime.date.today())
        
        # Mini Timer Variables
        self.mini_window = None
        self.mini_lbl = None
        
        # Database Setup
        self.init_db()
        
        # Timer Variables
        self.is_running = False
        self.time_left = 0
        self.current_mode = "Study"
        
        # UI Setup - Modern Tabview
        self.tabview = ctk.CTkTabview(self, width=850, height=650)
        self.tabview.pack(padx=20, pady=20, expand=True, fill="both")
        
        self.tab_home = self.tabview.add("Dashboard & Goals")
        self.tab_timer = self.tabview.add("Pomodoro & Tasks")
        
        self.build_home_tab()
        self.build_timer_tab()
        
        # Load Initial Data
        self.load_dashboard_stats()
        self.load_goals()
        self.load_tasks()

    # ==============================
    # DATABASE SETUP
    # ==============================
    def init_db(self):
        self.conn = sqlite3.connect("pomodoro_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, name TEXT, status TEXT, date_added TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ledger (date TEXT PRIMARY KEY, study_minutes INTEGER)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS goals (type TEXT PRIMARY KEY, content TEXT)''')
        
        # This handles your Rollover Request: Unfinished tasks move to today, completed tasks stay on their original date.
        self.cursor.execute("UPDATE tasks SET date_added = ? WHERE status = 'pending' AND date_added != ?", (self.today, self.today))
        
        self.cursor.execute("INSERT OR IGNORE INTO ledger (date, study_minutes) VALUES (?, 0)", (self.today,))
        self.conn.commit()

    # ==============================
    # TAB 1: DASHBOARD & GOALS
    # ==============================
    def build_home_tab(self):
        stats_frame = ctk.CTkFrame(self.tab_home, corner_radius=15)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        lbl_dash = ctk.CTkLabel(stats_frame, text="Daily Dashboard", font=("Helvetica", 24, "bold"))
        lbl_dash.pack(pady=10)
        
        self.stats_text = ctk.StringVar()
        lbl_stats = ctk.CTkLabel(stats_frame, textvariable=self.stats_text, font=("Helvetica", 16))
        lbl_stats.pack(pady=5)
        
        btn_ledger = ctk.CTkButton(stats_frame, text="View Past Ledger", fg_color="#636E72", hover_color="#2D3436", command=self.view_ledger_history)
        btn_ledger.pack(pady=15)
        
        goals_label = ctk.CTkLabel(self.tab_home, text="High-Level Goals", font=("Helvetica", 20, "bold"))
        goals_label.pack(pady=(15, 5))
        
        goals_frame = ctk.CTkFrame(self.tab_home, fg_color="transparent")
        goals_frame.pack(fill="both", expand=True, padx=20)
        
        self.goal_text_widgets = {}
        goals = ["Yearly", "Quarterly", "Monthly", "Weekly"]
        
        for i, goal in enumerate(goals):
            frame = ctk.CTkFrame(goals_frame, corner_radius=10)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            goals_frame.grid_columnconfigure(i%2, weight=1)
            goals_frame.grid_rowconfigure(i//2, weight=1)
            
            ctk.CTkLabel(frame, text=f"{goal} Goals", font=("Helvetica", 16, "bold"), text_color="#74B9FF").pack(anchor="w", padx=10, pady=5)
            text_area = ctk.CTkTextbox(frame, height=100, wrap="word", corner_radius=10)
            text_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self.goal_text_widgets[goal] = text_area
            
        btn_save = ctk.CTkButton(self.tab_home, text="Save Goals", font=("Helvetica", 14, "bold"), command=self.save_goals)
        btn_save.pack(pady=15)

    def load_dashboard_stats(self):
        self.cursor.execute("SELECT study_minutes FROM ledger WHERE date = ?", (self.today,))
        mins = self.cursor.fetchone()[0]
        hours = round(mins / 60, 2)
        
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE date_added = ?", (self.today,))
        total_tasks = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM tasks WHERE date_added = ? AND status = 'completed'", (self.today,))
        completed_tasks = self.cursor.fetchone()[0]
        
        self.stats_text.set(f"Date: {self.today}   |   Study Time: {hours} hrs ({mins} mins)   |   Tasks Done: {completed_tasks} / {total_tasks}")

    def load_goals(self):
        self.cursor.execute("SELECT type, content FROM goals")
        for goal_type, content in self.cursor.fetchall():
            if goal_type in self.goal_text_widgets:
                self.goal_text_widgets[goal_type].insert("1.0", content)

    def save_goals(self):
        for goal_type, widget in self.goal_text_widgets.items():
            content = widget.get("1.0", "end-1c")
            self.cursor.execute("REPLACE INTO goals (type, content) VALUES (?, ?)", (goal_type, content))
        self.conn.commit()

    def view_ledger_history(self):
        target_date = simpledialog.askstring("Ledger History", "Enter date (YYYY-MM-DD):", initialvalue=self.today)
        if not target_date: return
            
        self.cursor.execute("SELECT study_minutes FROM ledger WHERE date = ?", (target_date,))
        ledger_row = self.cursor.fetchone()
        if not ledger_row:
            messagebox.showinfo("Ledger", f"No data found for {target_date}.")
            return
            
        self.cursor.execute("SELECT name, status FROM tasks WHERE date_added = ?", (target_date,))
        tasks = "\n".join([f"- {name} [{status}]" for name, status in self.cursor.fetchall()]) or "No tasks."
        messagebox.showinfo(f"Ledger for {target_date}", f"Study Time: {ledger_row[0]} mins\n\nTasks:\n{tasks}")

    # ==============================
    # TAB 2: POMODORO & TASKS
    # ==============================
    def build_timer_tab(self):
        timer_frame = ctk.CTkFrame(self.tab_timer, corner_radius=20)
        timer_frame.pack(pady=20, padx=20, fill="x")
        
        self.lbl_timer = ctk.CTkLabel(timer_frame, text="00:00", font=("Helvetica", 80, "bold"), text_color="#00CEC9")
        self.lbl_timer.pack(pady=(20, 10))
        
        controls_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        ctk.CTkLabel(controls_frame, text="Study (min):", font=("Helvetica", 14)).grid(row=0, column=0, padx=10)
        self.opt_study = ctk.CTkOptionMenu(controls_frame, values=["1", "15", "25", "30", "45", "50", "60", "90", "120"], width=80)
        self.opt_study.set("25")
        self.opt_study.grid(row=0, column=1, padx=10)
        
        ctk.CTkLabel(controls_frame, text="Break (min):", font=("Helvetica", 14)).grid(row=0, column=2, padx=10)
        self.opt_break = ctk.CTkOptionMenu(controls_frame, values=["1","5", "10", "15", "20", "30"], width=80)
        self.opt_break.set("5")
        self.opt_break.grid(row=0, column=3, padx=10)
        
        btn_frame = ctk.CTkFrame(timer_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))
        
        btn_study = ctk.CTkButton(btn_frame, text="Start Study", font=("Helvetica", 16, "bold"), fg_color="#FF7675", hover_color="#D63031", command=lambda: self.start_timer("Study"))
        btn_study.grid(row=0, column=0, padx=10)
        
        btn_break = ctk.CTkButton(btn_frame, text="Start Break", font=("Helvetica", 16, "bold"), fg_color="#74B9FF", hover_color="#0984E3", command=lambda: self.start_timer("Break"))
        btn_break.grid(row=0, column=1, padx=10)
        
        # Added Stop Button for the continuous loop
        btn_stop = ctk.CTkButton(btn_frame, text="Stop Loop", font=("Helvetica", 16, "bold"), fg_color="#B2BEC3", hover_color="#636E72", command=self.stop_timer)
        btn_stop.grid(row=0, column=2, padx=10)
        
        tasks_label = ctk.CTkLabel(self.tab_timer, text="Daily Tasks", font=("Helvetica", 20, "bold"))
        tasks_label.pack(pady=(10, 5))
        
        input_frame = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        input_frame.pack(pady=5)
        
        self.task_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="What needs to be done?", font=("Helvetica", 14))
        self.task_entry.pack(side="left", padx=10)
        
        btn_add = ctk.CTkButton(input_frame, text="Add Task", font=("Helvetica", 14, "bold"), command=self.add_task)
        btn_add.pack(side="left")
        
        self.tasks_scroll = ctk.CTkScrollableFrame(self.tab_timer, width=500, height=200, corner_radius=10)
        self.tasks_scroll.pack(pady=10, fill="both", expand=True, padx=20)

    # ==============================
    # FLOATING TIMER & LOOP LOGIC
    # ==============================
    def create_mini_timer(self, mode):
        self.destroy_mini_timer()
        
        self.mini_window = ctk.CTkToplevel(self)
        self.mini_window.overrideredirect(True) 
        self.mini_window.attributes("-topmost", True) 
        self.mini_window.attributes("-toolwindow", True)
        
        window_width = 100
        window_height = 40
        x_pos = int((self.winfo_screenwidth() / 2) - (window_width / 2))
        y_pos = int(self.winfo_screenheight() - window_height - 50) 
        
        self.mini_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        
        bg_color = "#2D3436" 
        text_color = "#FF7675" if mode == "Study" else "#74B9FF"
        self.mini_window.configure(fg_color=bg_color)
        
        self.mini_lbl = ctk.CTkLabel(self.mini_window, text="00:00", font=("Helvetica", 24, "bold"), text_color=text_color, cursor="hand2")
        self.mini_lbl.pack(expand=True, fill="both")
        
        # Bind clicking the mini timer to restore the main window
        self.mini_lbl.bind("<Button-1>", self.restore_main_window)
        self.mini_window.bind("<Button-1>", self.restore_main_window)

    def restore_main_window(self, event=None):
        self.deiconify()          # Un-minimize if minimized
        self.lift()               # Bring to top of window stack
        self.focus_force()        # Force Windows to give it focus
        self.attributes('-topmost', True) # Flash it on top
        self.attributes('-topmost', False)

    def destroy_mini_timer(self):
        if self.mini_window is not None:
            self.mini_window.destroy()
            self.mini_window = None

    def start_timer(self, mode):
        if self.is_running: return
        self.current_mode = mode
        self.session_minutes = int(self.opt_study.get()) if mode == "Study" else int(self.opt_break.get())
        self.time_left = self.session_minutes * 60
        self.is_running = True
        
        color = "#FF7675" if mode == "Study" else "#74B9FF"
        self.lbl_timer.configure(text_color=color)
        
        self.create_mini_timer(mode)
        self.update_timer()

    def stop_timer(self):
        self.is_running = False
        self.lbl_timer.configure(text="00:00", text_color="#00CEC9")
        self.destroy_mini_timer()

    def update_timer(self):
        if self.is_running and self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            
            self.lbl_timer.configure(text=time_str)
            if hasattr(self, 'mini_lbl') and self.mini_lbl.winfo_exists():
                self.mini_lbl.configure(text=time_str)
                
            self.time_left -= 1
            self.after(1000, self.update_timer)
            
        elif self.time_left == 0 and self.is_running:
            self.is_running = False
            self.destroy_mini_timer()
            
            if self.current_mode == "Study":
                self.cursor.execute("UPDATE ledger SET study_minutes = study_minutes + ? WHERE date = ?", (self.session_minutes, self.today))
                self.conn.commit()
                self.load_dashboard_stats()
            
            # Bring window forward briefly to notify user of transition
            self.restore_main_window()
            
            # Determine the next mode and auto-start it
            next_mode = "Break" if self.current_mode == "Study" else "Study"
            self.start_timer(next_mode)

    # ==============================
    # TASKS LOGIC
    # ==============================
    def load_tasks(self):
        for widget in self.tasks_scroll.winfo_children():
            widget.destroy()
            
        self.cursor.execute("SELECT id, name, status FROM tasks WHERE date_added = ?", (self.today,))
        for task_id, name, status in self.cursor.fetchall():
            is_done = (status == "completed")
            
            cb = ctk.CTkCheckBox(
                self.tasks_scroll, text=name, font=("Helvetica", 14),
                text_color="gray" if is_done else "white",
                command=lambda t_id=task_id: self.complete_task(t_id)
            )
            cb.pack(anchor="w", pady=5, padx=10)
            
            if is_done:
                cb.select()
                cb.configure(state="disabled")

    def add_task(self):
        task_name = self.task_entry.get().strip()
        if task_name:
            self.cursor.execute("INSERT INTO tasks (name, status, date_added) VALUES (?, 'pending', ?)", (task_name, self.today))
            self.conn.commit()
            self.task_entry.delete(0, 'end')
            self.load_tasks()
            self.load_dashboard_stats()

    def complete_task(self, task_id):
        self.cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
        self.conn.commit()
        self.load_tasks()
        self.load_dashboard_stats()

if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()