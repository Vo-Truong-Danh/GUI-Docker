# 🐳 Docker Compose Auto-Load - Quick Reference

## 🚀 TL;DR

**Vấn đề**: Parse sai port "8081:8080" → lấy 8080  
**Giải pháp**: Click **🐳 Load from Docker Compose** → lấy đúng 8081 ✅

---

## 📝 Usage

```
Settings Tab → Click "🐳 Load from Docker Compose" → Done!
```

---

## ✅ Test Results

```powershell
cd "d:\BaiTapSinhVien\TH BigData\GUI-Docker"
python test_docker_compose_autoload.py
```

**Result**: ✅ ALL TESTS PASSED (100%)

---

## 📊 Port Mapping

| Service | docker-compose.yml | Loaded Port | Status |
|---------|-------------------|-------------|--------|
| spark-master | `"8081:8080"` | `8081` | ✅ Correct |
| namenode | `"9870:9870"` | `9870` | ✅ Correct |

---

## 🎯 Key Points

1. **HOST port first**: `"8081:8080"` → lấy `8081`
2. **Auto-find file**: Tự động tìm `docker-compose.yml`
3. **One-click**: Không cần chọn file
4. **Service mapping**: Auto-map service names

---

## 📁 Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Docker config |
| `settings_tab_v4.py` | Settings UI (modified) |
| `DOCKER_COMPOSE_AUTO_LOAD.md` | Full docs |
| `test_docker_compose_autoload.py` | Tests |

---

## ⚡ Quick Test

```powershell
# 1. Run app
python run_spark_gui/main.py

# 2. In Settings tab:
#    Click "🐳 Load from Docker Compose"

# 3. Verify:
#    spark_master_ui = 8081 ✅
#    hdfs_namenode_ui = 9870 ✅
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| File not found | Check `docker-compose.yml` exists |
| Wrong port | Verify format: `"HOST:CONTAINER"` |
| YAML error | Check syntax at yamllint.com |

---

**Status**: ✅ Ready | **Version**: 2.0 | **Tests**: 100% Pass
