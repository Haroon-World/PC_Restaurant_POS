import customtkinter as ctk
from tkinter import messagebox
import sys

from database import initialize_database
from cleanup import perform_daily_cleanup
from settings_page import SettingsPage
from menu_page import MenuPage
from billing_page import BillingPage
from history_page import HistoryPage


NAV_ITEMS = [
    ("billing",  "🧾  Billing",        None),
    ("menu",     "🍽  Menu",           None),
    ("history",  "📋  Today's History", None),
    ("settings", "⚙  Settings",        None),
]

ACTIVE_COLOR   = "#1f538d"
INACTIVE_COLOR = "transparent"
SIDEBAR_BG     = "#111827"  # very dark navy


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Restaurant POS System")
        self.geometry("1100x720")
        self.minsize(900, 600)

        # ── Global ttk dark theme ─────────────────────────────────────────
        from tkinter import ttk
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#1e1e2e",
            foreground="#e2e8f0",
            rowheight=36,
            fieldbackground="#1e1e2e",
            bordercolor="#2d3748",
            borderwidth=0,
            font=("Inter", 11),
        )
        style.map("Treeview", background=[("selected", "#1f538d")])
        style.configure(
            "Treeview.Heading",
            background="#111827",
            foreground="#a0aec0",
            relief="flat",
            font=("Inter", 12, "bold"),
            padding=10,
        )
        style.map("Treeview.Heading", background=[("active", "#2d3748")])

        # ── Layout: sidebar + content ─────────────────────────────────────
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ───────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(len(NAV_ITEMS) + 2, weight=1)

        # Brand logo text
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="#1f2937", corner_radius=0)
        brand_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        brand_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            brand_frame,
            text="🍴",
            font=ctk.CTkFont(family="Inter", size=32),
        ).grid(row=0, column=0, pady=(20, 4))

        ctk.CTkLabel(
            brand_frame,
            text="Restaurant POS",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#60a5fa",
        ).grid(row=1, column=0, pady=(0, 20))

        # Navigation buttons
        self._nav_buttons = {}
        for i, (name, label, _) in enumerate(NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda n=name: self.select_frame_by_name(n),
                corner_radius=8,
                height=44,
                font=("Inter", 14),
                anchor="w",
                fg_color=INACTIVE_COLOR,
                hover_color="#1e3a5f",
                text_color="#cbd5e0",
            )
            btn.grid(row=i, column=0, padx=14, pady=4, sticky="ew")
            self._nav_buttons[name] = btn

        # Footer / version label at bottom of sidebar
        ctk.CTkLabel(
            self.sidebar,
            text="v1.0  •  Restaurant POS",
            font=ctk.CTkFont(family="Inter", size=10),
            text_color="#374151",
        ).grid(row=len(NAV_ITEMS) + 3, column=0, pady=(10, 14))

        # ── Pages ─────────────────────────────────────────────────────────
        self.pages = {}
        self.pages["billing"]  = BillingPage(self,  corner_radius=0, fg_color="transparent")
        self.pages["menu"]     = MenuPage(self,     corner_radius=0, fg_color="transparent")
        self.pages["history"]  = HistoryPage(self,  corner_radius=0, fg_color="transparent")
        self.pages["settings"] = SettingsPage(self, corner_radius=0, fg_color="transparent")

        # Start on billing page
        self.select_frame_by_name("billing")

    # ── Navigation ────────────────────────────────────────────────────────────
    def select_frame_by_name(self, name: str):
        for page_name, btn in self._nav_buttons.items():
            if page_name == name:
                btn.configure(
                    fg_color=ACTIVE_COLOR,
                    text_color="white",
                    font=("Inter", 14, "bold"),
                )
            else:
                btn.configure(
                    fg_color=INACTIVE_COLOR,
                    text_color="#cbd5e0",
                    font=("Inter", 14),
                )

        for page_name, frame in self.pages.items():
            if page_name == name:
                frame.grid(row=0, column=1, sticky="nsew")
                if hasattr(frame, "refresh_data"):
                    frame.refresh_data()
            else:
                frame.grid_forget()

    def show_billing_page(self):   self.select_frame_by_name("billing")
    def show_menu_page(self):      self.select_frame_by_name("menu")
    def show_history_page(self):   self.select_frame_by_name("history")
    def show_settings_page(self):  self.select_frame_by_name("settings")


def main():
    try:
        initialize_database()
        perform_daily_cleanup()
    except Exception as e:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Error",
            f"Database Error occurred. Please restart the application.\nDetails: {e}",
        )
        root.destroy()
        sys.exit(1)

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
