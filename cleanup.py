import sqlite3
from datetime import datetime
from database import get_connection

def perform_daily_cleanup():
    """
    Checks the LastCleanup table. If the date has changed (new day),
    clears the Customers, Bills, and BillItems tables.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, cleanup_date FROM LastCleanup ORDER BY id DESC LIMIT 1")
        record = cursor.fetchone()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        if record:
            last_cleanup_date = record['cleanup_date']
            record_id = record['id']
            
            if last_cleanup_date != today:
                # It's a new day, clear history tables
                cursor.execute("DELETE FROM BillItems")
                cursor.execute("DELETE FROM Bills")
                cursor.execute("DELETE FROM Customers")
                
                # Update LastCleanup date
                cursor.execute("UPDATE LastCleanup SET cleanup_date = ? WHERE id = ?", (today, record_id))
                
                conn.commit()
                print(f"Daily cleanup performed for {today}")
        else:
            # Should not happen since initialize_database creates it, but just in case
            cursor.execute("INSERT INTO LastCleanup (cleanup_date) VALUES (?)", (today,))
            conn.commit()
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()
