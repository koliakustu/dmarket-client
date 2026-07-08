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
            sale_date INTEGER,
            price_cents INTEGER,
            is_order INTEGER,
            FOREIGN KEY (title) REFERENCES items (title) ON DELETE CASCADE
        )
    """)

    con.commit()
    con.close()

def add_items(items_list: list[tuple[str, str]]) -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executemany("""
    INSERT INTO items (title, category, last_updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(title) DO UPDATE SET
        last_updated_at = CURRENT_TIMESTAMP
    """, items_list)

    con.commit()
    con.close()

def touch_item_timestamp(title: str) -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
    UPDATE items SET last_updated_at = CURRENT_TIMESTAMP WHERE title = ?
    """, [title])

    if cur.rowcount == 0:
        con.close()
        raise ValueError(f"Item '{title}' does not exist in the database.")

    con.commit()
    con.close()

def get_items_titles(category: str = "", active: bool = True) -> list[str]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    query = "SELECT title FROM items WHERE is_active = ?"
    params: list[int | str] = [1 if active else 0]

    if category:
        query += " AND category = ?"
        params.append(category)

    cur.execute(query, params)
    titles = [row[0] for row in cur.fetchall()]

    con.close()
    return titles

def update_offers(title: str, offers: dict[int,int]) -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("DELETE FROM offers WHERE title = ?", [title])

    db_data = [(title, price, amount) for price, amount in offers.items()]

    if db_data:
        cur.executemany("""
            INSERT INTO offers (title, price_cents, amount) 
            VALUES (?, ?, ?)
        """, db_data
        )

    con.commit()
    con.close()

def update_orders(title: str, orders: dict[int, int]) -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("DELETE FROM orders WHERE title = ?", [title])

    db_data = [(title, price, amount) for price, amount in orders.items()]

    if db_data:
        cur.executemany("""
            INSERT INTO orders (title, price_cents, amount) 
            VALUES (?, ?, ?)
        """, db_data
        )

    con.commit()
    con.close()

def update_sales(title: str, sales: list[tuple[int, int, int]]) -> None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("DELETE FROM history WHERE title = ?", [title])

    db_data = [(title, sale_date, price, is_order) for sale_date, price, is_order in sales]

    if db_data:
        cur.executemany("""
            INSERT INTO history (title, sale_date, price_cents, is_order) 
            VALUES (?, ?, ?, ?)
        """, db_data
        )

    con.commit()
    con.close()

def get_last_sale_date(title: str) -> int | None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT MAX(sale_date) FROM history WHERE title = ?", [title])
    res = cur.fetchone()
    con.close()
    return res[0] if res else None
