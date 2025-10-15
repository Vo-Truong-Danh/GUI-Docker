# 📦 Hướng dẫn nhanh: Cài thư viện Python vào Spark

## Vấn đề trước đây

Để cài thư viện vào Spark container, bạn phải:
```bash
# Phức tạp, dễ nhầm lẫn
docker exec spark-worker python3 -m pip install --no-cache-dir "matplotlib==3.5.3"
```

## Giải pháp mới ✨

**Tab Python Packages** - Chỉ cần click!

## 3 Bước đơn giản

### Bước 1: Mở tab 📦 Python Packages

### Bước 2: Nhập thư viện
```
Tên thư viện: matplotlib==3.5.3
```
Hoặc chọn từ danh sách có sẵn.

### Bước 3: Nhấn "✅ Cài đặt"

Xong! 🎉

## Demo thực tế

### Ví dụ 1: Cài matplotlib
```
1. Mở tab "📦 Python Packages"
2. Container: spark-worker
3. Tên thư viện: matplotlib==3.5.3
4. ✓ Không dùng cache
5. Nhấn "✅ Cài đặt"
```

### Ví dụ 2: Cài nhiều thư viện
```
Tên thư viện: pandas numpy scikit-learn
→ Cài cả 3 cùng lúc!
```

### Ví dụ 3: Xem đã cài gì
```
Nhấn "📋 Xem đã cài"
→ Hiện bảng với tên, phiên bản, đường dẫn
```

### Ví dụ 4: Gỡ thư viện
```
1. Nhấn "📋 Xem đã cài"
2. Click chọn thư viện
3. Nhấn "🗑️ Gỡ thư viện"
```

## Thư viện phổ biến có sẵn

### Vẽ biểu đồ
- matplotlib
- seaborn
- plotly

### Xử lý dữ liệu
- pandas
- numpy
- scipy

### Machine Learning
- scikit-learn
- xgboost
- lightgbm

### Deep Learning
- torch (PyTorch)
- tensorflow
- keras

### Xử lý ảnh
- opencv-python
- pillow

### Web/API
- requests
- beautifulsoup4
- fastapi

## Lưu ý quan trọng ⚠️

### Thư viện mất khi restart container
**Giải pháp**:
```dockerfile
# Thêm vào Dockerfile
RUN pip install matplotlib pandas numpy
```

### Kiểm tra container đang chạy
```
Nhấn "🔄 Làm mới" để load danh sách containers
```

### Cài có chỉ định phiên bản
```
✅ matplotlib==3.5.3  (phiên bản cố định)
❌ matplotlib         (phiên bản mới nhất, có thể không tương thích)
```

## So sánh CLI vs GUI

### CLI (Cách cũ)
```bash
# Dài, khó nhớ, dễ sai
docker exec spark-worker python3 -m pip install --no-cache-dir "matplotlib==3.5.3"

# Xem đã cài
docker exec spark-worker python3 -m pip list

# Gỡ
docker exec spark-worker python3 -m pip uninstall -y matplotlib
```

### GUI (Cách mới) ✨
```
1. Chọn container
2. Nhập tên thư viện
3. Click "Cài đặt"
→ Xong!
```

## Sử dụng trong PySpark

Sau khi cài, dùng trong code:

```python
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
import pandas as pd

spark = SparkSession.builder.appName("Demo").getOrCreate()

# Đọc dữ liệu
df = spark.read.csv("hdfs://namenode:8020/data/sales.csv", header=True)

# Chuyển sang pandas
pdf = df.toPandas()

# Vẽ biểu đồ
plt.figure(figsize=(10, 6))
plt.bar(pdf['month'], pdf['revenue'])
plt.title('Monthly Revenue')
plt.savefig('/opt/spark/work-dir/chart.png')
print("Đã lưu biểu đồ!")
```

## Troubleshooting

### ❌ "docker: command not found"
**Giải pháp**: Cài Docker Desktop

### ❌ "no such container: spark-worker"
**Giải pháp**: 
```
1. Kiểm tra: docker ps
2. Start container: docker-compose up -d
3. Nhấn "🔄 Làm mới" trong app
```

### ⏳ Cài đặt quá lâu
**Giải pháp**: Đợi, theo dõi trong console

### ❌ "No matching distribution found"
**Giải pháp**: Kiểm tra tên và phiên bản trên https://pypi.org

## Tips hay 💡

### 1. Test trong worker trước
Cài vào `spark-worker` để test, sau đó mới cài vào `spark-master`.

### 2. Backup danh sách
```bash
docker exec spark-worker pip freeze > requirements.txt
```

### 3. Cài từ requirements.txt
```bash
docker exec spark-worker pip install -r /path/requirements.txt
```

### 4. Kiểm tra thư viện hoạt động
```bash
docker exec spark-worker python3 -c "import matplotlib; print(matplotlib.__version__)"
```

### 5. Xóa cache để giải phóng dung lượng
```bash
docker exec spark-worker pip cache purge
```

## Kết luận

✅ **Trước**: Phải nhớ lệnh Docker/pip phức tạp  
✅ **Sau**: Chỉ cần click trong GUI  

✅ **Trước**: Dễ gõ nhầm lệnh  
✅ **Sau**: Chọn từ danh sách có sẵn  

✅ **Trước**: Không biết cài được gì  
✅ **Sau**: Xem danh sách đầy đủ  

**→ Tiết kiệm thời gian, giảm lỗi, tăng năng suất!** 🚀

---

**Chi tiết đầy đủ**: [PYTHON_PACKAGES_GUIDE.md](PYTHON_PACKAGES_GUIDE.md)
