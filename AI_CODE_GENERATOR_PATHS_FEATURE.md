# 🔄 AI Code Generator - Auto-Save Input/Output Paths

## 📋 Tổng Quan

Tính năng **tự động lưu và khôi phục** đường dẫn Input File và Output Path trong tab AI Code Generator, giúp bạn không phải nhập lại mỗi lần sử dụng.

---

## ✨ Tính Năng Mới

### 1. **Auto-Save Paths** (Lưu Tự Động)
- ✅ Tự động lưu khi bạn thay đổi Input File
- ✅ Tự động lưu khi bạn thay đổi Output Path
- ✅ Lưu ngay lập tức, không cần nhấn nút Save
- ✅ Lưu vào file `spark_runner_config.json`

### 2. **Auto-Load Paths** (Khôi Phục Tự Động)
- ✅ Khi mở GUI lại, tự động load đường dẫn đã lưu
- ✅ Hiển thị đường dẫn cuối cùng bạn đã sử dụng
- ✅ Không cần thiết lập lại từ đầu

---

## 🎯 Cách Sử Dụng

### **Bước 1: Nhập Input File**
```
hdfs://namenode:9000/data/input.csv
```
→ Đường dẫn này **tự động được lưu** khi bạn nhập xong

### **Bước 2: Nhập Output Path**
```
hdfs://namenode:9000/output
```
→ Đường dẫn này **tự động được lưu** khi bạn nhập xong

### **Bước 3: Đóng GUI và Mở Lại**
→ Các đường dẫn **tự động được khôi phục** về giá trị bạn đã nhập trước đó

---

## 📁 Nơi Lưu Trữ

### **File Config**
```
run_spark_gui/spark_runner_config.json
```

### **Cấu Trúc JSON**
```json
{
  "ai_code_generator": {
    "last_input_file": "hdfs://namenode:9000/data/input.csv",
    "last_output_path": "hdfs://namenode:9000/output"
  }
}
```

---

## 🔧 Chi Tiết Kỹ Thuật

### **Code Implementation**

#### 1. **Load Saved Paths (Khởi động)**
```python
def load_saved_paths(self):
    """Load saved input/output paths from config"""
    self.saved_input = self.config.get('ai_code_generator', {}).get(
        'last_input_file', 
        'hdfs://namenode:9000/data/input.csv'
    )
    self.saved_output = self.config.get('ai_code_generator', {}).get(
        'last_output_path', 
        'hdfs://namenode:9000/output'
    )
```

#### 2. **Save Paths (Khi thay đổi)**
```python
def save_paths_to_config(self):
    """Save current input/output paths to config"""
    if 'ai_code_generator' not in self.config:
        self.config['ai_code_generator'] = {}
    
    self.config['ai_code_generator']['last_input_file'] = self.input_file_var.get()
    self.config['ai_code_generator']['last_output_path'] = self.output_file_var.get()
    
    # Save to file
    import json
    config_path = os.path.join(os.path.dirname(__file__), 'spark_runner_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(self.config, f, indent=4, ensure_ascii=False)
```

#### 3. **Auto-Save Trigger (Kích hoạt)**
```python
# Trace variable changes
self.input_file_var.trace_add('write', lambda *args: self.save_paths_to_config())
self.output_file_var.trace_add('write', lambda *args: self.save_paths_to_config())
```

---

## 📊 Luồng Hoạt Động

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GUI Khởi Động                                            │
│    └─> load_saved_paths()                                   │
│        └─> Đọc spark_runner_config.json                     │
│            └─> Khôi phục last_input_file, last_output_path  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. User Nhập Input/Output                                   │
│    └─> Gõ vào Entry widget                                  │
│        └─> trace_add() trigger                              │
│            └─> save_paths_to_config()                       │
│                └─> Ghi vào spark_runner_config.json         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Đóng GUI                                                  │
│    └─> Config đã được lưu                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Mở GUI Lại                                               │
│    └─> load_saved_paths()                                   │
│        └─> Hiển thị đường dẫn đã lưu                        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Lợi Ích

| Trước Đây | Bây Giờ |
|-----------|---------|
| ❌ Phải nhập lại Input mỗi lần | ✅ Tự động nhớ Input |
| ❌ Phải nhập lại Output mỗi lần | ✅ Tự động nhớ Output |
| ❌ Mất thời gian thiết lập | ✅ Tiết kiệm thời gian |
| ❌ Dễ nhập sai | ✅ Sử dụng lại đường dẫn đúng |

---

## 🎨 Demo Workflow

### **Lần 1: Thiết Lập**
```
1. Mở GUI
2. Chọn template "Word Count"
3. Nhập Input: hdfs://namenode:9000/data/harypotter.txt
4. Nhập Output: hdfs://namenode:9000/output/wordcount
5. Generate Code
   → Config được lưu tự động
6. Đóng GUI
```

### **Lần 2: Sử Dụng Lại**
```
1. Mở GUI
2. Tab AI Code Generator tự động hiển thị:
   ✓ Input: hdfs://namenode:9000/data/harypotter.txt
   ✓ Output: hdfs://namenode:9000/output/wordcount
3. Không cần nhập lại!
4. Có thể chỉnh sửa nếu muốn → Tự động lưu lại
```

---

## 🔍 Kiểm Tra Config

### **Xem File Config**
```bash
# Windows PowerShell
cat run_spark_gui/spark_runner_config.json
```

### **Expected Output**
```json
{
  "hdfs_url": "hdfs://namenode:9000",
  "namenode_host": "namenode",
  "namenode_port": 9870,
  "ports": { ... },
  "ai_code_generator": {
    "last_input_file": "hdfs://namenode:9000/data/harypotter.txt",
    "last_output_path": "hdfs://namenode:9000/output/wordcount"
  }
}
```

---

## 🛠️ Troubleshooting

### **Vấn Đề 1: Đường dẫn không được lưu**
**Nguyên nhân:** File config không có quyền ghi

**Giải pháp:**
```bash
# Check file permissions
ls -l run_spark_gui/spark_runner_config.json

# Fix permissions (Linux/Mac)
chmod 644 run_spark_gui/spark_runner_config.json
```

### **Vấn Đề 2: Đường dẫn không được load**
**Nguyên nhân:** Cấu trúc JSON bị lỗi

**Giải pháp:**
```bash
# Validate JSON
python -m json.tool run_spark_gui/spark_runner_config.json

# Reset config if needed
cp spark_runner_config.json.backup spark_runner_config.json
```

### **Vấn Đề 3: Muốn reset về mặc định**
**Giải pháp:**
```json
// Xóa section ai_code_generator trong spark_runner_config.json
{
  "ai_code_generator": {
    // Delete this section or set to default
  }
}
```

---

## 📝 Changelog

### **Version 4.3.0** (Current)
- ✅ Added auto-save Input File
- ✅ Added auto-save Output Path
- ✅ Added auto-load on startup
- ✅ Integration with spark_runner_config.json
- ✅ Real-time save using trace_add()

---

## 🎯 Next Steps

1. **Test đầy đủ:**
   - Nhập Input/Output → Đóng GUI → Mở lại → Kiểm tra
   - Thay đổi giá trị → Kiểm tra config file
   
2. **Sử dụng thực tế:**
   - Chạy các template khác nhau
   - Lưu đường dẫn cho từng project
   
3. **Mở rộng (Optional):**
   - Lưu Job Name
   - Lưu Template Selection
   - Lưu Extra Parameters

---

## 📞 Support

Nếu có vấn đề:
1. Kiểm tra `spark_runner_config.json`
2. Xem log trong terminal
3. Test với đường dẫn mặc định trước

**Tác giả:** Spark Runner GUI Team  
**Version:** 4.3.0  
**Ngày cập nhật:** 2025-10-13
