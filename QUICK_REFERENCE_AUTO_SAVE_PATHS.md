# 🚀 Quick Reference: Auto-Save Input/Output Paths

## ⚡ Tóm Tắt Nhanh

### **Tính Năng**
- ✅ Tự động lưu Input File khi nhập
- ✅ Tự động lưu Output Path khi nhập
- ✅ Tự động load lại khi mở GUI

### **Lưu Ở Đâu?**
```
run_spark_gui/spark_runner_config.json
```

### **Cấu Trúc**
```json
{
  "ai_code_generator": {
    "last_input_file": "hdfs://...",
    "last_output_path": "hdfs://..."
  }
}
```

---

## 🎯 Workflow Siêu Nhanh

```
1. Nhập Input  → Auto-save ✓
2. Nhập Output → Auto-save ✓
3. Đóng GUI   → Config saved ✓
4. Mở GUI     → Auto-load ✓
```

---

## 🔥 Tips

### **Tip 1: Không cần Save**
Chỉ cần gõ vào Input/Output → Tự động lưu ngay!

### **Tip 2: Thay đổi bất cứ lúc nào**
Mỗi khi bạn sửa → Tự động update config

### **Tip 3: Kiểm tra config**
```bash
cat run_spark_gui/spark_runner_config.json | grep ai_code
```

---

## 📊 So Sánh

| Trước | Sau |
|-------|-----|
| Nhập lại mỗi lần | Tự động nhớ |
| Mất 30 giây | Tiết kiệm 100% |
| Dễ sai | Dùng lại đúng |

---

## ✅ Test Ngay

1. Mở GUI
2. Chuyển sang tab **AI Code Generator**
3. Nhập Input: `hdfs://namenode:9000/data/test.csv`
4. Nhập Output: `hdfs://namenode:9000/output/test`
5. Đóng GUI
6. Mở lại → Kiểm tra xem có tự động load không

**Expected:** ✅ Input và Output tự động hiển thị giá trị bạn vừa nhập!

---

**Version:** 4.3.0  
**Created:** 2025-10-13  
**Feature:** Auto-Save Input/Output Paths
