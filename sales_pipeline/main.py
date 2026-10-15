import csv
from pathlib import Path

base_dir = Path(__file__).parent
input_file = base_dir / "orders.csv"
output_file = base_dir / "clean_orders.csv"

# 1. Đọc dữ liệu
with open(input_file, mode="r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    orders = list(reader)

# 2. Làm sạch và lọc đơn hoàn thành
seen_ids = set()
clean_orders = []
revenue = 0

for order in orders:
    order_id = order["order_id"]

    if order_id in seen_ids:
        print("Bỏ qua đơn trùng:", order_id)
        continue

    seen_ids.add(order_id)

    if order["status"] != "completed":
        continue

    try:
        amount = int(order["amount"])
    except ValueError:
        print("Số tiền trống hoặc không phải số nguyên:", order_id)
        continue

    if amount <= 0:
        print("Số tiền phải lớn hơn 0:", order_id)
        continue

    # Lưu số tiền đã chuyển sang số nguyên
    order["amount"] = amount

    # Giữ lại đơn hợp lệ để xuất file
    clean_orders.append(order)
    revenue += amount

# 3. Ghi dữ liệu ra file CSV
columns = [
    "order_id",
    "order_date",
    "customer_id",
    "amount",
    "status",
]

with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(clean_orders)

# 4. Báo cáo kết quả
print("Số đơn completed hợp lệ:", len(clean_orders))
print(f"Tổng doanh thu: {revenue:,} VND")
print("Đã lưu file:", output_file)