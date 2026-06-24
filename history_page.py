import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_todays_bills, search_todays_bills, get_bill_details, get_settings
from receipt import generate_receipt
from print_helper import smart_print_receipt

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top Section: Search
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Search (Bill No / Customer):", font=ctk.CTkFont(family="Inter", size=14)).grid(row=0, column=0, padx=10, pady=10)
        self.entry_search = ctk.CTkEntry(search_frame, font=("Inter", 13))
        self.entry_search.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.entry_search.bind("<KeyRelease>", self.search_history)
        
        # Middle Section: Table
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        columns = ("bill_id", "customer_name", "time", "total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("bill_id", text="Bill No")
        self.tree.heading("customer_name", text="Customer Name")
        self.tree.heading("time", text="Time")
        self.tree.heading("total", text="Total (Rs)")
        
        self.tree.column("bill_id", width=100, anchor="center")
        self.tree.column("customer_name", width=300, anchor="w")
        self.tree.column("time", width=150, anchor="center")
        self.tree.column("total", width=150, anchor="e")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bottom Section: Total & Buttons
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_today_total = ctk.CTkLabel(bottom_frame, text="Today's Sales Total: Rs 0.00", font=ctk.CTkFont(family="Inter", size=22, weight="bold"), text_color="#1f538d")
        self.lbl_today_total.grid(row=0, column=0, sticky="w")
        
        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")
        
        self.btn_view_details = ctk.CTkButton(btn_frame, text="View Details / Reprint", command=self.view_details, corner_radius=8, height=40, font=("Inter", 14), fg_color="#1f538d", hover_color="#14375e")
        self.btn_view_details.pack(side="right", padx=10)
        
        self.refresh_data()

    def refresh_data(self):
        self.load_table_data()

    def load_table_data(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if data is None:
            data = get_todays_bills()
            
        total_sales = 0.0
        for row in data:
            self.tree.insert("", "end", values=(
                row['bill_id'], 
                row['customer_name'], 
                row['bill_time'], 
                f"{row['total_amount']:.2f}"
            ))
            total_sales += float(row['total_amount'])
            
        self.lbl_today_total.configure(text=f"Today's Sales Total: Rs {total_sales:.2f}")

    def search_history(self, event):
        query = self.entry_search.get()
        if query:
            data = search_todays_bills(query)
            self.load_table_data(data)
        else:
            self.load_table_data()

    def view_details(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a bill from the table.")
            return
            
        item = self.tree.item(selected[0])
        bill_id = item['values'][0]
        
        details = get_bill_details(bill_id)
        if not details:
            messagebox.showerror("Error", "Bill details not found.")
            return
            
        info = details['info']
        items = details['items']
        
        # Create a popup window to show details
        popup = ctk.CTkToplevel(self)
        popup.title(f"Bill Details - #{bill_id}")
        popup.geometry("400x500")
        
        # Make popup modal
        popup.grab_set()
        
        scrollable_frame = ctk.CTkScrollableFrame(popup)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(scrollable_frame, text=f"Bill No: {info['bill_id']}", font=ctk.CTkFont(family="Inter", size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(scrollable_frame, text=f"Date: {info['bill_date']}   Time: {info['bill_time']}", font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="w")
        ctk.CTkLabel(scrollable_frame, text=f"Customer: {info['customer_name']}", font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="w")
        ctk.CTkLabel(scrollable_frame, text=f"Phone: {info['phone']}", font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="w")
        ctk.CTkLabel(scrollable_frame, text=f"Address: {info['address']}", font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="w", pady=(0, 10))
        
        for idx, i in enumerate(items, 1):
            item_text = f"{idx}. {i['item_name']} - Rs {i['price']} x {i['quantity']} = Rs {i['subtotal']}"
            ctk.CTkLabel(scrollable_frame, text=item_text, font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="w")
            
        if float(info.get('delivery_charge', 0)) > 0 or float(info.get('service_charge', 0)) > 0:
            ctk.CTkLabel(scrollable_frame, text=f"Subtotal: Rs {info.get('subtotal_amount', 0):.2f}", font=ctk.CTkFont(family="Inter", size=13, weight="bold")).pack(anchor="e", pady=(10, 0))
            if float(info.get('delivery_charge', 0)) > 0:
                ctk.CTkLabel(scrollable_frame, text=f"Delivery Charge: Rs {info.get('delivery_charge', 0):.2f}", font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="e")
            if float(info.get('service_charge', 0)) > 0:
                ctk.CTkLabel(scrollable_frame, text=f"Service Charge: Rs {info.get('service_charge', 0):.2f}", font=ctk.CTkFont(family="Inter", size=13)).pack(anchor="e")
                
        ctk.CTkLabel(scrollable_frame, text=f"Grand Total: Rs {info['total_amount']:.2f}", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#1f538d").pack(anchor="e", pady=(10, 0))
        
        def reprint():
            settings = get_settings()
            cust_info = {
                'customer_name': info['customer_name'],
                'phone': info['phone'],
                'address': info['address']
            }
            try:
                filepath = generate_receipt(
                    info['bill_id'], info['bill_date'], info['bill_time'],
                    cust_info, items, info.get('subtotal_amount', info['total_amount']),
                    info['total_amount'], settings,
                    delivery_charge=info.get('delivery_charge', 0),
                    service_charge=info.get('service_charge', 0)
                )
                
                # Smart printing fallback
                smart_print_receipt(filepath, popup)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reprint PDF: {e}", parent=popup)
                
        ctk.CTkButton(popup, text="Reprint Receipt", command=reprint, corner_radius=8, height=40, font=("Inter", 14), fg_color="#28a745", hover_color="#218838").pack(pady=15)
