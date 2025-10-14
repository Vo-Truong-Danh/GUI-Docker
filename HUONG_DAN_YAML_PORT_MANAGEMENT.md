# Hướng Dẫn Sử Dụng Tính Năng YAML Port Management (Vietnamese)

## 🎯 Tổng Quan

Cải tiến mới cho phép bạn:
- ✅ Import cổng từ file YAML
- ✅ Export cổng ra file YAML
- ✅ Thêm cổng tùy chỉnh
- ✅ Xóa cổng không cần thiết
- ✅ Hỗ trợ Docker Compose format

## 📋 Cài Đặt

### 1. Cài đặt PyYAML (nếu chưa có)
```powershell
pip install pyyaml
```

### 2. Hoặc cài tất cả dependencies
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
pip install -r requirements.txt
```

## 🚀 Hướng Dẫn Sử Dụng

### 1️⃣ Import Cổng từ File YAML

**Bước 1**: Mở tab Settings trong ứng dụng

**Bước 2**: Click nút **"Load from YAML"**

**Bước 3**: Chọn file YAML chứa cấu hình cổng

**Bước 4**: Cổng sẽ được import tự động

#### Định dạng YAML hỗ trợ:

**Format 1: Chuẩn (Standard)**
```yaml
ports:
  spark_master_ui: 9090
  spark_worker_ui: 8081
  hdfs_namenode_ui: 9870
  jupyter: 8888
  custom_service: 3000
```

**Format 2: Phẳng (Flat)**
```yaml
spark_master_ui: 9090
spark_worker_ui: 8081
hdfs_namenode_ui: 9870
jupyter: 8888
```

**Format 3: Docker Compose**
```yaml
services:
  spark-master:
    ports:
      - "9090:8080"
  jupyter:
    ports:
      - "8888:8888"
```

### 2️⃣ Export Cổng ra File YAML

**Bước 1**: Cấu hình các cổng trong tab Settings

**Bước 2**: Click nút **"Save to YAML"**

**Bước 3**: Chọn vị trí và tên file

**Bước 4**: File YAML sẽ được tạo với format:

```yaml
# Spark Runner GUI - Port Configuration
# Generated: 2024-10-14 12:34:56
# Application: Spark Runner GUI V6.0

ports:
  spark_master_ui: 9090
  spark_worker_ui: 8081
  hdfs_namenode_ui: 9870
  hdfs_datanode_ui: 9864
  history_server: 18080
  jupyter: 8888
  custom_api: 5000
```

### 3️⃣ Thêm Cổng Tùy Chỉnh

**Bước 1**: Click nút **"Add Port"**

**Bước 2**: Nhập thông tin:
- **Port Name**: Tên cổng (vd: `api_server`, `database_ui`)
- **Port Number**: Số cổng (1024-65535)

**Bước 3**: Click **OK**

**Bước 4**: Cổng mới xuất hiện trong danh sách

#### Quy tắc đặt tên:
- ✅ Cho phép: `api_server`, `database_ui`, `custom_port_1`
- ❌ Không cho phép: `api server` (có dấu cách), `api-server` (có dấu gạch ngang)
- ❌ Không được trùng tên với cổng đã có

### 4️⃣ Xóa Cổng

**Bước 1**: Tìm cổng muốn xóa trong danh sách

**Bước 2**: Click nút **🗑️** bên cạnh cổng đó

**Bước 3**: Xác nhận xóa trong dialog

**Lưu ý**: Không thể xóa các cổng mặc định:
- spark_master_ui
- spark_worker_ui
- hdfs_namenode_ui
- hdfs_datanode_ui
- history_server
- jupyter

## 💡 Các Trường Hợp Sử Dụng Thực Tế

### Case 1: Backup Cấu Hình
```
1. Click "Save to YAML"
2. Lưu file: port_config_backup_2024_10_14.yaml
3. Khi cần restore: Click "Load from YAML" → Chọn file backup
```

### Case 2: Chia Sẻ Cấu Hình với Team
```
1. Export cấu hình hiện tại ra YAML
2. Gửi file cho team members
3. Team import file YAML vào Settings
```

### Case 3: Setup Từ Docker Compose
```
1. Có file docker-compose.yml sẵn
2. Click "Load from YAML"
3. Chọn docker-compose.yml
4. Cổng được parse tự động từ port mapping
```

### Case 4: Thêm Service Mới
```
1. Cần thêm API server port 5000
2. Click "Add Port"
3. Nhập: Name = "api_server", Port = "5000"
4. Click OK
5. Cổng mới sẵn sàng sử dụng
```

## ⚠️ Lưu Ý Quan Trọng

### 1. Phạm Vi Port Hợp Lệ
- Port phải trong khoảng **1024-65535**
- Port < 1024 là privileged ports (cần quyền root)

### 2. Lưu Cấu Hình
- Sau khi import/thêm/xóa port, nhớ click **"Save Settings"**
- Khởi động lại Docker containers để áp dụng thay đổi

### 3. Xung Đột Port
- Kiểm tra port không bị trùng với service khác
- Sử dụng "Test Connections" để kiểm tra port có hoạt động không

### 4. File YAML
- File phải có extension `.yaml` hoặc `.yml`
- Đảm bảo syntax YAML đúng (indent bằng space, không dùng tab)

## 🔧 Troubleshooting

### Lỗi: "Invalid YAML syntax"
**Nguyên nhân**: File YAML không đúng format

**Giải pháp**:
- Kiểm tra indent (dùng 2 hoặc 4 spaces)
- Không dùng tab để indent
- Dùng YAML validator online để check

### Lỗi: "Port must be between 1024 and 65535"
**Nguyên nhân**: Port number ngoài phạm vi

**Giải pháp**:
- Chọn port trong khoảng 1024-65535
- Tránh port < 1024 (yêu cầu quyền admin)

### Lỗi: "Port name already exists"
**Nguyên nhân**: Tên port bị trùng

**Giải pháp**:
- Đổi tên port khác
- Hoặc xóa port cũ trước khi thêm

### YAML không load
**Nguyên nhân**: Format không đúng hoặc thiếu section ports

**Giải pháp**:
- Kiểm tra file có section `ports:`
- Hoặc dùng flat format (key: value trực tiếp)

## 📝 Ví Dụ File YAML Hoàn Chỉnh

### Example 1: Development Environment
```yaml
# Development Ports Configuration
ports:
  # Spark Services
  spark_master_ui: 9090
  spark_worker_ui: 8081
  history_server: 18080
  
  # HDFS Services
  hdfs_namenode_ui: 9870
  hdfs_datanode_ui: 9864
  
  # Development Tools
  jupyter: 8888
  
  # Custom Services
  api_server: 5000
  database_ui: 8080
  monitoring_dashboard: 3000
```

### Example 2: Production Environment
```yaml
# Production Ports Configuration
ports:
  spark_master_ui: 19090
  spark_worker_ui: 18081
  hdfs_namenode_ui: 19870
  hdfs_datanode_ui: 19864
  history_server: 28080
  jupyter: 18888
```

### Example 3: Minimal Setup
```yaml
ports:
  spark_master_ui: 9090
  jupyter: 8888
```

## 🎓 Best Practices

### 1. Đặt Tên Port Rõ Ràng
```
✅ Good: api_server, database_admin, monitoring_ui
❌ Bad: port1, x, temp
```

### 2. Document Ports
```yaml
# Always add comments in YAML
ports:
  # Main Spark UI
  spark_master_ui: 9090
  
  # Development notebook
  jupyter: 8888
```

### 3. Version Control
```
- Lưu file YAML vào git
- Đặt tên có version: ports_v1.0.yaml
- Document thay đổi trong commit message
```

### 4. Separate Environments
```
ports_development.yaml
ports_staging.yaml
ports_production.yaml
```

## 📊 Demo Workflow

### Workflow 1: Setup Môi Trường Mới
```
1. Tạo file: dev_ports.yaml
2. Thêm cấu hình cổng cho dev environment
3. Import vào Settings: Load from YAML
4. Verify: Test Connections
5. Save: Click Save Settings
6. Restart Docker containers
```

### Workflow 2: Chuyển Từ Dev Sang Production
```
1. Export dev config: Save to YAML → dev_ports.yaml
2. Copy và edit: prod_ports.yaml (đổi số port)
3. Deploy production: Load from YAML → prod_ports.yaml
4. Verify và Save
```

## 🆘 Hỗ Trợ

### Nếu gặp vấn đề:
1. Kiểm tra file log: `run_spark_gui/logs/`
2. Verify syntax YAML online: https://www.yamllint.com/
3. Test connection với: "Test Connections" button
4. Check documentation: `SETTINGS_YAML_ENHANCEMENT.md`

## 🎉 Tính Năng Nâng Cao

### Auto-Backup
- Mỗi lần save settings, tự động tạo backup
- Location: `run_spark_gui/backups/`

### Keyboard Shortcuts (Future)
- Ctrl+L: Load from YAML
- Ctrl+S: Save to YAML
- Ctrl+A: Add Port

---

**Version**: 1.0  
**Last Updated**: 2024-10-14  
**Language**: Tiếng Việt  
**Author**: GitHub Copilot
