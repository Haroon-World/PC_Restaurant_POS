import os
import subprocess
import customtkinter as ctk
from tkinter import messagebox

def smart_print_receipt(filepath, parent_window):
    """
    Attempts to print the receipt using the default printer.
    If no printer is found or printing fails, falls back to a PDF-only popup.
    """
    printer_available = False
    
    try:
        # Check if a default printer exists
        # CREATE_NO_WINDOW = 0x08000000 to prevent console flashing
        result = subprocess.run(
            ["wmic", "printer", "where", "default='True'", "get", "name"],
            capture_output=True, text=True, creationflags=0x08000000
        )
        output = result.stdout.strip()
        # wmic output has a header line "Name" and then the printer name.
        if result.returncode == 0 and len(output.split('\n')) > 1:
            printer_available = True
    except Exception:
        # If wmic fails for any reason, assume no printer
        printer_available = False

    def show_fallback():
        popup = ctk.CTkToplevel(parent_window)
        popup.title("No Printer Detected")
        popup.geometry("350x200")
        
        # Make the popup appear on top
        popup.attributes('-topmost', True)
        popup.grab_set()
        
        # Force update geometry
        popup.update()
        
        msg = f"No printer detected. Receipt saved as PDF.\nLocation: {filepath}"
        lbl = ctk.CTkLabel(popup, text=msg, justify="center", wraplength=300, font=ctk.CTkFont(family="Inter", size=13))
        lbl.pack(pady=30, padx=20)
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        def open_pdf():
            try:
                os.startfile(os.path.abspath(filepath))
            except Exception:
                pass
            popup.grab_release()
            popup.destroy()
            
        def close_popup():
            popup.grab_release()
            popup.destroy()
            
        btn_open = ctk.CTkButton(btn_frame, text="Open Receipt", command=open_pdf, corner_radius=8, fg_color="#1f538d", hover_color="#14375e")
        btn_open.pack(side="left", padx=10, expand=True)
        
        btn_close = ctk.CTkButton(btn_frame, text="Close", command=close_popup, corner_radius=8, fg_color="#6c757d", hover_color="#5a6268")
        btn_close.pack(side="right", padx=10, expand=True)

    if printer_available:
        try:
            os.startfile(os.path.abspath(filepath), "print")
            messagebox.showinfo("Success", "Receipt sent to printer successfully", parent=parent_window)
        except Exception:
            # If startfile fails (e.g. no PDF reader registered with print verb), fallback quietly
            show_fallback()
    else:
        show_fallback()
