# 🎯 ULTRA LOW DISK - Skip Arguments Guide

## ✅ ĐÃ SỬA LỖI & THÊM TÍNH NĂNG MỚI

### 🔧 Các vấn đề đã sửa:

1. **Lỗi Column Name trong Evaluation** ✅
   - Model dùng `userCol="user"` nhưng evaluation dùng `playlist_idx`
   - Đã sửa: Rename column trước khi gọi `recommendForUserSubset()`

2. **Thiếu Arguments `--skip_training` và `--skip_evaluation`** ✅
   - Đã thêm 2 arguments mới vào argparse

3. **Hiển thị Progress** ✅
   - Thêm thông tin về Spark UI và checkpoints
   - Set log level thành INFO để thấy iterations
   - Hiển thị estimated time

---

## 📝 ARGUMENTS MỚI

### `--skip_training`
**Công dụng:** Bỏ qua training, chỉ load model có sẵn

**Khi nào dùng:**
- Model đã được train rồi
- Chỉ muốn chạy evaluation lại
- Chỉ muốn generate submission với model cũ

**Ví dụ:**
```bash
docker exec gui-docker-spark-worker-2 /spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/spotify_rec_ULTRA_LOW_DISK.py \
  --skip_training
```

---

### `--skip_evaluation`
**Công dụng:** Bỏ qua evaluation (MAP@500), chỉ train model

**Khi nào dùng:**
- Chỉ quan tâm training model, không cần đánh giá
- Tiết kiệm thời gian (evaluation mất ~15-20 phút)
- Khi ổ đĩa sắp đầy, chỉ cần model

**Ví dụ:**
```bash
docker exec gui-docker-spark-worker-2 /spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/spotify_rec_ULTRA_LOW_DISK.py \
  --rank 120 --maxIter 40 \
  --skip_evaluation
```

---

### Kết hợp cả 2 flags
**Công dụng:** Chỉ load model (không train, không evaluate)

**Khi nào dùng:**
- Kiểm tra xem model có tồn tại không
- Chuẩn bị cho bước generate submission

**Ví dụ:**
```bash
docker exec gui-docker-spark-worker-2 /spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /tmp/spotify_rec_ULTRA_LOW_DISK.py \
  --skip_training --skip_evaluation
```

---

## 🎬 SỬ DỤNG TRONG GUI

### Custom Args Field:
```
--skip_training --skip_evaluation
```

**Hoặc chỉ skip training:**
```
--skip_training
```

**Hoặc chỉ skip evaluation:**
```
--skip_evaluation
```

**Với custom parameters:**
```
--rank 120 --maxIter 40 --skip_evaluation
```

---

## 📊 OUTPUT KHI DÙNG SKIP FLAGS

### Khi `--skip_training`:
```
⏭️  SKIPPING TRAINING (loading existing model)...
✅ Model loaded from hdfs://namenode:8020/output/model/als_model

📊 EVALUATING MAP@500...
✅ MAP@500: 0.0348 (3.48%) in 12.3 min

================================================================================
✅ MODEL LOADED & EVALUATION COMPLETE!
================================================================================
📊 Final MAP@500: 0.0348 (3.48%)
💾 Model path: hdfs://namenode:8020/output/model/als_model
🔧 Parameters: rank=100, alpha=55.0, regParam=0.025, maxIter=38
================================================================================
```

### Khi `--skip_evaluation`:
```
🎓 TRAINING ALS MODEL (ULTRA LOW DISK MODE)...
   Rank: 120 | MaxIter: 40 | RegParam: 0.05 | Alpha: 50.0

   📊 Monitor progress:
   - Spark UI: http://localhost:4040 (detailed stages)
   - Logs below (iteration checkpoints)

   🚀 Training started (target: 40 iterations)...
   ⏱️  Expected time: ~32-48 minutes
   💡 Checkpoints every 5 iterations (you'll see logs)

INFO ALS: Iteration 0
INFO ALS: Iteration 1
...
✅ MODEL TRAINED (45.2 min)

⏭️  SKIPPING EVALUATION

================================================================================
✅ TRAINING COMPLETE (EVALUATION SKIPPED)
================================================================================
💾 Model path: hdfs://namenode:8020/output/model/als_model
🔧 Parameters: rank=120, alpha=50.0, regParam=0.05, maxIter=40
================================================================================
```

### Khi cả 2 flags:
```
⏭️  SKIPPING TRAINING (loading existing model)...
✅ Model loaded from hdfs://namenode:8020/output/model/als_model

⏭️  SKIPPING EVALUATION

================================================================================
✅ MODEL LOADED (TRAINING & EVALUATION SKIPPED)
================================================================================
💾 Model path: hdfs://namenode:8020/output/model/als_model
🔧 Parameters: rank=100, alpha=55.0, regParam=0.025, maxIter=38
================================================================================
```

---

## 🔍 PROGRESS MONITORING

### Trong Spark UI (http://localhost:4040):
1. **Jobs Tab:** Xem tổng số jobs và tiến độ
2. **Stages Tab:** Xem chi tiết từng stage (iteration)
3. **Storage Tab:** Xem checkpoints đang lưu
4. **Executors Tab:** Xem CPU/Memory usage

### Trong Console Logs:
```
INFO ALS: Iteration 0
INFO ALS: Iteration 1
INFO ALS: Iteration 2
INFO ALS: Iteration 3
INFO ALS: Iteration 4
INFO ALS: Iteration 5 (checkpoint saved)  ← Checkpoint every 5 iterations
...
```

---

## 💡 TIPS

1. **Muốn train nhanh chỉ để test:**
   ```
   --rank 50 --maxIter 10 --skip_evaluation
   ```

2. **Đã train xong, chỉ cần đánh giá lại:**
   ```
   --skip_training
   ```

3. **Chỉ cần model, không cần score:**
   ```
   --skip_evaluation
   ```

4. **Tiết kiệm tối đa thời gian:**
   ```
   --rank 80 --maxIter 20 --skip_evaluation
   ```

---

## 🆕 VERSION HISTORY

**v1.2** (2025-10-29)
- ✅ Added `--skip_training` argument
- ✅ Added `--skip_evaluation` argument
- ✅ Fixed column name mismatch in evaluation
- ✅ Added progress monitoring info
- ✅ Set log level to INFO during training
- ✅ Added estimated training time display

**v1.1** (2025-10-29)
- Initial ULTRA LOW DISK version
- Optimized for rank 80-150

---

## 📞 TROUBLESHOOTING

**Q: Model not found khi dùng `--skip_training`**
- A: Chạy training ít nhất 1 lần để tạo model

**Q: Evaluation vẫn chạy dù có `--skip_evaluation`**
- A: Kiểm tra xem có copy file mới vào container chưa:
  ```bash
  docker cp "code python/spotify_rec_ULTRA_LOW_DISK.py" gui-docker-spark-worker-2:/tmp/
  ```

**Q: Không thấy iteration logs**
- A: Mở Spark UI: http://localhost:4040

---

✅ **File đã cập nhật:** `spotify_rec_ULTRA_LOW_DISK.py`
✅ **Đã copy vào container:** `/tmp/spotify_rec_ULTRA_LOW_DISK.py`
✅ **Sẵn sàng chạy trong GUI!**




