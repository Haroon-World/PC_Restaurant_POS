# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys
import shutil
from PIL import Image
from database import get_settings, save_settings


def _get_app_dir():
    """Returns the directory next to the EXE (or script during dev)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.logo_path = ""

        # ── Scrollable content area ──────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(0, weight=1)
        self.scroll.grid_columnconfigure(0, weight=1)

        # ── Page Title ───────────────────────────────────────────────────────
        title_frame = ctk.CTkFrame(self.scroll, fg_color="#1f538d", corner_radius=12)
        title_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 20))
        title_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_frame,
            text="⚙  Restaurant Settings",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color="white",
        ).grid(row=0, column=0, pady=18)

        # ── Logo Section Card ─────────────────────────────────────────────
        logo_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e1e2e")
        logo_card.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 15))
        logo_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            logo_card,
            text="Restaurant Logo",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color="#a0aec0",
        ).grid(row=0, column=0, pady=(15, 8))

        self.logo_preview_label = ctk.CTkLabel(
            logo_card,
            text="📷  No Logo Selected",
            width=140, height=140,
            corner_radius=70,
            fg_color="#2d2d44",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#718096",
        )
        self.logo_preview_label.grid(row=1, column=0, pady=(0, 12))

        self.btn_choose_logo = ctk.CTkButton(
            logo_card,
            text="📁  Choose Logo",
            command=self.choose_logo,
            corner_radius=20,
            height=36,
            font=("Inter", 13),
            fg_color="#2b5797",
            hover_color="#1a3d6e",
            width=180,
        )
        self.btn_choose_logo.grid(row=2, column=0, pady=(0, 18))

        # ── Info Section Card ─────────────────────────────────────────────
        info_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e1e2e")
        info_card.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 15))
        info_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            info_card,
            text="🏪  Restaurant Information",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color="#a0aec0",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 10))

        fields = [
            ("Restaurant Name:", "entry_name", "e.g. Seaview Grill"),
            ("Phone Number:", "entry_phone", "e.g. 03001234567"),
            ("Address:", "entry_address", "e.g. 123 Main Street"),
        ]
        for i, (label, attr, placeholder) in enumerate(fields, start=1):
            ctk.CTkLabel(
                info_card,
                text=label,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#cbd5e0",
            ).grid(row=i, column=0, padx=(20, 10), pady=8, sticky="e")

            entry = ctk.CTkEntry(
                info_card,
                placeholder_text=placeholder,
                width=320,
                height=38,
                font=("Inter", 13),
                corner_radius=8,
                border_color="#3a3a5c",
                fg_color="#2d2d44",
            )
            entry.grid(row=i, column=1, padx=(0, 20), pady=8, sticky="w")
            setattr(self, attr, entry)

        # Extra padding at bottom
        ctk.CTkLabel(info_card, text="").grid(row=len(fields)+1, column=0)

        # ── Charges Section Card ──────────────────────────────────────────
        charge_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e1e2e")
        charge_card.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 15))
        charge_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            charge_card,
            text="💰  Default Charges",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color="#a0aec0",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 10))

        charges = [
            ("Delivery Charge (Rs):", "entry_delivery", "0.00"),
            ("Service Charge (Rs):", "entry_service", "0.00"),
        ]
        for i, (label, attr, placeholder) in enumerate(charges, start=1):
            ctk.CTkLabel(
                charge_card,
                text=label,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#cbd5e0",
            ).grid(row=i, column=0, padx=(20, 10), pady=8, sticky="e")

            entry = ctk.CTkEntry(
                charge_card,
                placeholder_text=placeholder,
                width=200,
                height=38,
                font=("Inter", 13),
                corner_radius=8,
                border_color="#3a3a5c",
                fg_color="#2d2d44",
            )
            entry.grid(row=i, column=1, padx=(0, 20), pady=8, sticky="w")
            setattr(self, attr, entry)

        ctk.CTkLabel(charge_card, text="").grid(row=len(charges)+1, column=0)

        # ── Custom Receipt Message Card ───────────────────────────────────
        msg_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e1e2e")
        msg_card.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 15))
        msg_card.grid_columnconfigure(0, weight=1)

        msg_header = ctk.CTkFrame(msg_card, fg_color="transparent")
        msg_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 6))
        msg_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            msg_header,
            text="💬  Custom Receipt Message",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color="#a0aec0",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            msg_card,
            text="This message will be printed at the bottom of every receipt.\n"
                 "Supports any language: English, اردو, 中文, etc.",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#718096",
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 8))

        self.text_receipt_msg = ctk.CTkTextbox(
            msg_card,
            width=500,
            height=90,
            font=("Inter", 13),
            corner_radius=8,
            border_color="#3a3a5c",
            fg_color="#2d2d44",
            text_color="#e2e8f0",
            border_width=1,
        )
        self.text_receipt_msg.grid(row=2, column=0, padx=20, pady=(0, 6), sticky="ew")

        # Default message hint
        self.lbl_default_hint = ctk.CTkLabel(
            msg_card,
            text='Default (when empty): "Thank You For Visiting"',
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#4a5568",
        )
        self.lbl_default_hint.grid(row=3, column=0, padx=20, pady=(0, 18), sticky="w")

        # ── Save Button ────────────────────────────────────────────────────
        self.btn_save = ctk.CTkButton(
            self.scroll,
            text="💾  Save Settings",
            command=self.save_data,
            corner_radius=10,
            height=46,
            font=("Inter", 15, "bold"),
            fg_color="#28a745",
            hover_color="#218838",
            width=260,
        )
        self.btn_save.grid(row=5, column=0, pady=(5, 30))

        self.load_settings()

    # ── Data Methods ─────────────────────────────────────────────────────────

    def load_settings(self):
        settings = get_settings()
        if settings:
            self.entry_name.insert(0, settings.get('restaurant_name', ''))
            self.entry_phone.insert(0, settings.get('phone', ''))
            self.entry_address.insert(0, settings.get('address', ''))
            self.entry_delivery.insert(0, str(settings.get('default_delivery_charge', 0.0)))
            self.entry_service.insert(0, str(settings.get('default_service_charge', 0.0)))
            self.logo_path = settings.get('logo_path', '')
            self.update_logo_preview()

            # Load custom receipt message
            msg = settings.get('custom_receipt_message', '')
            if msg:
                self.text_receipt_msg.insert("1.0", msg)

    def choose_logo(self):
        file_path = filedialog.askopenfilename(
            title="Select Logo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            assets_dir = os.path.join(_get_app_dir(), "assets", "logos")
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)

            filename = os.path.basename(file_path)
            dest_path = os.path.join(assets_dir, filename)

            try:
                shutil.copy(file_path, dest_path)
                self.logo_path = dest_path
                self.update_logo_preview()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logo: {e}")

    def update_logo_preview(self):
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                img = Image.open(self.logo_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(140, 140))
                self.logo_preview_label.configure(image=ctk_img, text="")
                self.logo_preview_label.image = ctk_img
            except Exception:
                self.logo_preview_label.configure(text="⚠ Error loading image", image="")
        else:
            self.logo_preview_label.configure(text="📷  No Logo Selected", image="")

    def save_data(self):
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        address = self.entry_address.get().strip()
        delivery = self.entry_delivery.get().strip() or "0"
        service = self.entry_service.get().strip() or "0"

        # Get custom receipt message (strip trailing newlines)
        custom_message = self.text_receipt_msg.get("1.0", "end").strip()

        if not name:
            messagebox.showwarning("Validation Error", "Restaurant Name is required.")
            return

        try:
            delivery_val = float(delivery)
            service_val = float(service)
        except ValueError:
            messagebox.showwarning("Validation Error", "Charges must be valid numbers.")
            return

        try:
            save_settings(name, address, phone, self.logo_path, delivery_val, service_val, custom_message)
            # Visual feedback: temporarily change button
            self.btn_save.configure(text="✅  Saved!", fg_color="#155724")
            self.after(2000, lambda: self.btn_save.configure(text="💾  Save Settings", fg_color="#28a745"))
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
