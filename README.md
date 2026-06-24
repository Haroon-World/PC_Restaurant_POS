# Restaurant POS Desktop Application

A complete Point of Sale desktop application for a small restaurant, built with Python and CustomTkinter.

## Features

- **Offline Support**: Uses SQLite, ensuring instant startup and full offline capability.
- **Daily Reset Logic**: Automatically clears bills and customer records at the start of a new day, while preserving settings and menus.
- **Menu Management**: Add, update, and remove menu items dynamically.
- **Billing System**: Select items, specify quantities, and automatically calculate subtotals and grand totals.
- **PDF Receipts**: Professional receipt generation using ReportLab.
- **History Tracking**: View today's past bills and reprint receipts at any time.

## Requirements

- Python 3.x
- Dependencies listed in `requirements.txt`

## Installation

1. Open a terminal in the project directory.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Folder Structure
- `assets/logos/`: Stores the uploaded restaurant logo.
- `receipts/`: Contains automatically generated PDF receipts.
- `sql/`: Contains the SQLite database schema (`restaurant_pos.sql`).
- `restaurant.db`: The SQLite database file (created automatically on first run).
