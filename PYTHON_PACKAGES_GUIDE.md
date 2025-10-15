# 📦 Python Packages Manager - Hướng dẫn sử dụng

## Tổng quan

Tab **Python Packages Manager** cho phép bạn dễ dàng cài đặt, xem và gỡ bỏ các thư viện Python trong Spark Docker containers mà không cần dùng terminal.

## Tính năng chính

### ✅ Cài đặt thư viện
- Cài đặt bất kỳ thư viện Python nào từ PyPI
- Hỗ trợ chỉ định phiên bản (ví dụ: `matplotlib==3.5.3`)
- Tùy chọn `--no-cache-dir` để tiết kiệm dung lượng
- Tùy chọn `--upgrade` để nâng cấp thư viện đã cài

### 📋 Xem thư viện đã cài
- Liệt kê tất cả thư viện trong container
- Hiển thị tên, phiên bản và đường dẫn cài đặt
- Định dạng bảng dễ đọc

### 🗑️ Gỡ thư viện
- Gỡ bỏ thư viện không cần thiết
- Xác nhận trước khi gỡ để tránh nhầm lẫn

### 📚 Thư viện phổ biến
Danh sách sẵn 20+ thư viện phổ biến cho Data Science/Spark:
- **Visualization**: matplotlib, seaborn, plotly
- **Data Processing**: pandas, numpy, scipy
- **Machine Learning**: scikit-learn, xgboost, lightgbm
- **Deep Learning**: torch, tensorflow, keras, transformers
- **Image Processing**: opencv-python, pillow
- **Web/API**: requests, beautifulsoup4, fastapi
- **Database**: sqlalchemy, psycopg2-binary, pymongo

## Cách sử dụng

### 1. Chọn Container

Chọn container muốn cài thư viện:
- `spark-worker` - Worker node (mặc định)
- `spark-master` - Master node
- `jupyter-notebook` - Jupyter container (nếu có)

**💡 Tip**: Nhấn nút "🔄 Làm mới" để tự động phát hiện containers đang chạy.

### 2. Cài đặt thư viện

#### Cách 1: Nhập tên thủ công
```
Tên thư viện: matplotlib
```

#### Cách 2: Chọn từ danh sách phổ biến
```
Hoặc chọn: [Dropdown] → matplotlib
```

#### Cách 3: Chỉ định phiên bản
```
Tên thư viện: matplotlib==3.5.3
```

#### Cách 4: Cài nhiều thư viện cùng lúc
```
Tên thư viện: pandas numpy scipy
```

### 3. Tùy chọn cài đặt

- ☑️ **Không dùng cache**: Tiết kiệm dung lượng, khuyến nghị bật
- ☐ **Nâng cấp nếu đã cài**: Cập nhật lên phiên bản mới nhất

### 4. Thực hiện cài đặt

Nhấn nút **✅ Cài đặt** và theo dõi quá trình trong console.

## Ví dụ thực tế

### Ví dụ 1: Cài matplotlib để vẽ biểu đồ

```
Container: spark-worker
Tên thư viện: matplotlib==3.5.3
Tùy chọn: ✓ Không dùng cache
```

**Lệnh thực thi**:
```bash
docker exec spark-worker python3 -m pip install --no-cache-dir matplotlib==3.5.3
```

### Ví dụ 2: Cài nhiều thư viện ML

```
Container: spark-worker
Tên thư viện: pandas numpy scikit-learn
Tùy chọn: ✓ Không dùng cache
```

### Ví dụ 3: Nâng cấp thư viện đã cài

```
Container: spark-worker
Tên thư viện: requests
Tùy chọn: ✓ Không dùng cache, ✓ Nâng cấp nếu đã cài
```

**Lệnh thực thi**:
```bash
docker exec spark-worker python3 -m pip install --no-cache-dir --upgrade requests
```

## Xem thư viện đã cài

1. Nhấn nút **📋 Xem đã cài**
2. Xem danh sách trong bảng bên dưới:

```
┌────────────────┬──────────┬─────────────────────────────┐
│ Tên thư viện   │ Phiên bản │ Đường dẫn                   │
├────────────────┼──────────┼─────────────────────────────┤
│ matplotlib     │ 3.5.3    │ /usr/local/lib/python3.9... │
│ pandas         │ 1.5.0    │ /usr/local/lib/python3.9... │
│ numpy          │ 1.23.0   │ /usr/local/lib/python3.9... │
└────────────────┴──────────┴─────────────────────────────┘
```

## Gỡ thư viện

1. Nhấn **📋 Xem đã cài** để load danh sách
2. Click chọn thư viện cần gỡ trong bảng
3. Nhấn nút **🗑️ Gỡ thư viện**
4. Xác nhận trong dialog

## Lưu ý quan trọng

### ⚠️ Thư viện hệ thống
Không nên gỡ các thư viện cốt lõi:
- pip
- setuptools
- wheel
- pyspark (nếu đang dùng Spark)

### 💾 Persistence
Thư viện cài trong container sẽ **mất** khi:
- Xóa container
- Rebuild image từ đầu

**Giải pháp**:
- Thêm vào `requirements.txt` trong image
- Hoặc mount volume chứa thư viện
- Hoặc rebuild Dockerfile với các thư viện cần thiết

### 🔄 Cài lại sau khi restart
Nếu thư viện bị mất sau khi restart:
1. Container bị xóa/recreate
2. Cần cài lại hoặc thêm vào Dockerfile

## Troubleshooting

### ❌ "docker: command not found"
**Nguyên nhân**: Docker chưa được cài hoặc không trong PATH

**Giải pháp**:
```powershell
# Windows: Cài Docker Desktop
# Kiểm tra:
docker --version
```

### ❌ "Error: no such container"
**Nguyên nhân**: Container không tồn tại hoặc đã dừng

**Giải pháp**:
1. Kiểm tra containers đang chạy:
   ```powershell
   docker ps
   ```
2. Nhấn "🔄 Làm mới" để cập nhật danh sách
3. Khởi động lại containers nếu cần

### ❌ "pip: No matching distribution found"
**Nguyên nhân**: Tên thư viện sai hoặc phiên bản không tồn tại

**Giải pháp**:
1. Kiểm tra tên đúng trên [PyPI](https://pypi.org)
2. Kiểm tra phiên bản có sẵn
3. Thử cài không chỉ định phiên bản (lấy mới nhất)

### ⏳ Cài đặt quá lâu
**Nguyên nhân**: Thư viện lớn hoặc có nhiều dependencies

**Giải pháp**:
- Đợi đến khi hoàn thành
- Theo dõi progress trong console
- Xem CPU/Memory usage trong Performance Monitor tab

### 🔒 Permission denied
**Nguyên nhân**: User trong container không có quyền cài đặt

**Giải pháp**:
```dockerfile
# Thêm vào Dockerfile:
USER root
RUN pip install <package>
USER spark
```

## Tips & Best Practices

### 💡 Tip 1: Test trong worker trước
Cài thư viện vào `spark-worker` để test trước khi cài vào `spark-master`.

### 💡 Tip 2: Sử dụng version pinning
```
✅ Good: matplotlib==3.5.3
❌ Bad: matplotlib (phiên bản có thể thay đổi)
```

### 💡 Tip 3: Cài nhóm thư viện liên quan
```
# Data Science stack
pandas numpy matplotlib seaborn

# Machine Learning stack
scikit-learn xgboost lightgbm
```

### 💡 Tip 4: Backup requirements.txt
Sau khi cài xong, export danh sách:
```bash
docker exec spark-worker pip freeze > requirements.txt
```

### 💡 Tip 5: Dọn dẹp thư viện không dùng
Định kỳ gỡ thư viện không còn cần thiết để tiết kiệm dung lượng.

## Tích hợp với Spark Job

Sau khi cài thư viện, sử dụng trong PySpark code:

```python
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

spark = SparkSession.builder \
    .appName("Data Visualization") \
    .getOrCreate()

# Load data
df = spark.read.csv("hdfs://namenode:8020/data/input.csv", header=True)

# Convert to pandas for plotting
pdf = df.toPandas()

# Visualize
plt.figure(figsize=(10, 6))
plt.bar(pdf['category'], pdf['value'])
plt.title('Data Analysis')
plt.savefig('/opt/spark/work-dir/output/chart.png')
```

## Lệnh CLI tương đương

Tất cả thao tác trong GUI đều có thể thực hiện qua CLI:

```powershell
# Cài thư viện
docker exec spark-worker python3 -m pip install --no-cache-dir matplotlib==3.5.3

# Xem đã cài
docker exec spark-worker python3 -m pip list

# Xem chi tiết
docker exec spark-worker python3 -m pip show matplotlib

# Gỡ thư viện
docker exec spark-worker python3 -m pip uninstall -y matplotlib

# Export requirements
docker exec spark-worker python3 -m pip freeze > requirements.txt

# Cài từ requirements
docker exec spark-worker python3 -m pip install -r /path/requirements.txt
```

## Kết luận

Tab Python Packages Manager giúp đơn giản hóa việc quản lý thư viện trong Spark containers, phù hợp cho:
- Developers muốn test nhanh
- Data Scientists cần thư viện visualization
- DevOps cần quản lý dependencies
- Students học Spark/PySpark

**Ưu điểm**:
- ✅ Giao diện trực quan, dễ sử dụng
- ✅ Không cần nhớ lệnh Docker/pip phức tạp
- ✅ Real-time output và error handling
- ✅ Danh sách thư viện phổ biến có sẵn
- ✅ Hỗ trợ multi-container

**Hạn chế**:
- ⚠️ Thư viện không persistent sau khi xóa container
- ⚠️ Cần internet để download từ PyPI
- ⚠️ Không hỗ trợ offline installation

---

**Tác giả**: Spark Runner GUI Team  
**Phiên bản**: 1.0.0  
**Cập nhật**: 2025-10-15
