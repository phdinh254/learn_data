import csv
import sqlite3
from pathlib import Path

base_dir = Path(__file__).parent
input_file = base_dir / "data" / "processed" / "clean_orders.csv"
database_file = base_dir / "sales.db"

if not input_file.exists():
    raise SystemExit("Chưa có clean_orders.csv. Hãy chạy main.py trước.")

conn = sqlite3.connect(database_file)

try:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT NOT NULL PRIMARY KEY,
            order_date TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            amount INTEGER NOT NULL CHECK (amount > 0),
            status TEXT NOT NULL CHECK (status = 'completed'),
            source_file TEXT NOT NULL,
            source_row INTEGER NOT NULL
        )
    """)

    inserted_count = 0
    skipped_count = 0

    with open(
        input_file,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for order in reader:
            cursor = conn.execute("""
                INSERT INTO orders (
                    order_id,
                    order_date,
                    customer_id,
                    amount,
                    status,
                    source_file,
                    source_row
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO NOTHING
            """, (
                order["order_id"],
                order["order_date"],
                order["customer_id"],
                int(order["amount"]),
                order["status"],
                order["source_file"],
                int(order["source_row"]),
            ))

            if cursor.rowcount == 1:
                inserted_count += 1
            else:
                skipped_count += 1

    conn.commit()

    total_orders, revenue = conn.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0)
        FROM orders
    """).fetchone()

    print("Số đơn thêm mới:", inserted_count)
    print("Số đơn đã tồn tại, bỏ qua:", skipped_count)
    print("Tổng số đơn trong database:", total_orders)
    print(f"Tổng doanh thu: {revenue:,} VND")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()