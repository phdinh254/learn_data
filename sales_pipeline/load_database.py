import csv
import sqlite3
from pathlib import Path

base_dir = Path(__file__).parent
input_file = base_dir / "clean_orders.csv"
database_file = base_dir / "sales.db"

# 1. Đọc dữ liệu đã làm sạch
with open(input_file, mode="r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    orders = list(reader)

# 2. Kết nối SQLite; tự tạo sales.db nếu chưa có
conn = sqlite3.connect(database_file)

try:
    # 3. Tạo bảng nếu chưa tồn tại
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            order_date TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            amount INTEGER NOT NULL CHECK (amount > 0),
            status TEXT NOT NULL
        )
    """)

    # 4. Thêm đơn hàng; bỏ qua mã đơn đã tồn tại
    for order in orders:
        conn.execute("""
            INSERT INTO orders (
                order_id,
                order_date,
                customer_id,
                amount,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO NOTHING
        """, (
            order["order_id"],
            order["order_date"],
            order["customer_id"],
            int(order["amount"]),
            order["status"],
        ))

    # Lưu thay đổi
    conn.commit()

    # 5. Kiểm tra dữ liệu bằng SQL
    cursor = conn.execute("""
        SELECT COUNT(*), COALESCE(SUM(amount), 0)
        FROM orders
    """)

    order_count, revenue = cursor.fetchone()

    print("Số đơn trong database:", order_count)
    print(f"Tổng doanh thu: {revenue:,} VND")
    print("Database:", database_file)

finally:
    # Đóng kết nối kể cả khi có lỗi
    conn.close()