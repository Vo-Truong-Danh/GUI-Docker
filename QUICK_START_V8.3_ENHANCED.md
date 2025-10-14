# 🚀 QUICK START - V8.3 Enhanced

## ✨ 3 Tính Năng Mới

1. ✅ **Lưu file Python** (Save/Copy/Run buttons)
2. ✅ **Lưu API key** (không cần nhập lại)
3. ✅ **Chỉ in code Python** (không in verbose)

---

## 📖 Hướng Dẫn Sử Dụng

### Bước 1: Khởi động GUI

```powershell
cd "D:\BaiTapSinhVien\TH BigData\GUI-Docker"
python run_spark_gui/main.py
```

### Bước 2: Initialize AI Engine (Lần đầu)

1. **Chọn tab**: `🤖 AI Engine V8.3`

2. **Cấu hình**:
   - AI Provider: **"Gemini 2.5 Flash (Free)"**
   - API Key: Paste key của bạn (hoặc để trống dùng free tier)

3. **Click**: `🚀 Initialize Engine`

4. **Kết quả**:
   ```
   ✅ AI Engine V8.3 initialized!
   
   Provider: google_gemini_25_flash
   Temperature: 0.0
   API Key: Saved ✅
   ```

**Lưu ý**: API key đã được lưu! Lần sau không cần nhập lại.

---

### Bước 3: Generate Code

1. **Browse HDFS File**:
   - Click: `📂 Browse`
   - Navigate: `/` → `input` → `harrypotter.txt`
   - Click: `✅ Select`

2. **Nhập câu hỏi**:
   ```
   Count word 'snape' in file
   ```

3. **Click**: `🚀 Generate PySpark Code`

4. **Kết quả** (CHỈ CODE, KHÔNG CÓ GIẢI THÍCH):
   ```python
   from pyspark.sql import SparkSession
   
   spark = SparkSession.builder.appName("CountSnape").getOrCreate()
   text_rdd = spark.sparkContext.textFile("hdfs://namenode:8020/input/harrypotter.txt")
   snape_count = text_rdd \
       .flatMap(lambda line: line.lower().split()) \
       .filter(lambda word: word == "snape") \
       .count()
   print(f"Count of 'snape': {snape_count}")
   spark.stop()
   ```

**Không còn**: "Tuyệt vời! Đây là code...", "### Giải thích:", etc.

---

### Bước 4: Save/Copy/Run Code

**Option 1: Copy to Clipboard**
```
Click: 📋 Copy Code
→ Paste anywhere: Ctrl+V
```

**Option 2: Save to File**
```
Click: 💾 Save to File
→ Choose location: D:/my_pyspark_code.py
→ Result: ✅ File saved
```

**Option 3: Run Immediately**
```
Click: ▶️ Run Code
→ Confirm: Yes
→ Result: Terminal opens, code runs
```

---

## 🔄 Lần Sau Sử Dụng

**Không cần setup lại!**

```powershell
# 1. Khởi động
python run_spark_gui/main.py

# 2. Tab "🤖 AI Engine V8.3"
# → API key đã được load sẵn ✅

# 3. Click "🚀 Initialize Engine"
# → Ready!

# 4. Generate code như bình thường
```

---

## 💡 Tips & Tricks

### Tip 1: Quick Examples

Click các example có sẵn:
- ✅ "Count word 'snape' in file"
- ✅ "Top 20 most frequent words"
- ✅ "Count total words in text file"
- ✅ "Find lines containing 'harry'"

### Tip 2: Code-Only Output

Nếu vẫn thấy verbose text:
- Check temperature = 0.0 ✅
- Check provider = Gemini 2.5 Flash ✅
- Code extraction tự động loại bỏ:
  - Markdown headers (`##`)
  - Giải thích (`**Note:`, `### Explanation`)
  - Comments dài dòng

### Tip 3: Run Code với Docker

Nếu code dùng HDFS:
```powershell
# Đảm bảo Docker đang chạy
docker ps | Select-String "namenode"

# Nếu chưa chạy
docker-compose up -d

# Wait 30s, test
python test_hdfs_connection.py
```

---

## 🐛 Troubleshooting

### Issue 1: API Key không được lưu

**Symptom**: Mỗi lần mở GUI phải nhập lại API key

**Solution**:
```powershell
# Check config file
cat run_spark_gui/spark_runner_config.json

# Should contain:
# "ai_api_key": "AIza...",
# "ai_provider": "Gemini 2.5 Flash (Free)"
```

**Fix**: Click "Initialize Engine" 1 lần nữa để lưu.

---

### Issue 2: Vẫn thấy verbose text

**Symptom**: Output có cả giải thích dài dòng

**Solution**:
1. Check temperature: Phải là **0.0**
2. Check provider: Dùng **Gemini 2.5 Flash (Free)**
3. Restart GUI

**Debug**:
```python
# Check trong console log:
🔧 Selected: Gemini 2.5 Flash (Free)
🔧 Mapped to: AIProvider.GOOGLE_GEMINI_25_FLASH
```

---

### Issue 3: Run Code không mở terminal

**Symptom**: Click "Run Code" nhưng không thấy terminal

**Solution (Windows)**:
```powershell
# Manual run
python generated_code.py

# Or in PowerShell
start cmd /k python "path/to/code.py"
```

---

## 📊 Feature Comparison

| Feature | Before V8.3 | V8.3 Enhanced |
|---------|-------------|---------------|
| Save code | ❌ No | ✅ Yes |
| Copy code | ❌ Manual | ✅ Button |
| Run code | ❌ Manual | ✅ 1-click |
| API key | ❌ Re-enter | ✅ Auto-load |
| Output | ❌ Verbose | ✅ Code-only |

---

## ✅ Checklist

**Lần đầu setup**:
- [ ] Run GUI
- [ ] Enter API key
- [ ] Click "Initialize Engine"
- [ ] Check: "API Key: Saved ✅"

**Mỗi lần dùng**:
- [ ] Run GUI
- [ ] API key auto-load ✅
- [ ] Initialize engine
- [ ] Browse HDFS file
- [ ] Enter question
- [ ] Generate code → Chỉ thấy code!
- [ ] Save/Copy/Run code

---

## 🎯 Examples

### Example 1: Word Count
```
Question: Count word 'harry' in file
HDFS File: /input/harrypotter.txt

Generated Code:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("CountHarry").getOrCreate()
rdd = spark.sparkContext.textFile("hdfs://namenode:8020/input/harrypotter.txt")
count = rdd.flatMap(lambda line: line.lower().split()).filter(lambda w: w == "harry").count()
print(f"Harry count: {count}")
spark.stop()
```
```

### Example 2: Top 20 Words
```
Question: Top 20 most frequent words
HDFS File: /input/harrypotter.txt

Generated Code:
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Top20Words").getOrCreate()
rdd = spark.sparkContext.textFile("hdfs://namenode:8020/input/harrypotter.txt")
word_counts = rdd \
    .flatMap(lambda line: line.lower().split()) \
    .map(lambda word: (word, 1)) \
    .reduceByKey(lambda a, b: a + b) \
    .sortBy(lambda x: x[1], ascending=False) \
    .take(20)
    
for word, count in word_counts:
    print(f"{word}: {count}")
    
spark.stop()
```
```

---

## 🔗 Related Docs

- **Full features**: `FEATURES_V8.3_ENHANCED.md`
- **Bug fixes**: `FIXES_SUMMARY_V8.3.md`
- **Test script**: `TEST_NEW_FEATURES.py`

---

**Version**: V8.3 Enhanced  
**Date**: October 14, 2025  
**Status**: ✅ Ready to use!
