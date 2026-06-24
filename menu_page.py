import customtkinter as ctk
from tkinter import messagebox, ttk
from database import get_menu_items, add_menu_item, update_menu_item, delete_menu_item, search_menu_items

class MenuPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Top Section: Form
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        self.form_frame.grid_columnconfigure(1, weight=1)
        self.form_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(self.form_frame, text="Item Name:", font=ctk.CTkFont(family="Inter", size=14)).grid(row=0, column=0, padx=10, pady=10)
        self.entry_name = ctk.CTkEntry(self.form_frame)
        self.entry_name.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(self.form_frame, text="Price (Rs):", font=ctk.CTkFont(family="Inter", size=14)).grid(row=0, column=2, padx=10, pady=10)
        self.entry_price = ctk.CTkEntry(self.form_frame)
        self.entry_price.grid(row=0, column=3, sticky="ew", padx=10, pady=10)
        
        self.btn_add = ctk.CTkButton(self.form_frame, text="Add Item", command=self.add_item, corner_radius=8, height=35, font=("Inter", 13), fg_color="#28a745", hover_color="#218838")
        self.btn_add.grid(row=0, column=4, padx=10, pady=10)
        
        self.btn_update = ctk.CTkButton(self.form_frame, text="Update Item", command=self.update_item, state="disabled", corner_radius=8, height=35, font=("Inter", 13), fg_color="#1f538d", hover_color="#14375e")
        self.btn_update.grid(row=0, column=5, padx=10, pady=10)
        
        self.btn_clear = ctk.CTkButton(self.form_frame, text="Clear", command=self.clear_form, corner_radius=8, height=35, font=("Inter", 13), fg_color="#6c757d", hover_color="#5a6268")
        self.btn_clear.grid(row=0, column=6, padx=10, pady=10)
        
        # Middle Section: Search & Delete
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.action_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.action_frame, text="Search:", font=ctk.CTkFont(family="Inter", size=14)).grid(row=0, column=0, padx=10, pady=10)
        self.entry_search = ctk.CTkEntry(self.action_frame)
        self.entry_search.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.entry_search.bind("<KeyRelease>", self.search_items)
        
        self.btn_delete = ctk.CTkButton(self.action_frame, text="Delete Selected", command=self.delete_item, state="disabled", corner_radius=8, height=35, font=("Inter", 13), fg_color="#dc3545", hover_color="#c82333")
        self.btn_delete.grid(row=0, column=2, padx=10, pady=10)
        
        # Bottom Section: Table
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        
        # We use ttk.Treeview for the table as CustomTkinter doesn't have a built-in data table
        columns = ("id", "item_name", "price")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("price", text="Price (Rs)")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("item_name", width=300, anchor="w")
        self.tree.column("price", width=150, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        self.selected_item_id = None
        
        self.load_table_data()

    def clear_form(self):
        self.entry_name.delete(0, 'end')
        self.entry_price.delete(0, 'end')
        self.selected_item_id = None
        self.btn_add.configure(state="normal")
        self.btn_update.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        self.tree.selection_remove(self.tree.selection())

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.selected_item_id = item['values'][0]
            name = item['values'][1]
            price = item['values'][2]
            
            self.entry_name.delete(0, 'end')
            self.entry_name.insert(0, name)
            
            self.entry_price.delete(0, 'end')
            self.entry_price.insert(0, str(price))
            
            self.btn_add.configure(state="disabled")
            self.btn_update.configure(state="normal")
            self.btn_delete.configure(state="normal")

    def load_table_data(self, data=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if data is None:
            data = get_menu_items()
            
        for row in data:
            self.tree.insert("", "end", values=(row['id'], row['item_name'], f"{row['price']:.2f}"))

    def search_items(self, event):
        query = self.entry_search.get()
        if query:
            data = search_menu_items(query)
            self.load_table_data(data)
        else:
            self.load_table_data()

    def add_item(self):
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        
        if not name or not price_str:
            messagebox.showwarning("Validation Error", "All fields are required.")
            return
            
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showwarning("Validation Error", "Price must be a valid number.")
            return
            
        success, msg = add_menu_item(name, price)
        if success:
            self.clear_form()
            self.load_table_data()
        else:
            messagebox.showerror("Error", msg)

    def update_item(self):
        if not self.selected_item_id:
            return
            
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        
        if not name or not price_str:
            messagebox.showwarning("Validation Error", "All fields are required.")
            return
            
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showwarning("Validation Error", "Price must be a valid number.")
            return
            
        success, msg = update_menu_item(self.selected_item_id, name, price)
        if success:
            self.clear_form()
            self.load_table_data()
        else:
            messagebox.showerror("Error", msg)

    def delete_item(self):
        if not self.selected_item_id:
            return
            
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?")
        if confirm:
            success, msg = delete_menu_item(self.selected_item_id)
            if success:
                self.clear_form()
                self.load_table_data()
            else:
                messagebox.showerror("Error", msg)
