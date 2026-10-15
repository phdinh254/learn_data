import sqlite3
from pathlib import Path

database_file = Path(__file__).parent / "sales.db"

if not database_file.exists():
    raise SystemExit("Chưa có sales.db. Hãy chạy load_database.py trước.")

conn = sqlite3.connect(database_file)

try:
    # Tổng quan
    total_orders, revenue = conn.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0)
        FROM orders
    """).fetchone()

    print("TỔNG QUAN")
    print("Số đơn:", total_orders)
    print(f"Doanh thu: {revenue:,} VND")

    # Báo cáo theo ngày phát sinh đơn hàng
    print("\nDOANH THU THEO NGÀY")

    rows = conn.execute("""
        SELECT order_date, COUNT(*), SUM(amount)
        FROM orders
        GROUP BY order_date
        ORDER BY order_date
    """)

    for order_date, count, total in rows:
        print(f"{order_date} | {count} đơn | {total:,} VND")

    # Báo cáo theo khách hàng
    print("\nDOANH THU THEO KHÁCH HÀNG")

    rows = conn.execute("""
        SELECT customer_id, COUNT(*), SUM(amount)
        FROM orders
        GROUP BY customer_id
        ORDER BY SUM(amount) DESC, customer_id
    """)

    for customer_id, count, total in rows:
        print(f"{customer_id} | {count} đơn | {total:,} VND")

finally:
    conn.close()