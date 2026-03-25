import re
import csv
import sqlite3
import datetime
from datetime import timedelta

def parse_ai_input(text):
    text = text.lower()
    
    # Defaults
    amount = None
    item = ""
    category = "Others"
    date = datetime.datetime.now()
    
    # 1. Parse Date naturally
    if "yesterday" in text:
        date = date - timedelta(days=1)
        text = text.replace("yesterday", "").strip()
    elif "last week" in text:
        date = date - timedelta(days=7)
        text = text.replace("last week", "").strip()
    
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")

    # 2. Parse Amount (look for $, numbers, or text followed by numbers)
    # Examples: "$15 for pizza", "15 for pizza", "bought coffee for 5.50"
    amount_match = re.search(r'\$?(\d+(?:\.\d{1,2})?)', text)
    if amount_match:
        amount = float(amount_match.group(1))
        # Remove the amount from the string to help find the item
        text = text.replace(amount_match.group(0), "").strip()
    
    # 3. Parse Item (simply grab what's left, preferably after 'for' or 'bought')
    # Cleanup fluff words
    text = re.sub(r'\b(for|spent|bought|paid)\b', '', text).strip()
    item = text if text else "Unknown Item"
    
    # 4. Guess Category (simple keyword matching)
    if any(word in item for word in ['pizza', 'coffee', 'lunch', 'burger', 'food', 'dinner']):
        category = "Food"
    elif any(word in item for word in ['uber', 'lyft', 'gas', 'taxi', 'bus', 'train']):
        category = "Transport"
    elif any(word in item for word in ['movie', 'game', 'concert', 'ticket']):
        category = "Entertainment"
    elif any(word in item for word in ['shirt', 'shoes', 'clothes', 'amazon']):
        category = "Shopping"
    elif any(word in item for word in ['electric', 'water', 'internet', 'rent']):
        category = "Utilities"

    return {"amount": amount, "item": item, "category": category, "date": date_str}

def export_to_csv(db_path, filename="expenses_export.csv"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, item, amount, category, date, is_recurring, recurrence_period FROM expenses")
        rows = cursor.fetchall()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Item', 'Amount', 'Category', 'Date', 'Is Recurring', 'Recurrence Period'])
            writer.writerows(rows)
            
        conn.close()
        return True, filename
    except Exception as e:
        return False, str(e)
