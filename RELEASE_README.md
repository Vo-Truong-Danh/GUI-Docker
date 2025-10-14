# Spark Runner GUI v6.0.1 - Quick Start

## 🚀 Installation (2 Minutes)

### Step 1: Install Docker Desktop
- Download: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- **Important**: Docker must be running!

### Step 2: Run Application
- Double-click `SparkRunnerGUI.exe`
- Wait for GUI to load
- Done! 🎉

## 📋 Requirements

✅ Windows 10/11 (64-bit)  
✅ Docker Desktop installed and running  
✅ 4GB RAM minimum  
❌ **NO** Python installation needed!

## ✨ Features

### 1. **Spark Runner**
- Run PySpark jobs on Docker containers
- View real-time logs
- Download results

### 2. **HDFS Upload**
- Upload files to HDFS
- Browse HDFS filesystem
- Manage data files

### 3. **AI Code Generator**
- Generate PySpark code with AI
- Multiple AI providers (Gemini, GPT, Claude)
- Auto-complete responses

### 4. **Performance Monitor**
- Real-time Docker stats
- CPU, Memory, Network monitoring
- Resource usage charts

### 5. **Docker Compose Editor**
- Edit docker-compose.yml
- Syntax highlighting
- Validation

### 6. **Settings**
- Port configuration
- Load from Docker Compose
- System preferences

## 🎯 Quick Usage

### First Time Setup:
1. Start Docker Desktop
2. Run `SparkRunnerGUI.exe`
3. Go to **Settings** tab
4. Click **Load from Docker Compose**
5. Click **Start Containers** (or use `docker-compose up -d` in terminal)

### Run Spark Job:
1. Go to **Spark Runner** tab
2. Browse Python file
3. Configure settings
4. Click **Run**
5. View logs and results

### Upload to HDFS:
1. Go to **HDFS Upload** tab
2. Select local file
3. Choose HDFS destination
4. Click **Upload**

### Generate AI Code:
1. Go to **AI API** tab
2. Select AI provider
3. Enter question
4. Click **Generate**
5. Copy/Save/Run code

## ⚠️ Troubleshooting

### Problem: "Docker not found"
**Solution:** 
- Start Docker Desktop
- Wait 30 seconds for initialization
- Restart application

### Problem: "Containers not starting"
**Solution:**
- Check Docker Desktop is running
- Run in terminal: `docker-compose up -d`
- Check port conflicts (8080, 8081, 9870, etc.)

### Problem: "Cannot connect to HDFS"
**Solution:**
- Verify namenode container is running
- Check ports: 9870 (Web UI), 8020 (HDFS)
- Test connection in HDFS Upload tab

### Problem: Application won't start
**Solution:**
- Check antivirus isn't blocking
- Run as Administrator
- Check Windows Defender logs

## 📞 Support

- **Documentation**: See full README.md
- **Issues**: https://github.com/yourusername/GUI-Docker/issues
- **Wiki**: https://github.com/yourusername/GUI-Docker/wiki

## 🔧 Configuration

Configuration file: `spark_runner_config.json`

Edit with notepad to customize:
- Container names
- Ports
- Paths
- Timeouts

## 🎓 Learning Resources

### Spark Documentation
- https://spark.apache.org/docs/latest/

### HDFS Guide
- https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsUserGuide.html

### Docker Reference
- https://docs.docker.com/

## ✅ System Check

Before running:
- [ ] Docker Desktop installed
- [ ] Docker Desktop is running
- [ ] No port conflicts (8080, 8081, 9870, 9864)
- [ ] 4GB+ RAM available
- [ ] Windows Defender not blocking

## 📊 Default Ports

| Service | Port |
|---------|------|
| Spark Master UI | 9090 |
| Spark Worker UI | 8081 |
| HDFS NameNode UI | 9870 |
| HDFS DataNode | 9864 |
| History Server | 18080 |

Access via browser: `http://localhost:[PORT]`

## 🎉 Version 6.0.1 Features

### ✨ New in v6.0.1
- Fixed port configuration icons
- Enhanced AI API (no truncation)
- Increased token limit 2048→8192
- Better streaming support
- Improved retry logic

### 🛡️ v6.0 Features
- Enhanced error handling
- Resource manager
- Backup system
- Auto-recovery
- Health monitoring

## 💡 Pro Tips

1. **Keep Docker Running**: Application needs Docker Desktop
2. **Check Logs**: Use Spark Runner logs for debugging
3. **Port Conflicts**: Change ports in Settings if needed
4. **AI API**: Gemini is free, no API key needed
5. **HDFS Browser**: Real-time HDFS filesystem browser

## 🌟 Getting Started Tutorial

### Tutorial 1: Hello World Spark Job
```python
# 1. Create file: hello_spark.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("HelloWorld").getOrCreate()
data = [("Hello", 1), ("World", 2), ("Spark", 3)]
df = spark.createDataFrame(data, ["word", "count"])
df.show()
spark.stop()

# 2. Go to Spark Runner tab
# 3. Browse to hello_spark.py
# 4. Click Run
# 5. See output in logs!
```

### Tutorial 2: Upload File to HDFS
```
1. Go to HDFS Upload tab
2. Click "Browse Local File"
3. Select any CSV file
4. HDFS Path: /input/mydata.csv
5. Click Upload
6. Verify in HDFS browser
```

### Tutorial 3: Generate Code with AI
```
1. Go to AI API tab
2. Question: "Read CSV from HDFS and calculate average"
3. Click Generate
4. Copy generated code
5. Use in Spark Runner!
```

## 📝 Notes

- **Antivirus**: May flag executable as unknown. This is normal for PyInstaller apps.
- **First Run**: May take 10-20 seconds to load
- **Docker**: Must be running before starting application
- **Ports**: Ensure no conflicts with existing services

## 🚀 Enjoy!

Happy Spark coding! 🎉

---

**Version:** 6.0.1  
**Release Date:** 2025-10-14  
**Platform:** Windows 10/11 (64-bit)  
**Size:** ~40 MB  
**License:** MIT
