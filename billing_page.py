import customtkinter as ctk
from tkinter import messagebox, ttk
import os
from PIL import Image
from database import get_settings, get_menu_items, save_bill
from receipt import generate_receipt
from print_helper import smart_print_receipt

class BillingPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.current_items = []  # List of dicts: {'item_name': 'x', 'price': 10.0, 'quantity': 1, 'subtotal': 10.0}
        self.grand_total = 0.0
        
        self.setup_header()
        self.setup_customer_info()
        self.setup_menu_selection()
        self.setup_order_table()
        self.setup_buttons()
        
        self.refresh_data()

    def refresh_data(self):
        """Called when tab is opened to refresh settings and menu"""
        self.settings = get_settings()
        
        # Update header
        self.lbl_rest_name.configure(text=self.settings.get('restaurant_name', 'Restaurant Name'))
        self.lbl_rest_address.configure(text=self.settings.get('address', 'Address'))
        self.lbl_rest_phone.configure(text=f"Phone: {self.settings.get('phone', 'Phone')}")
        
        logo_path = self.settings.get('logo_path', '')
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
                self.lbl_logo.configure(image=ctk_img, text="")
                self.lbl_logo.image = ctk_img
            except:
                self.lbl_logo.configure(image="", text="[LOGO]")
        else:
            self.lbl_logo.configure(image="", text="[LOGO]")
            
        # Update menu dropdown
        self.menu_data = get_menu_items()
        self.menu_dict = {item['item_name']: item['price'] for item in self.menu_data}
        menu_names = list(self.menu_dict.keys())
        
        # Update charge entries with defaults
        self.entry_delivery_charge.delete(0, 'end')
        self.entry_delivery_charge.insert(0, str(self.settings.get('default_delivery_charge', 0.0)))
        self.entry_service_charge.delete(0, 'end')
        self.entry_service_charge.insert(0, str(self.settings.get('default_service_charge', 0.0)))
        
        if menu_names:
            self.combo_menu.configure(values=menu_names)
            self.combo_menu.set(menu_names[0])
            self.update_price_display(menu_names[0])
        else:
            self.combo_menu.configure(values=["No items available"])
            self.combo_menu.set("No items available")
            self.lbl_current_price.configure(text="Rs 0.00")
            
        self.update_order_table()

    def setup_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        
        self.lbl_logo = ctk.CTkLabel(header_frame, text="[LOGO]", width=80, height=80, corner_radius=10, fg_color="gray20")
        self.lbl_logo.pack(side="left", padx=10)
        
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=10)
        
        self.lbl_rest_name = ctk.CTkLabel(info_frame, text="Restaurant Name", font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="#1f538d")
        self.lbl_rest_name.pack(anchor="w", pady=(0, 5))
        self.lbl_rest_address = ctk.CTkLabel(info_frame, text="Address", font=ctk.CTkFont(family="Inter", size=14))
        self.lbl_rest_address.pack(anchor="w")
        self.lbl_rest_phone = ctk.CTkLabel(info_frame, text="Phone", font=ctk.CTkFont(family="Inter", size=14))
        self.lbl_rest_phone.pack(anchor="w")

    def setup_customer_info(self):
        cust_frame = ctk.CTkFrame(self)
        cust_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        ctk.CTkLabel(cust_frame, text="Customer Information", font=ctk.CTkFont(family="Inter", size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=15)
        
        ctk.CTkLabel(cust_frame, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_cust_name = ctk.CTkEntry(cust_frame, width=200)
        self.entry_cust_name.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(cust_frame, text="Phone:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_cust_phone = ctk.CTkEntry(cust_frame, width=200)
        self.entry_cust_phone.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(cust_frame, text="Address:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry_cust_address = ctk.CTkEntry(cust_frame, width=200)
        self.entry_cust_address.grid(row=3, column=1, padx=10, pady=5)

    def setup_menu_selection(self):
        menu_frame = ctk.CTkFrame(self)
        menu_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        
        ctk.CTkLabel(menu_frame, text="Add Menu Item", font=ctk.CTkFont(family="Inter", size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=15)
        
        ctk.CTkLabel(menu_frame, text="Item:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.combo_menu = ctk.CTkComboBox(menu_frame, values=[], width=200, command=self.update_price_display)
        self.combo_menu.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(menu_frame, text="Price:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lbl_current_price = ctk.CTkLabel(menu_frame, text="Rs 0.00")
        self.lbl_current_price.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(menu_frame, text="Qty:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.entry_qty = ctk.CTkEntry(menu_frame, width=100)
        self.entry_qty.insert(0, "1")
        self.entry_qty.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.btn_add_to_bill = ctk.CTkButton(menu_frame, text="Add to Bill", command=self.add_to_bill, corner_radius=8, height=35, font=("Inter", 13), fg_color="#1f538d", hover_color="#14375e")
        self.btn_add_to_bill.grid(row=4, column=0, columnspan=2, pady=20)

    def update_price_display(self, choice):
        if hasattr(self, 'menu_dict') and choice in self.menu_dict:
            price = self.menu_dict[choice]
            self.lbl_current_price.configure(text=f"Rs {price:.2f}")

    def add_to_bill(self):
        item_name = self.combo_menu.get()
        if not hasattr(self, 'menu_dict') or item_name not in self.menu_dict:
            messagebox.showwarning("Error", "Invalid menu item selected.")
            return
            
        try:
            qty = int(self.entry_qty.get())
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Quantity must be a positive integer.")
            return
            
        price = self.menu_dict[item_name]
        subtotal = price * qty
        
        # Check if item already in bill, if so, just update quantity
        found = False
        for item in self.current_items:
            if item['item_name'] == item_name:
                item['quantity'] += qty
                item['subtotal'] += subtotal
                found = True
                break
                
        if not found:
            self.current_items.append({
                'item_name': item_name,
                'price': price,
                'quantity': qty,
                'subtotal': subtotal
            })
            
        self.update_order_table()
        self.entry_qty.delete(0, 'end')
        self.entry_qty.insert(0, "1")

    def setup_order_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        
        columns = ("item_name", "price", "quantity", "subtotal")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("price", text="Price (Rs)")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("subtotal", text="Subtotal (Rs)")
        
        self.tree.column("item_name", width=300, anchor="w")
        self.tree.column("price", width=100, anchor="center")
        self.tree.column("quantity", width=100, anchor="center")
        self.tree.column("subtotal", width=150, anchor="e")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Charges and Total Frame
        totals_frame = ctk.CTkFrame(self, fg_color="transparent")
        totals_frame.grid(row=3, column=1, sticky="e", padx=20, pady=5)
        
        ctk.CTkLabel(totals_frame, text="Delivery Charge (Rs):", font=ctk.CTkFont(family="Inter", size=14)).grid(row=0, column=0, padx=10, pady=2, sticky="e")
        self.entry_delivery_charge = ctk.CTkEntry(totals_frame, width=100)
        self.entry_delivery_charge.insert(0, "0.0")
        self.entry_delivery_charge.grid(row=0, column=1, padx=10, pady=2)
        self.entry_delivery_charge.bind("<KeyRelease>", lambda e: self.update_order_table())
        
        ctk.CTkLabel(totals_frame, text="Service Charge (Rs):", font=ctk.CTkFont(family="Inter", size=14)).grid(row=1, column=0, padx=10, pady=2, sticky="e")
        self.entry_service_charge = ctk.CTkEntry(totals_frame, width=100)
        self.entry_service_charge.insert(0, "0.0")
        self.entry_service_charge.grid(row=1, column=1, padx=10, pady=2)
        self.entry_service_charge.bind("<KeyRelease>", lambda e: self.update_order_table())
        
        self.lbl_grand_total = ctk.CTkLabel(totals_frame, text="Grand Total: Rs 0.00", font=ctk.CTkFont(family="Inter", size=22, weight="bold"), text_color="#1f538d")
        self.lbl_grand_total.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="e")

    def update_order_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.subtotal_amount = 0.0
        for item in self.current_items:
            self.tree.insert("", "end", values=(
                item['item_name'], 
                f"{item['price']:.2f}", 
                item['quantity'], 
                f"{item['subtotal']:.2f}"
            ))
            self.subtotal_amount += item['subtotal']
            
        try:
            del_charge = float(self.entry_delivery_charge.get().strip() or "0")
            srv_charge = float(self.entry_service_charge.get().strip() or "0")
        except ValueError:
            del_charge = 0.0
            srv_charge = 0.0
            
        self.grand_total = self.subtotal_amount + del_charge + srv_charge
        self.lbl_grand_total.configure(text=f"Grand Total: Rs {self.grand_total:.2f}")

    def setup_buttons(self):
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.btn_generate = ctk.CTkButton(btn_frame, text="Generate Receipt", command=self.process_generate_receipt, corner_radius=8, height=40, font=("Inter", 14), fg_color="#28a745", hover_color="#218838")
        self.btn_generate.pack(side="left", padx=15)
        
        self.btn_save = ctk.CTkButton(btn_frame, text="Save Bill", command=self.process_save_bill, corner_radius=8, height=40, font=("Inter", 14), fg_color="#1f538d", hover_color="#14375e")
        self.btn_save.pack(side="left", padx=15)
        
        self.btn_new = ctk.CTkButton(btn_frame, text="New Bill", command=self.clear_form, corner_radius=8, height=40, font=("Inter", 14), fg_color="#007bff", hover_color="#0069d9")
        self.btn_new.pack(side="left", padx=15)
        
        self.btn_clear = ctk.CTkButton(btn_frame, text="Clear Form", command=self.clear_form, corner_radius=8, height=40, font=("Inter", 14), fg_color="#dc3545", hover_color="#c82333")
        self.btn_clear.pack(side="left", padx=15)

    def clear_form(self):
        """Clears UI state without deleting DB data"""
        self.entry_cust_name.delete(0, 'end')
        self.entry_cust_phone.delete(0, 'end')
        self.entry_cust_address.delete(0, 'end')
        self.entry_qty.delete(0, 'end')
        self.entry_qty.insert(0, "1")
        
        self.current_items = []
        self.update_order_table()

    def process_save_bill(self):
        if not self.current_items:
            messagebox.showwarning("Error", "Bill is empty.")
            return None
            
        cust_name = self.entry_cust_name.get().strip() or "Walk-in Customer"
        cust_phone = self.entry_cust_phone.get().strip()
        cust_address = self.entry_cust_address.get().strip()
        
        if cust_phone and (not cust_phone.isdigit() or len(cust_phone) != 11):
            messagebox.showwarning("Validation Error", "Mobile number must be exactly 11 digits if provided.")
            return None
            
        try:
            del_charge = float(self.entry_delivery_charge.get().strip() or "0")
            srv_charge = float(self.entry_service_charge.get().strip() or "0")
        except ValueError:
            messagebox.showwarning("Validation Error", "Charges must be valid numbers.")
            return None
        
        try:
            bill_id, bill_date, bill_time = save_bill(
                cust_name, cust_phone, cust_address, 
                self.current_items, self.subtotal_amount,
                delivery_charge=del_charge, service_charge=srv_charge
            )
            messagebox.showinfo("Success", f"Bill #{bill_id} saved successfully.")
            return bill_id, bill_date, bill_time, del_charge, srv_charge
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save bill: {e}")
            return None

    def process_generate_receipt(self):
        result = self.process_save_bill()
        if result:
            bill_id, bill_date, bill_time, del_charge, srv_charge = result
            cust_info = {
                'customer_name': self.entry_cust_name.get().strip() or "Walk-in Customer",
                'phone': self.entry_cust_phone.get().strip(),
                'address': self.entry_cust_address.get().strip()
            }
            
            try:
                filepath = generate_receipt(
                    bill_id, bill_date, bill_time, 
                    cust_info, self.current_items, 
                    self.subtotal_amount, self.grand_total, self.settings,
                    delivery_charge=del_charge, service_charge=srv_charge
                )
                
                # Smart printing fallback
                smart_print_receipt(filepath, self)
                
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate PDF: {e}")
