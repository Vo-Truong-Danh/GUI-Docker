# 🚀 Hướng Dẫn Nhanh: Upload & Xử Lý File Lớn

## 📋 Bài toán: Xử lý file CSV 2GB với 10 triệu dòng

### Scenario: Reddit Comments Dataset
- **File**: `reddit_comments_2023.csv`
- **Size**: 2.5 GB  
- **Rows**: 10,500,000 dòng
- **Columns**: id, created_utc, author, body, score, subreddit, link_flair_text

**Yêu cầu:**
1. ✅ Upload file lớn lên HDFS
2. ✅ Trích xuất các trường cần thiết
3. ✅ Lọc bỏ [deleted] comments
4. ✅ Lưu kết quả dạng Parquet

---

## 🎯 Giải pháp (3 bước)

### Bước 1: Upload File CSV lên HDFS 📤

#### Trong GUI:

1. **Mở app**: `python main.py`
2. **Chọn tab**: "HDFS Upload"
3. **Browse file**: Chọn `reddit_comments_2023.csv`
4. **Container**: `namenode`
5. **HDFS Path**: `/user/data/raw/`
6. **Click**: "📤 Upload"

**Kết quả:**
```
📊 File size: 2500.00 MB
📦 Using chunked upload (file > 100 MB)
🔪 Chunk size: 50.00 MB
🧩 Total chunks: 50

📦 Chunk 1/50: 50.00 MB
   ✓ Progress: 2.0%
...
📦 Chunk 50/50: 50.00 MB
   ✓ Progress: 100.0%

✅ Successfully uploaded reddit_comments_2023.csv
⏱️ Total time: 3m 45s
```

#### Hoặc Terminal:

```powershell
cd run_spark_gui

python large_file_upload.py `
  "D:/data/reddit_comments_2023.csv" `
  namenode `
  "/user/data/raw/reddit_comments_2023.csv"
```

---

### Bước 2: Copy Spark Job vào Container 📋

```powershell
# Copy ETL script vào spark-master
docker cp spark_jobs/csv_etl_job.py spark-master:/opt/spark-apps/

# Verify
docker exec spark-master ls -lh /opt/spark-apps/csv_etl_job.py
```

**Output:**
```
-rw-r--r-- 1 root root 12K Oct 15 23:00 /opt/spark-apps/csv_etl_job.py
```

---

### Bước 3: Chạy Spark ETL Job 🔥

#### Option A: Qua GUI (Recommended)

1. **Mở tab**: "Spark Runner"
2. **Script Path**: `/opt/spark-apps/csv_etl_job.py`
3. **Arguments** (2 dòng):
   ```
   hdfs:///user/data/raw/reddit_comments_2023.csv
   hdfs:///user/data/processed/reddit_comments_cleaned
   ```
4. **Container**: `spark-master`
5. **Click**: "🚀 Run Spark Job"

#### Option B: Qua Terminal

```powershell
docker exec spark-master spark-submit `
  --master spark://spark-master:7077 `
  --executor-memory 2G `
  --driver-memory 1G `
  /opt/spark-apps/csv_etl_job.py `
  hdfs:///user/data/raw/reddit_comments_2023.csv `
  hdfs:///user/data/processed/reddit_comments_cleaned
```

**Kết quả mong đợi:**

```
============================================================
🚀 Starting Spark ETL Job - Large CSV Processing
============================================================

📖 Reading CSV from HDFS...
✅ Read 10,500,000 records in 45s
📊 Partitions: 16

🔍 Extracting required fields...
✅ Extracted 7 columns:
   - created_utc
   - body
   - score
   - subreddit
   - link_flair_text
   - author
   - id

🧹 Cleaning data...
   Initial: 10,500,000 records
   Filtered [deleted]: 890,234 records
   Filtered [removed]: 234,567 records
   Filtered empty body: 145,678 records
   Final: 9,229,521 records
   ✅ Removed 1,270,479 (12.1%)

📊 Summary Statistics:

🏆 Top 10 Subreddits:
+------------------+---------+
|subreddit         |count    |
+------------------+---------+
|askreddit         |1,245,890|
|politics          |842,341  |
|worldnews         |731,256  |
|funny             |628,945  |
|todayilearned     |512,378  |
+------------------+---------+

💾 Writing to Parquet...
   📂 Partitioned by: year, month
✅ Written 9,229,521 records in 67s

============================================================
✅ ETL Job Completed Successfully!
⏱️ Total time: 2m 45s
============================================================
```

---

## 🔍 Kiểm Tra Kết Quả

### Xem file đã xử lý:

```powershell
# List output directory
docker exec namenode hdfs dfs -ls /user/data/processed/reddit_comments_cleaned

# Output:
drwxr-xr-x   - root supergroup          0 2023-10-15 23:20 /user/data/processed/reddit_comments_cleaned/year=2023
drwxr-xr-x   - root supergroup          0 2023-10-15 23:20 /user/data/processed/reddit_comments_cleaned/year=2022

# List partitions
docker exec namenode hdfs dfs -ls /user/data/processed/reddit_comments_cleaned/year=2023

# Output:
drwxr-xr-x   - root supergroup          0 /user/data/processed/reddit_comments_cleaned/year=2023/month=1
drwxr-xr-x   - root supergroup          0 /user/data/processed/reddit_comments_cleaned/year=2023/month=2
...
drwxr-xr-x   - root supergroup          0 /user/data/processed/reddit_comments_cleaned/year=2023/month=12
```

### Query data với PySpark:

```powershell
# Vào spark-master container
docker exec -it spark-master bash

# Start PySpark shell
pyspark

# Trong PySpark:
>>> df = spark.read.parquet("hdfs:///user/data/processed/reddit_comments_cleaned")
>>> df.printSchema()
>>> df.count()  # 9,229,521
>>> df.show(5, truncate=False)

# Query nhanh nhờ partitioning
>>> df_oct = df.filter("year = 2023 AND month = 10")
>>> df_oct.count()

# Top comments by score
>>> df.orderBy(col("score").desc()).select("body", "score", "subreddit").show(10, truncate=False)

# Filter by subreddit
>>> df_ask = df.filter("subreddit_clean = 'askreddit'")
>>> df_ask.select("body", "score").show(10, truncate=False)
```

---

## 📊 So Sánh Performance

### Before (CSV):
- **Size**: 2.5 GB
- **Read time**: 45 seconds
- **Query time** (filter): 30 seconds
- **Storage cost**: High

### After (Parquet):
- **Size**: 420 MB (**83% nhỏ hơn** 🎉)
- **Read time**: 7 seconds (**6.4x nhanh hơn** ⚡)
- **Query time** (filter): 2 seconds (**15x nhanh hơn** 🚀)
- **Storage cost**: Low

---

## 💡 Tips & Tricks

### Tip 1: Compress CSV trước khi upload (Recommended)

```powershell
# Compress bằng gzip (Windows: 7-Zip, WinRAR)
# File size: 2.5 GB → 450 MB (82% nhỏ hơn!)

# Spark có thể đọc .gz trực tiếp
spark.read.csv("hdfs:///user/data/raw/reddit_comments_2023.csv.gz")
```

### Tip 2: Test với sample data trước

```powershell
# Tạo sample 10K rows
Get-Content reddit_comments_2023.csv -Head 10001 | Out-File sample_10k.csv

# Upload sample
# Test ETL job
# Nếu OK → upload full file
```

### Tip 3: Monitor Spark UI

Mở browser: `http://localhost:4040`

Xem:
- **Jobs**: Thời gian từng stage
- **Stages**: Task distribution  
- **Storage**: Cached DataFrames
- **Executors**: Memory usage

### Tip 4: Tune Spark memory nếu cần

```powershell
spark-submit `
  --executor-memory 4G `   # Tăng từ 2G
  --driver-memory 2G `      # Tăng từ 1G
  --conf spark.sql.shuffle.partitions=400 `  # Tăng từ 200
  ...
```

---

## ❓ Troubleshooting

### Problem: Upload quá chậm

**Solution 1**: Compress file trước
```powershell
7z a reddit_comments.csv.gz reddit_comments.csv
# Upload file .gz (nhỏ hơn 80%)
```

**Solution 2**: Check network
```powershell
# Test connection
docker exec namenode ping -c 5 google.com
```

### Problem: Spark Out of Memory

**Solution**: Tăng executor memory
```powershell
# Trong csv_etl_job.py, sửa dòng:
.config("spark.executor.memory", "4g")  # Tăng từ 2g lên 4g
```

### Problem: CSV parse errors

**Solution**: Thêm error handling
```python
# Trong csv_etl_job.py:
df = spark.read \
    .option("mode", "DROPMALFORMED") \  # Skip bad rows
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .csv(input_path)
```

---

## 📚 Tài Liệu Liên Quan

1. **LARGE_FILE_ETL_GUIDE.md** - Chi tiết đầy đủ
2. **large_file_upload.py** - Script upload chunked
3. **csv_etl_job.py** - Spark ETL template
4. **spark_jobs/** - Folder chứa Spark jobs

---

## ✅ Checklist

- [x] File CSV lớn upload thành công lên HDFS
- [x] Spark job chạy không lỗi
- [x] Data đã được làm sạch (lọc [deleted])
- [x] Kết quả lưu dạng Parquet với partition
- [x] Query nhanh hơn 10x so với CSV
- [x] Tiết kiệm 80% storage

**🎉 Hoàn thành! Bạn đã xử lý thành công file CSV 2.5GB với 10 triệu dòng!**

---

**Version**: 1.0  
**Date**: 2025-10-15  
**Time to complete**: ~10 phút (upload 4 phút + ETL 3 phút + verify 3 phút)
