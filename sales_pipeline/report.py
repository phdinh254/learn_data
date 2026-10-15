import sqlite3
from pathlib import Path

database_file = Path(__file__).parent / "sales.db"

# Kiểm tra để tránh vô tình tạo database trống
if not database_file.exists():
    raise SystemExit("Chưa có sales.db. Hãy chạy load_database.py trước.")

conn = sqlite3.connect(database_file)

try:
    # 1. Tổng số đơn và tổng doanh thu
    cursor = conn.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0)
        FROM orders
    """)

    order_count, revenue = cursor.fetchone()

    print("TỔNG QUAN")
    print("Số đơn:", order_count)
    print(f"Doanh thu: {revenue:,} VND")

    # 2. Doanh thu theo ngày
    cursor = conn.execute("""
        SELECT order_date, COUNT(*), SUM(amount)
        FROM orders
        GROUP BY order_date
        ORDER BY order_date
    """)

    print("\nDOANH THU THEO NGÀY")

    for order_date, count, total in cursor:
        print(f"{order_date} | {count} đơn | {total:,} VND")

    # 3. Doanh thu theo khách hàng
    cursor = conn.execute("""
        SELECT customer_id, COUNT(*), SUM(amount)
        FROM orders
        GROUP BY customer_id
        ORDER BY SUM(amount) DESC, customer_id
    """)

    print("\nDOANH THU THEO KHÁCH HÀNG")

    for customer_id, count, total in cursor:
        print(f"{customer_id} | {count} đơn | {total:,} VND")

finally:
    conn.close()