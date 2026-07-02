import sqlite3


class Database:

    def __init__(self, db="data.db"):
        self.conn = sqlite3.connect(db)
        self._init()

    def _init(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            invoice_number TEXT,
            date TEXT,
            total TEXT
        )
        """)

    def save(self, receipt):
        try:
            self.conn.execute("""
            INSERT INTO invoices (company, invoice_number, date, total)
            VALUES (?, ?, ?, ?)
            """, (
                receipt.company.value,
                receipt.invoice_number.value,
                receipt.date.value,
                receipt.total.value
            ))
            self.conn.commit()
        except:
            self.conn.rollback()
            raise

    def close(self):
        self.conn.close()