import sqlite3
import datetime

class DB:
    def __init__(self):
        self._conn = sqlite3.connect("smart_expenses.db", check_same_thread=False)
        self._cursor = self._conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        
        # Add new columns if they don't exist (migration)
        try:
            self._cursor.execute("ALTER TABLE expenses ADD COLUMN is_recurring BOOLEAN DEFAULT 0")
        except sqlite3.OperationalError:
            pass
            
        try:
            self._cursor.execute("ALTER TABLE expenses ADD COLUMN recurrence_period TEXT DEFAULT 'none'")
        except sqlite3.OperationalError:
            pass

        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL
            )
        """)
        self._conn.commit()

    def add_expense(self, item, amount, category, date=None, is_recurring=False, recurrence_period='none'):
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._cursor.execute(
            "INSERT INTO expenses (item, amount, category, date, is_recurring, recurrence_period) VALUES (?, ?, ?, ?, ?, ?)", 
            (item, amount, category, date, is_recurring, recurrence_period)
        )
        self._conn.commit()

    def get_all_expenses(self, limit=None):
        query = "SELECT * FROM expenses ORDER BY date DESC"
        if limit is not None:
            query += f" LIMIT {limit}"
        self._cursor.execute(query)
        return self._cursor.fetchall()

    def delete_expense(self, id):
        self._cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
        self._conn.commit()

    def get_stats_by_category(self):
        self._cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        return self._cursor.fetchall()
        
    def get_expenses_by_date_range(self, start_date, end_date): # YYYY-MM-DD
        self._cursor.execute(
            "SELECT * FROM expenses WHERE date(date) >= date(?) AND date(date) <= date(?) ORDER BY date DESC",
            (start_date, end_date)
        )
        return self._cursor.fetchall()

    def set_budget(self, category, amount):
        self._cursor.execute(
            "INSERT INTO budgets (category, amount) VALUES (?, ?) ON CONFLICT(category) DO UPDATE SET amount=?", 
            (category, amount, amount)
        )
        self._conn.commit()

    def get_budgets(self):
        self._cursor.execute("SELECT category, amount FROM budgets")
        return {row[0]: row[1] for row in self._cursor.fetchall()}
        
    def close(self):
        self._conn.close()
