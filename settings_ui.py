import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
import threading

BG_COLOR = "#080A0F"
ACCENT_COLOR = "#E8FF47"
TEXT_COLOR = "#FFFFFF"
MUTED_TEXT = "#A0A0A0"
PANEL_BG = "#12151E"

class SettingsWindow:
    def __init__(self, config, config_lock, save_callback, reload_packs_callback, get_available_packs_func):
        self.config = config
        self.config_lock = config_lock
        self.save_callback = save_callback
        self.reload_packs_callback = reload_packs_callback
        self.get_available_packs = get_available_packs_func

        self.root = tk.Tk()
        self.root.title("TantuSpank Settings")
        self.root.geometry("400x500")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.attributes("-topmost", True)

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Panel.TFrame", background=PANEL_BG)
        
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_COLOR)
        style.configure("Sub.TLabel", foreground=MUTED_TEXT, font=("Segoe UI", 9))
        style.configure("Panel.TLabel", background=PANEL_BG, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        
        style.configure("Accent.TButton", background=ACCENT_COLOR, foreground="#000000", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=5)
        style.map("Accent.TButton", background=[("active", "#D4E83D")])

        style.configure("TCombobox", fieldbackground=PANEL_BG, background=PANEL_BG, foreground=TEXT_COLOR, selectbackground=ACCENT_COLOR, selectforeground="#000")
        
    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        ttk.Label(main_frame, text="TantuSpank Configuration", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(main_frame, text="Adjust how the application responds to your spanks.", style="Sub.TLabel").pack(anchor=tk.W, pady=(0, 20))

        # Settings Panel
        panel = ttk.Frame(main_frame, style="Panel.TFrame", padding=15)
        panel.pack(fill=tk.X, pady=(0, 20))

        # -- Sensitivity
        ttk.Label(panel, text="Sensitivity (%)", style="Panel.TLabel").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.sens_var = tk.DoubleVar()
        with self.config_lock:
            self.sens_var.set(self.config.get("sensitivity", 0.50) * 100)
        
        # We use a standard scale but style it minimally
        self.sens_scale = tk.Scale(panel, variable=self.sens_var, from_=0, to=100, orient=tk.HORIZONTAL, 
                                   bg=PANEL_BG, fg=TEXT_COLOR, highlightthickness=0, troughcolor=BG_COLOR, 
                                   activebackground=ACCENT_COLOR, sliderrelief=tk.FLAT, length=150)
        self.sens_scale.grid(row=0, column=1, sticky=tk.E, pady=10)

        # -- Volume
        ttk.Label(panel, text="Global Volume (%)", style="Panel.TLabel").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.vol_var = tk.DoubleVar()
        with self.config_lock:
            self.vol_var.set(self.config.get("global_volume", 1.0) * 100)
        
        self.vol_scale = tk.Scale(panel, variable=self.vol_var, from_=0, to=100, orient=tk.HORIZONTAL, 
                                  bg=PANEL_BG, fg=TEXT_COLOR, highlightthickness=0, troughcolor=BG_COLOR, 
                                  activebackground=ACCENT_COLOR, sliderrelief=tk.FLAT, length=150)
        self.vol_scale.grid(row=1, column=1, sticky=tk.E, pady=10)

        # -- Cooldown
        ttk.Label(panel, text="Cooldown (ms)", style="Panel.TLabel").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.cd_var = tk.StringVar()
        with self.config_lock:
            self.cd_var.set(str(self.config.get("cooldown_ms", 300)))
        
        self.cd_combo = ttk.Combobox(panel, textvariable=self.cd_var, values=["0", "150", "300", "500", "1000", "2000", "5000"], width=10, state="readonly")
        self.cd_combo.grid(row=2, column=1, sticky=tk.E, pady=10)

        # -- Current Pack
        ttk.Label(panel, text="Current Sound Pack", style="Panel.TLabel").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.pack_var = tk.StringVar()
        with self.config_lock:
            self.pack_var.set(self.config.get("last_used_pack", "pack_default"))
        
        packs = self.get_available_packs()
        self.pack_combo = ttk.Combobox(panel, textvariable=self.pack_var, values=packs, width=15, state="readonly")
        self.pack_combo.grid(row=3, column=1, sticky=tk.E, pady=10)

        # Bottom Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        save_btn = ttk.Button(btn_frame, text="SAVE & APPLY", style="Accent.TButton", command=self.save)
        save_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = tk.Button(btn_frame, text="CANCEL", bg=BG_COLOR, fg=MUTED_TEXT, borderwidth=0, activebackground=BG_COLOR, activeforeground=TEXT_COLOR, font=("Segoe UI", 10), cursor="hand2", command=self.root.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=15)

    def save(self):
        with self.config_lock:
            self.config["sensitivity"] = self.sens_var.get() / 100.0
            self.config["global_volume"] = self.vol_var.get() / 100.0
            self.config["cooldown_ms"] = int(self.cd_var.get())
            pack_name = self.pack_var.get()
            
        # Call the save callback
        self.save_callback()
        
        # Load the new pack if changed
        self.reload_packs_callback(pack_name)
        
        self.root.destroy()

def open_settings_window(config, config_lock, save_callback, reload_packs_callback, get_available_packs_func):
    app = SettingsWindow(config, config_lock, save_callback, reload_packs_callback, get_available_packs_func)
    app.root.mainloop()
