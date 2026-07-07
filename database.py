import sqlite3

DB_PATH = "market.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    con.execute("""
        CREATE TABLE IF NOT EXISTS items (
            title TEXT PRIMARY KEY,
            category TEXT,
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
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

def add_items(items_list: list[tuple[str, str]]) -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executemany("""
    INSERT OR IGNORE INTO items (title, category) 
    VALUES (?, ?)
    """, items_list)

    con.commit()
    con.close()

def get_items_titles(category: str = "", active: bool = True) -> list[str]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    query = "SELECT title FROM items WHERE is_active = ?"
    params: list[int | str] = [1 if active else 0]

    if category:
        query += " AND category_path = ?"
        params.append(category)

    cur.execute(query, params)
    titles = [row[0] for row in cur.fetchall()]

    con.close()
    return titles

def update_offers(title: str, offers: dict[int,int]) -> None:
    pass

def update_orders(title: str, orders: dict[int, int]) -> None:
    pass

def update_sales(title: str, sales: dict[int, int]) -> None:
    pass

