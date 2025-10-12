# 📝 Docker Compose Editor - User Guide

## 🎯 Overview

Docker Compose Editor tab cho phép bạn:
- ✅ Edit docker-compose.yml với syntax highlighting
- ✅ Validate YAML syntax realtime
- ✅ Start/Stop compose services trực tiếp
- ✅ View services status
- ✅ Backup files
- ✅ Auto-sync với Spark Runner tab

---

## 🚀 Quick Start

### 1️⃣ Load File
```
📂 Browse → Select docker-compose.yml → Auto-loads
```

Nếu file không tồn tại → Auto-load template với:
- spark-master
- spark-worker  
- namenode
- datanode
- networks & volumes

### 2️⃣ Edit File
- Edit trực tiếp trong editor
- Syntax highlighting tự động
- Press F5 để validate YAML

### 3️⃣ Save File
```
💾 Save (or Ctrl+S)
→ Validates YAML
→ Updates config['compose_file']
→ Syncs with Spark Runner
```

### 4️⃣ Start Compose
```
🚀 Start Compose
→ Proactive cleanup (removes all existing containers)
→ Starts services
→ Shows success/error
```

---

## 🎮 Button Functions

### 📂 Browse File
- Opens file dialog
- Filters: .yml, .yaml files
- Updates config path automatically
- Loads file content

### 💾 Save File
- Saves current content
- Validates YAML syntax first
- Updates config['compose_file']
- Shows file info (path, size, lines)

### 🔄 Reload File
- Reloads from disk
- Asks confirmation if modified
- Discards unsaved changes

### ✅ Validate YAML
- Checks YAML syntax
- Shows structure analysis:
  - Version
  - Services count
  - Networks count
  - Volumes count
- Displays in Validation Results panel

---

## 🚀 Quick Actions

### 🚀 Start Compose
**Function:** Start all Docker Compose services

**Process:**
```
1. 🔍 Check existing containers
2. 🧹 Remove all existing (proactive cleanup)
3. 💻 Run: docker-compose up -d
4. ✅ Show success/error dialog
```

**Features:**
- ✅ Proactive cleanup (no conflicts!)
- ✅ One-attempt guarantee
- ✅ Detailed logging
- ✅ Success confirmation dialog

**Expected Log:**
```log
[22:45:00] 🚀 Starting docker-compose...
[22:45:00] 📄 Using: docker-compose.yml
[22:45:00] 🔍 Checking for existing containers...
[22:45:01] 📋 Found 5 existing containers
[22:45:01] 🧹 Proactive cleanup: removing all...
[22:45:02] ✅ All existing containers removed
[22:45:02] 💻 $ docker-compose up -d
[22:45:08] ✅ Docker Compose started successfully
```

---

### ⏹️ Stop Compose
**Function:** Stop all running services

**Process:**
```
1. ⚠️ Confirmation dialog
2. 💻 Run: docker-compose stop
3. ✅ Show success/error
```

**Features:**
- ✅ Asks confirmation before stop
- ✅ Graceful shutdown
- ✅ Preserves containers (doesn't remove)

**Expected Log:**
```log
[22:46:00] ⏹️ Stopping docker-compose...
[22:46:00] 📄 Using: docker-compose.yml
[22:46:01] 💻 $ docker-compose stop
[22:46:05] ✅ Docker Compose stopped
```

---

### 📊 View Services
**Function:** Check status of all services

**Process:**
```
1. 💻 Run: docker-compose ps
2. 📊 Display results in Validation panel
3. ✅ Shows container names, status, ports
```

**Output Example:**
```
📊 Docker Compose Services Status:

NAME           IMAGE                          STATUS    PORTS
spark-master   bde2020/spark-master:3.3.0    Up        0.0.0.0:8080->8080/tcp
spark-worker   bde2020/spark-worker:3.3.0    Up        0.0.0.0:8081->8081/tcp
namenode       bde2020/hadoop-namenode:2.0.0 Up        0.0.0.0:9870->9870/tcp
datanode       bde2020/hadoop-datanode:2.0.0 Up        
```

**If No Services:**
```
  No services running or compose file not started.
  
  Run "Start Compose" first.
```

---

### 💾 Backup File
**Function:** Create timestamped backup

**Process:**
```
1. Check file exists
2. Create backup: {filename}.backup_{timestamp}
3. ✅ Show success with path
```

**Example:**
```
Original: docker-compose.yml
Backup:   docker-compose.yml.backup_20251012_224500
```

**Features:**
- ✅ Timestamp format: YYYYMMDD_HHMMSS
- ✅ Preserves original file
- ✅ Shows backup location

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save file |
| `Ctrl+R` | Reload file |
| `F5` | Validate YAML |

---

## 📊 Information & Validation Panel

### File Info Section
Shows when file loaded:
```
✅ File loaded successfully

Path: D:/Downloads/docker-compose.yml
Size: 1204 bytes
Lines: 54

Ready to edit...
```

### Validation Results Section
Shows after validation (F5):
```
✅ YAML Syntax: VALID

📊 Structure Analysis:

  • Version: 3
  • Services: 4
    - spark-master
    - spark-worker
    - namenode
    - datanode
  • Networks: 1
    - bigdata_network
  • Volumes: 2
    - hadoop_namenode
    - hadoop_datanode
```

---

## 🎨 Modified Indicator

### States:

**● Modified** (Yellow)
- File has unsaved changes
- Appears after editing

**● Saved** (Green)  
- All changes saved
- File in sync with disk

---

## 🔄 Integration with Spark Runner

### Auto-Sync Features:

**When you save in Editor:**
```python
config['compose_file'] = saved_path
# → Spark Runner now uses this file!
```

**When you browse in Editor:**
```python
config['compose_file'] = selected_path
# → Spark Runner syncs automatically!
```

**When you start in Spark Runner:**
```python
compose_file = config.get('compose_file')
# → Uses file from Editor!
```

---

## 💡 Best Practices

### 1️⃣ Always Validate Before Save
```
Edit → Press F5 → Check results → Save
```

### 2️⃣ Create Backups Regularly
```
💾 Backup File → Before major changes
```

### 3️⃣ Use View Services to Verify
```
🚀 Start → 📊 View Services → Check status
```

### 4️⃣ Stop Before Switching Files
```
⏹️ Stop Compose → Edit/Switch → 🚀 Start Compose
```

---

## 🐛 Troubleshooting

### Issue: Start Compose fails
**Solution:**
1. Check YAML syntax (F5)
2. View error logs in Log panel
3. Try manual: `docker-compose up -d`

### Issue: View Services shows nothing
**Cause:** Services not started yet  
**Solution:** Click "🚀 Start Compose" first

### Issue: Modified indicator stuck
**Solution:** Save file (Ctrl+S) or Reload (Ctrl+R)

### Issue: File not syncing to Spark Runner
**Cause:** Not saved yet  
**Solution:** Click "💾 Save" to trigger sync

---

## 📖 Advanced Usage

### Custom Templates
Edit default template in code:
```python
default_template = """
version: '3'
services:
  my-service:
    image: my-image
    ...
"""
```

### Validation Rules
Add custom validation:
```python
# Check required fields
if 'services' not in data:
    errors.append('Missing services')
```

### Log Filtering
Filter logs by type:
```python
# Only show errors
if log_type == 'error':
    display_log()
```

---

## 🎯 Quick Reference

| Action | Button | Shortcut | Result |
|--------|--------|----------|--------|
| Load file | 📂 Browse | - | Opens dialog |
| Save file | 💾 Save | Ctrl+S | Saves & syncs |
| Reload | 🔄 Reload | Ctrl+R | Reloads from disk |
| Validate | ✅ Validate | F5 | Checks YAML |
| Start | 🚀 Start Compose | - | Starts services |
| Stop | ⏹️ Stop Compose | - | Stops services |
| Status | 📊 View Services | - | Shows status |
| Backup | 💾 Backup File | - | Creates backup |

---

## ✅ Summary

**Docker Compose Editor = All-in-One Solution!**

- ✅ Edit with syntax highlighting
- ✅ Validate YAML realtime  
- ✅ Start/Stop services directly
- ✅ View status inline
- ✅ Backup protection
- ✅ Auto-sync with Spark Runner
- ✅ Proactive cleanup (no conflicts!)
- ✅ One-attempt guarantee

**No need to switch between tools!** 🎉

---

*Last Updated: October 12, 2025*  
*Version: 4.2.2*  
*Feature: Full Docker Compose Management*
