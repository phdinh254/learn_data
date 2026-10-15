import csv
from pathlib import Path

base_dir = Path(__file__).parent
raw_dir = base_dir / "data" / "raw"
output_dir = base_dir / "data" / "processed"

csv_files = sorted(raw_dir.glob("*.csv"))

if not csv_files:
    raise SystemExit(f"Không tìm thấy file CSV trong: {raw_dir}")

# Tự tạo thư mục đầu ra nếu chưa có
output_dir.mkdir(parents=True, exist_ok=True)

seen_ids = set()
clean_orders = []
rejected_orders = []

total_rows = 0
completed_count = 0
revenue = 0

for csv_file in csv_files:
    print(f"Đang đọc: {csv_file.name}")

    with open(
        csv_file,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        # Dòng 1 là tiêu đề, dữ liệu mẫu bắt đầu từ dòng 2
        for row_number, order in enumerate(reader, start=2):
            total_rows += 1

            # Giữ thông tin nguồn để tra cứu
            order["source_file"] = csv_file.name
            order["source_row"] = row_number

            order_id = order["order_id"]
            reason = ""

            if order["status"] == "completed":
                completed_count += 1

            # Giữ lần xuất hiện đầu tiên của mỗi mã đơn
            if order_id in seen_ids:
                reason = "Trùng mã đơn"
            else:
                seen_ids.add(order_id)

                if order["status"] != "completed":
                    reason = "Trạng thái chưa hoàn thành"
                else:
                    try:
                        amount = int(order["amount"])
                    except ValueError:
                        reason = "Số tiền trống hoặc không phải số nguyên"
                    else:
                        if amount <= 0:
                            reason = "Số tiền phải lớn hơn 0"

            if reason:
                order["reason"] = reason
                rejected_orders.append(order)
                continue

            order["amount"] = amount
            clean_orders.append(order)
            revenue += amount

# Các cột chung của file đầu ra
columns = [
    "order_id",
    "order_date",
    "customer_id",
    "amount",
    "status",
    "source_file",
    "source_row",
]

# Ghi đơn hợp lệ
clean_file = output_dir / "clean_orders.csv"

with open(clean_file, mode="w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(clean_orders)

# Ghi các dòng bị loại kèm lý do
rejected_file = output_dir / "rejected_orders.csv"

with open(rejected_file, mode="w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=columns + ["reason"],
    )
    writer.writeheader()
    writer.writerows(rejected_orders)

print("\nKẾT QUẢ")
print("Tổng số dòng đầu vào:", total_rows)
print("Số dòng completed trước làm sạch:", completed_count)
print("Số đơn hợp lệ:", len(clean_orders))
print("Số dòng bị loại:", len(rejected_orders))
print(f"Tổng doanh thu: {revenue:,} VND")
print("Đã lưu:", clean_file)
print("Đã lưu:", rejected_file)