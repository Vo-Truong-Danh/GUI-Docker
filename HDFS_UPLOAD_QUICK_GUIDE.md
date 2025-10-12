# 🚀 HDFS Upload - Quick Reference Guide (v4.2.4)

## 📊 What's New in v4.2.4

### ✅ Enhanced Logging
- **Timestamp** trên mọi log message: `[14:23:15]`
- **Detailed progress** cho mọi action
- **Docker commands** được hiển thị trước khi execute
- **Return codes** và output được log ra

### ✅ Config Management
- Show **absolute path** của config file khi khởi động
- Show **full path** khi save config
- Config file: `spark_runner_config.json` trong thư mục app

### ✅ Better Error Messages
- Specific error types (timeout, Docker not found, etc.)
- Actionable suggestions
- Context information

---

## 🎯 Quick Start

### 1. Test Connection
```
[14:23:15] 🔍 Testing HDFS connection...
[14:23:15] 📦 Container: namenode
[14:23:15] 💻 Executing: docker exec namenode hdfs dfs -ls /
[14:23:15] 🔄 Starting test in background thread...
[14:23:16] Return code: 0
[14:23:16] ✅ Connection successful!
```

**Steps:**
1. Click "🔍 Test" button
2. Watch log for detailed progress
3. Success dialog if connected
4. Check HDFS directory listing

### 2. Add Files
```
[14:25:10] 📂 Opening file dialog...
[14:25:12] ➕ Added: test_data.csv
[14:25:12] ➕ Added: sample.json
[14:25:12] ✅ Total added: 2 file(s)
```

**Steps:**
1. Click "➕ Add Files" or "📂 Add Folder"
2. Select files/folder
3. See detailed list with names
4. Duplicate warnings if file already added

### 3. Upload Files
```
============================================================
[14:26:30] ▶ Starting upload of 2 file(s)
[14:26:30] 📦 Container: namenode
[14:26:30] 📁 HDFS Path: /user/spark/data
============================================================
[14:26:30] 🔄 Starting upload in background thread...

[14:26:31] [1/2] 📤 Uploading: test_data.csv
[14:26:31]       Size: 1024.5 KB
[14:26:31]       Step 1/3: Copy to container
[14:26:31]       💻 $ docker cp "test_data.csv" namenode:/tmp/
[14:26:32]       ✓ Copied to container /tmp/
[14:26:32]       Step 2/3: Upload to HDFS
[14:26:32]       💻 $ hdfs dfs -put /tmp/test_data.csv /user/spark/data
[14:26:33]       ✓ Uploaded to HDFS
[14:26:33]       📍 Location: /user/spark/data/test_data.csv
[14:26:33]       Step 3/3: Cleanup temp file
[14:26:33]       ✓ Cleaned up /tmp/test_data.csv

============================================================
[14:27:00] 📊 Upload Summary
[14:27:00]    ✅ Success: 2
[14:27:00]    ❌ Failed: 0
[14:27:00]    📁 Total: 2
============================================================
```

**Steps:**
1. Add files first
2. Click "▶ Upload to HDFS"
3. Watch detailed step-by-step progress
4. See summary at end
5. Success dialog when complete

### 4. Save Config
```
[14:28:00] ✓ Configuration saved to D:\...\spark_runner_config.json
```

**Steps:**
1. Modify settings (container, path, etc.)
2. Click "💾 Save Config"
3. See absolute path in confirmation dialog
4. Config saved with UTF-8 encoding

---

## 📁 Config File Management

### Default Location
```
D:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui\spark_runner_config.json
```

### Config Structure
```json
{
    "hdfs_container": "namenode",
    "hdfs_path": "/user/spark/data",
    "auto_extract": true
}
```

### How to Find Config File
1. **Check startup log:**
   ```
   [14:20:00] 📁 Config file: D:\...\spark_runner_config.json
   ```

2. **Save config and check dialog:**
   - Click "💾 Save Config"
   - Dialog shows absolute path

3. **Manual check:**
   - Navigate to app directory
   - Look for `spark_runner_config.json`

### How to Backup Config
```powershell
# PowerShell
cd "D:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui"
Copy-Item spark_runner_config.json spark_runner_config.json.backup
```

### How to Share Config
1. Locate config file (see above)
2. Copy `spark_runner_config.json` 
3. Send to teammate
4. They place it in their app directory

---

## 🔍 Troubleshooting

### Problem: Log không hiện gì khi bấm nút
**Solution:**
- Check if app started successfully
- Look for startup messages:
  ```
  [14:20:00] 📤 HDFS Upload Manager ready
  [14:20:00] 📁 Config file: ...
  ```
- If no messages → Check console for errors

### Problem: "Docker not found" error
**Log:**
```
[14:30:00] ❌ Docker command not found. Is Docker installed?
```

**Solution:**
1. Check if Docker Desktop is running
2. Run in PowerShell: `docker --version`
3. If not found → Install Docker Desktop
4. Restart app after Docker installed

### Problem: Connection timeout
**Log:**
```
[14:30:00] ❌ Connection timeout (10s)
```

**Solution:**
1. Check if Docker containers running: `docker ps`
2. Check if namenode container exists
3. Check container name matches config
4. Try longer timeout (modify code if needed)

### Problem: Upload fails
**Log:**
```
[14:30:00] ❌ HDFS upload failed: File exists
```

**Solution:**
1. Check log for exact error message
2. Common issues:
   - File already exists in HDFS
   - Permission denied
   - HDFS full
   - Wrong path
3. Try different filename or path

### Problem: Config không save
**Solution:**
1. Check if file is read-only
2. Check if you have write permission
3. Check disk space
4. See error message in log for details

---

## 📊 Log Message Types

### Success (Green)
```
[14:20:00] ✅ Connection successful!
[14:20:00] ✓ Uploaded to HDFS
```

### Error (Red)
```
[14:20:00] ❌ Connection failed: Container not found
[14:20:00] ❌ Docker command not found
```

### Warning (Yellow)
```
[14:20:00] ⚠️ Already added: test.csv
[14:20:00] ⏹ Upload cancelled by user
```

### Info (Blue)
```
[14:20:00] 🔍 Testing HDFS connection...
[14:20:00] 📦 Container: namenode
```

### Normal (White)
```
[14:20:00] 💻 $ docker exec namenode hdfs dfs -ls /
[14:20:00] Output: drwxr-xr-x ...
```

---

## 🎨 UI Elements

### Status Badges
- **● Ready** (Gray) - Sẵn sàng
- **● Testing...** (Blue) - Đang test
- **● Connected** (Green) - Kết nối thành công
- **● Uploading...** (Blue) - Đang upload
- **● Complete** (Green) - Hoàn thành
- **● Error** (Red) - Lỗi
- **● Timeout** (Red) - Timeout
- **● Stopping...** (Yellow) - Đang dừng

### Buttons
- **🔍 Test** - Test HDFS connection
- **💾 Save Config** - Save configuration
- **➕ Add Files** - Add files to upload
- **📂 Add Folder** - Add entire folder
- **▶ Upload to HDFS** - Start upload
- **⏹ Stop Upload** - Cancel upload
- **🗑️ Clear All** - Clear file list

---

## ⚡ Tips & Tricks

### 1. Monitor Progress
- Watch log for real-time updates
- Check status badge color
- Look for [x/y] progress indicators

### 2. Debug Issues
- Timestamp helps identify when error occurred
- Docker commands shown → can copy & test manually
- Return codes indicate success (0) or failure (non-zero)

### 3. Efficient Workflow
1. Test connection first
2. Add files/folders
3. Check file list (count)
4. Upload with one click
5. Monitor detailed progress
6. Check summary

### 4. Config Management
- Save config after changes
- Note absolute path from dialog
- Backup before major changes
- Share config with team

---

## 📈 Performance Tips

### Large Files
- Upload shows progress per file
- Timeout is 60 seconds per file
- Consider splitting very large files

### Many Files
- Progress shown as [1/100], [2/100], etc.
- Can stop upload mid-way
- Summary shows success/fail counts

### Batch Operations
- Add entire folder at once
- Duplicate check prevents re-adding
- Clear all for fresh start

---

## 🆘 Getting Help

### Check Logs First
1. Look at timestamp to identify when issue occurred
2. Read error message carefully
3. Check docker command that failed
4. Note return code

### Common Solutions
- Docker not running → Start Docker Desktop
- Container not found → Check docker ps
- Permission denied → Check HDFS permissions
- File exists → Use different name or remove old file

### Report Issues
Include:
1. Timestamp of error
2. Full error message from log
3. Docker command that failed
4. Config settings
5. Docker container status

---

**Version:** 4.2.4  
**Last Updated:** October 12, 2025  
**Status:** ✅ Production Ready
