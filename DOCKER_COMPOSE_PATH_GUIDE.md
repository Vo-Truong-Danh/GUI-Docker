# Docker Compose Path Management Guide

## 📄 Overview
This guide explains how the application handles docker-compose.yml file paths to ensure consistency across tabs and prevent confusion.

## 🔧 How It Works

### Default Path
```
d:\BaiTapSinhVien\TH BigData\GUI-Docker\run_spark_gui\docker-compose.yml
```

This default path is set when the application starts and stored in `spark_runner_config.json` under the key `compose_file`.

### Path Configuration

#### 1. Config Section in Spark Runner Tab
- **Location**: Configuration card with Docker Compose field
- **Components**:
  - Text entry showing current compose file path
  - Browse button (📂) to select different file
  - Save button to persist changes

#### 2. Docker Compose Editor Tab
- **Auto-sync**: When you load or save a file in the editor, the path is automatically updated
- **Template**: If file doesn't exist, a 40-line Spark template is loaded
- **Save behavior**: Saving updates both the file and the config

## 🔄 Path Synchronization

### When Paths Are Updated:
1. **Browse in Config**: Using the Browse button updates `compose_file` immediately
2. **Save Config**: Clicking "Save Configuration" persists the path
3. **Editor Browse**: Opening a file in Docker Compose Editor updates config
4. **Editor Save**: Saving in editor updates config to match saved file path

### All Docker Operations Use This Path:
- ✅ Start containers
- ⏹️ Stop containers
- 🔄 Restart containers
- 🔨 Build images
- 🧹 Clean resources

## ✅ Validation System

### Before Every Docker Operation:
```
1. Get compose_file from config
2. Check if file exists on disk
3. If NOT exists → Show error dialog
4. If exists → Log filename and proceed
```

### Example Log Output:
```
🐳 Starting Docker containers...
📄 Using: docker-compose.yml
✅ Docker containers started successfully
```

### Error Dialog:
If file not found, shows:
```
Docker Compose file not found:
C:\path\to\docker-compose.yml

Please check the path in Config section or
use Browse button to select the correct file.
```

## 📋 Best Practices

### ✅ DO:
- Use Browse button to select correct compose file
- Check Config section to verify current path
- Save Configuration after changing path
- Ensure compose file exists before starting Docker

### ❌ DON'T:
- Manually edit config JSON without using UI
- Assume default path if you've changed it
- Run Docker commands if file path is incorrect
- Edit file outside application without reloading

## 🔍 Troubleshooting

### Issue: "Docker Compose file not found"
**Solution**: 
1. Go to Spark Runner tab → Configuration card
2. Click Browse button (📂)
3. Select your docker-compose.yml file
4. Click "Save Configuration"

### Issue: Edited file but Docker uses old version
**Solution**:
- Always edit in Docker Compose Editor tab OR
- If editing externally, reload the file in editor
- Verify path in Config section matches your file

### Issue: Two different docker-compose.yml files
**Solution**:
- Application uses ONE compose file at a time
- Current path shown in Config section
- Use Browse to switch between files
- Path persists across application restarts

## 📊 Config File Structure

Location: `run_spark_gui/spark_runner_config.json`

```json
{
  "container_name": "spark_master",
  "spark_master": "spark://spark-master:7077",
  "compose_file": "d:\\...\\docker-compose.yml",
  "history": [...]
}
```

## 🎯 Quick Reference

| Action | Effect on Path |
|--------|---------------|
| Browse in Config | Updates path immediately |
| Save Configuration | Persists path to JSON |
| Browse in Editor | Updates path + loads file |
| Save in Editor | Updates path to saved location |
| Reset Config | Restores default path |
| Docker Start/Stop/etc | Uses current config path |

## 🔐 Path Validation Flow

```
User clicks Docker operation
    ↓
Get compose_file from config
    ↓
Check file exists?
    ├─ YES → Log filename → Execute command
    └─ NO  → Show error → Stop
```

## 💡 Tips

1. **Visual Confirmation**: Every Docker operation logs the filename being used
2. **Error Prevention**: Validation happens BEFORE running commands
3. **Single Source of Truth**: Config file stores the active path
4. **Cross-tab Sync**: Changes in one tab reflect in others
5. **User-friendly**: Browse button prevents typos in paths

## 📝 Summary

The docker-compose.yml path is:
- ✅ **Configurable** - Change via Browse button
- ✅ **Validated** - Checked before every Docker operation  
- ✅ **Synchronized** - Updates across all tabs
- ✅ **Logged** - Shows which file is being used
- ✅ **Persistent** - Saved in config JSON
- ✅ **Safe** - Prevents running invalid paths

---
**Last Updated**: 2024
**Version**: v4.1.0
