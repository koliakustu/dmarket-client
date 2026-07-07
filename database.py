import sqlite3

DB_PATH = "market.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    con.execute("""
        CREATE TABLE IF NOT EXISTS items (
            title TEXT PRIMARY KEY,
            category TEXT
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            title TEXT,
            price_cents INTEGER,
            amount INTEGER,
            PRIMARY KEY (title, price_cents),
            FOREIGN KEY (title) REFERENCES items (title) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            title TEXT,
            price_cents INTEGER,
            amount INTEGER,
            PRIMARY KEY (title, price_cents),
            FOREIGN KEY (title) REFERENCES items (title) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            sale_date TEXT,
            price_cents INTEGER,
            FOREIGN KEY (title) REFERENCES items (title) ON DELETE CASCADE
        )
    """)

    con.commit()
    con.close()

    def update_offers(title: str, offers: dict[int,int]) -> None:
        pass

    def update_orders(title: str, orders: dict[int, int]) -> None:
        pass

    def update_sales(title: str, sales: dict[int, int]) -> None:
        pass

