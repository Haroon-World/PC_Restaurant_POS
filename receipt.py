import os
import sys
from reportlab.pdfgen import canvas


def _get_app_dir():
    """Returns the directory next to the EXE (or script during dev)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


RECEIPTS_DIR = os.path.join(_get_app_dir(), 'receipts')

def generate_receipt(bill_id, bill_date, bill_time, customer_info, items, subtotal_amount, total_amount, settings, delivery_charge=0.0, service_charge=0.0):
    """
    Generates a PDF receipt for the bill formatted for a standard 80mm thermal POS printer.
    Returns the file path of the generated receipt.
    """
    if not os.path.exists(RECEIPTS_DIR):
        os.makedirs(RECEIPTS_DIR)
        
    filename = f"bill_{bill_id}.pdf"
    filepath = os.path.join(RECEIPTS_DIR, filename)
    
    # Standard 80mm receipt width in points (1 inch = 72 points; 3.15 inches = 226.8 points)
    width = 226.8 
    
    # Calculate dynamic height based on number of items
    base_height = 300  # header, info, footer
    logo_height = 80 if settings.get('logo_path', '') and os.path.exists(settings.get('logo_path', '')) else 0
    items_height = len(items) * 15
    charges_height = 0
    if float(delivery_charge) > 0: charges_height += 15
    if float(service_charge) > 0: charges_height += 15
    if charges_height > 0: charges_height += 15  # Subtotal line
    # Account for custom multi-line footer messages
    custom_msg = (settings.get('custom_receipt_message') or '').strip()
    footer_lines = len([l for l in custom_msg.split('\n') if l.strip()]) if custom_msg else 1
    footer_extra = max(0, (footer_lines - 1) * 13)
    height = base_height + logo_height + items_height + charges_height + footer_extra
    
    c = canvas.Canvas(filepath, pagesize=(width, height))
    
    y = height - 20
    margin = 10
    
    # Draw Logo if exists
    logo_path = settings.get('logo_path', '')
    if logo_path and os.path.exists(logo_path):
        try:
            # Center logo
            c.drawImage(logo_path, (width - 80) / 2, y - 60, width=80, height=60, preserveAspectRatio=True, mask='auto')
            y -= 70
        except Exception as e:
            print(f"Failed to load logo for receipt: {e}")
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, settings.get('restaurant_name', 'Restaurant Name'))
    y -= 15
    
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, y, settings.get('address', 'Address'))
    y -= 12
    c.drawCentredString(width / 2, y, f"Phone: {settings.get('phone', 'Phone')}")
    y -= 15
    
    # Divider
    c.setDash(2, 2)
    c.line(margin, y, width - margin, y)
    c.setDash()
    y -= 15
    
    # Bill Info
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, f"Bill No: {bill_id}")
    y -= 12
    c.setFont("Helvetica", 8)
    c.drawString(margin, y, f"Date: {bill_date}")
    c.drawRightString(width - margin, y, f"Time: {bill_time}")
    y -= 15
    
    c.setDash(2, 2)
    c.line(margin, y, width - margin, y)
    c.setDash()
    y -= 15
    
    # Customer Info
    cust_name = customer_info.get('customer_name', '').strip()
    cust_phone = customer_info.get('phone', '').strip()
    cust_addr = customer_info.get('address', '').strip()
    
    # Check if any customer info is actually provided
    has_cust_info = False
    if cust_name and cust_name.lower() != "walk-in customer":
        has_cust_info = True
    if cust_phone and cust_phone != 'N/A':
        has_cust_info = True
    if cust_addr and cust_addr != 'N/A':
        has_cust_info = True
        
    if has_cust_info:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "Customer:")
        y -= 12
        c.setFont("Helvetica", 8)
        
        if cust_name and cust_name.lower() != "walk-in customer":
            c.drawString(margin, y, cust_name[:25]) # Truncate long names
            y -= 12
            
        if cust_phone and cust_phone != 'N/A':
            c.drawString(margin, y, f"Phone: {cust_phone}")
            y -= 12
            
        if cust_addr and cust_addr != 'N/A':
            c.drawString(margin, y, cust_addr[:30])
            y -= 12
            
        y -= 3
        c.setDash(2, 2)
        c.line(margin, y, width - margin, y)
        c.setDash()
        y -= 15
    
    # Items Header
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin, y, "Item")
    c.drawString(width - 90, y, "Price")
    c.drawString(width - 50, y, "Qty")
    c.drawRightString(width - margin, y, "Total")
    y -= 10
    c.setDash(2, 2)
    c.line(margin, y, width - margin, y)
    c.setDash()
    y -= 15
    
    # Items
    c.setFont("Helvetica", 8)
    for item in items:
        # Truncate item name
        item_name = str(item['item_name'])[:12]
        c.drawString(margin, y, item_name)
        c.drawString(width - 90, y, f"{item['price']:.0f}")
        c.drawString(width - 45, y, str(item['quantity']))
        c.drawRightString(width - margin, y, f"{item['subtotal']:.0f}")
        y -= 15
        
    y -= 5
    c.setDash(2, 2)
    c.line(margin, y, width - margin, y)
    c.setDash()
    y -= 15
    
    # Subtotal and Charges
    if float(delivery_charge) > 0 or float(service_charge) > 0:
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin, y, "Subtotal:")
        c.drawRightString(width - margin, y, f"Rs {subtotal_amount:.2f}")
        y -= 15
        
        c.setFont("Helvetica", 8)
        if float(delivery_charge) > 0:
            c.drawString(margin, y, "Delivery Charge:")
            c.drawRightString(width - margin, y, f"Rs {delivery_charge:.2f}")
            y -= 15
        if float(service_charge) > 0:
            c.drawString(margin, y, "Service Charge:")
            c.drawRightString(width - margin, y, f"Rs {service_charge:.2f}")
            y -= 15
            
        y -= 5
        c.setDash(2, 2)
        c.line(margin, y, width - margin, y)
        c.setDash()
        y -= 15
    
    # Grand Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Grand Total:")
    c.drawRightString(width - margin, y, f"Rs {total_amount:.2f}")
    y -= 30
    
    # Footer — use custom message from settings, fallback to default
    footer_message = (settings.get('custom_receipt_message') or '').strip()
    if not footer_message:
        footer_message = "Thank You For Visiting"

    c.setFont("Helvetica-Oblique", 9)
    # Support multi-line messages (split by newline)
    lines = footer_message.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            c.drawCentredString(width / 2, y, line[:50])  # Truncate very long lines
            y -= 13
    
    c.save()
    return filepath
