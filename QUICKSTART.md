# 🚀 Quick Start Guide - Spark Runner GUI

**Get started in 5 minutes!**

---

## Prerequisites

✅ Python 3.7+  
✅ Docker Desktop  
✅ 8GB RAM minimum

---

## Installation (3 Steps)

### 1️⃣ Clone & Install

```bash
# Clone repository
git clone https://github.com/yourusername/GUI-Docker.git
cd GUI-Docker/run_spark_gui

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Start Docker Desktop

**Windows:**
- Open Docker Desktop from Start Menu
- Wait for "Docker Desktop is running"

**Mac/Linux:**
```bash
# Verify Docker is running
docker info
```

### 3️⃣ Launch Application

**Windows:**
```cmd
run.bat
```

**Mac/Linux:**
```bash
python3 main.py
```

---

## First Run (2 Minutes)

### Step 1: Start Containers

1. Open **🚀 Spark Runner** tab
2. Click **START CONTAINERS**
3. Wait ~2 minutes (first time only)
4. Status shows **"Running ✅"**

### Step 2: Run Your First Job

1. Click **📂 Browse**
2. Select a Python file (or use demo file)
3. Click **RUN JOB NOW** (Ctrl+R)
4. Watch the magic happen! ✨

---

## Demo Example

Create `hello_spark.py`:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("HelloSpark").getOrCreate()
sc = spark.sparkContext

# Simple test
data = [1, 2, 3, 4, 5]
rdd = sc.parallelize(data)
result = rdd.map(lambda x: x * 2).collect()

print("Original:", data)
print("Doubled:", result)

spark.stop()
```

**Run it:**
1. Load file in GUI
2. Click **RUN JOB NOW**
3. See output in log! 🎉

---

## Quick Tips

- **Ctrl+R**: Quick run
- **F5**: Generate commands
- **F1**: Help
- **Right-click**: Context menus

---

## Next Steps

- 📖 Read [USER_GUIDE.md](USER_GUIDE.md) for detailed tutorials
- 🔍 Explore other tabs (HDFS, AI Generator, Monitor)
- 💡 Try templates in AI Code Generator
- 📊 Monitor performance in real-time

---

## Troubleshooting

**Containers won't start?**
```bash
# Check Docker is running
docker ps

# Clean and restart
docker-compose down
docker-compose up -d
```

**Permission denied?**
```bash
# Linux/Mac: Add user to docker group
sudo usermod -aG docker $USER
```

**Port already in use?**
- Close other Docker containers
- Or edit `docker-compose.yml` ports

---

## Need Help?

- 📘 [Full README](README.md)
- 📖 [User Guide](USER_GUIDE.md)
- 🐛 [Report Issues](https://github.com/yourusername/GUI-Docker/issues)
- 💬 [Discussions](https://github.com/yourusername/GUI-Docker/discussions)

---

**Happy Sparking! 🎉**

*Version 3.0.0 - January 2025*
