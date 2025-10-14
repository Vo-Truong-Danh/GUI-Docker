# 🎯 YAML Port Management - Quick Reference

## 🚀 Quick Commands

### Install Dependencies
```powershell
pip install pyyaml
```

### Run Application
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
python main.py
```

### Run Tests
```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
python test_yaml_port_management.py
```

## 📝 YAML Format Examples

### Standard Format (Recommended)
```yaml
ports:
  spark_master_ui: 9090
  jupyter: 8888
  custom_api: 5000
```

### Flat Format
```yaml
spark_master_ui: 9090
jupyter: 8888
```

### Docker Compose Format
```yaml
services:
  spark-master:
    ports:
      - "9090:8080"
```

## 🎮 UI Operations

### In Settings Tab:

| Button | Action |
|--------|--------|
| **Load from YAML** | Import ports from YAML file |
| **Save to YAML** | Export ports to YAML file |
| **Add Port** | Add custom port (dialog) |
| **🗑️** | Delete specific port |
| **Save Settings** | Save all changes |
| **Reset to Default** | Restore default ports |
| **Test Connections** | Check port accessibility |

## ✅ Port Validation Rules

| Rule | Valid | Invalid |
|------|-------|---------|
| Range | 1024-65535 | <1024, >65535 |
| Name | `api_server` | `api server` (space) |
| Duplicate | First one | Same name twice |

## 🛡️ Protected Ports (Cannot Delete)
- `spark_master_ui`
- `spark_worker_ui`
- `hdfs_namenode_ui`
- `hdfs_datanode_ui`
- `history_server`
- `jupyter`

## 📁 Key Files

| File | Purpose |
|------|---------|
| `run_spark_gui/settings_tab_v4.py` | Main implementation |
| `example_port_config.yaml` | Example YAML file |
| `HUONG_DAN_YAML_PORT_MANAGEMENT.md` | Vietnamese guide |
| `SETTINGS_YAML_ENHANCEMENT.md` | Technical docs |
| `test_yaml_port_management.py` | Test suite |

## ⚡ Common Workflows

### Backup Config
```
Settings → Save to YAML → Save as backup_YYYYMMDD.yaml
```

### Import Config
```
Settings → Load from YAML → Select file → Ports updated
```

### Add Custom Port
```
Settings → Add Port → Enter name & number → OK
```

### Share Config
```
Export YAML → Send to team → Team imports YAML
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Invalid YAML" | Check syntax at yamllint.com |
| "Port out of range" | Use 1024-65535 |
| "Port name exists" | Use different name |
| "Cannot delete" | It's a protected default port |

## 📞 Need Help?

1. Read: `HUONG_DAN_YAML_PORT_MANAGEMENT.md`
2. Check: `run_spark_gui/logs/`
3. Test: Run `test_yaml_port_management.py`

## 🎓 Example: Complete Setup

```powershell
# 1. Install
pip install pyyaml

# 2. Run app
python run_spark_gui/main.py

# 3. In Settings Tab:
#    a. Load example_port_config.yaml
#    b. Add custom port: api_server = 5000
#    c. Save to YAML: my_config.yaml
#    d. Click "Save Settings"

# 4. Done! ✅
```

---

**Quick Help**: All tests passed ✅ | Ready to use 🚀 | Documentation complete 📚
