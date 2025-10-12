# 📖 Hướng Dẫn Sử Dụng Chi Tiết - Spark Runner GUI v3.0

## Mục Lục

1. [Giới Thiệu](#giới-thiệu)
2. [Khởi Động Lần Đầu](#khởi-động-lần-đầu)
3. [Spark Runner Tab](#spark-runner-tab)
4. [HDFS Upload Tab](#hdfs-upload-tab)
5. [AI Code Generator Tab](#ai-code-generator-tab)
6. [Performance Monitor Tab](#performance-monitor-tab)
7. [Tips & Tricks](#tips--tricks)
8. [Best Practices](#best-practices)

---

## Giới Thiệu

Spark Runner GUI là công cụ desktop giúp bạn:
- ✅ Quản lý Docker containers cho Spark cluster
- ✅ Chạy Spark jobs dễ dàng
- ✅ Upload dữ liệu lên HDFS
- ✅ Generate PySpark code tự động
- ✅ Monitor hiệu năng containers

### Kiến trúc hệ thống

```
┌─────────────────────────────────────┐
│      Spark Runner GUI (Python)      │
│  ┌─────────┬────────┬──────────┐   │
│  │ Spark   │ HDFS   │ AI Gen   │   │
│  │ Runner  │ Upload │ + Monitor│   │
│  └─────────┴────────┴──────────┘   │
└──────────────┬──────────────────────┘
               │ Docker API
               ▼
┌─────────────────────────────────────┐
│       Docker Desktop                 │
│  ┌────────┬────────┬─────────────┐  │
│  │NameNode│DataNode│ Spark Master│  │
│  └────────┴────────┴─────────────┘  │
│  ┌─────────────┐                    │
│  │ Spark Worker│                    │
│  └─────────────┘                    │
└─────────────────────────────────────┘
```

---

## Khởi Động Lần Đầu

### Bước 1: Kiểm tra yêu cầu

```bash
# Check Python
python --version
# Output: Python 3.7.x trở lên

# Check Docker
docker --version
# Output: Docker version 24.x.x

# Check docker-compose
docker-compose --version
# Output: docker-compose version 1.29.x
```

### Bước 2: Khởi động ứng dụng

**Windows:**
```cmd
cd GUI-Docker\run_spark_gui
run.bat
```

**Mac/Linux:**
```bash
cd GUI-Docker/run_spark_gui
python3 main.py
```

### Bước 3: Khởi động Docker containers (Lần đầu tiên)

1. Vào tab **🚀 Spark Runner**
2. Scroll xuống phần **🐳 Docker Container Management**
3. Click **START CONTAINERS**

**Lưu ý:**
- Lần đầu tiên sẽ mất 5-10 phút để pull images
- Progress được hiển thị trong log
- Status label sẽ chuyển sang "Running ✅" khi xong

### Bước 4: Verify containers

Click **CHECK STATUS** để xem:
```
NAME           COMMAND        STATUS        PORTS
spark-master   /bin/bash...   Up 2 minutes  0.0.0.0:8080->8080/tcp
spark-worker   /bin/bash...   Up 2 minutes  0.0.0.0:8081->8081/tcp
namenode       /bin/bash...   Up 2 minutes  0.0.0.0:9870->9870/tcp
datanode       /bin/bash...   Up 2 minutes
```

---

## Spark Runner Tab

### Overview

Tab này cho phép bạn:
- ✅ Chạy Python scripts trên Spark cluster
- ✅ Quản lý Docker containers
- ✅ Xem logs real-time
- ✅ Export commands và logs

### Interface Layout

```
┌─────────────────────────────────────────────────────┐
│ Left Panel (Fixed)      │ Right Panel (Expandable)  │
│                         │                            │
│ 📁 File Selection       │ 📊 Execution Log          │
│ ⚙️ Configuration        │                            │
│ 🐳 Docker Management    │ • Real-time output        │
│ 🚀 Spark Execution      │ • Color-coded messages    │
│ 💻 Generated Commands   │ • Auto-scroll             │
│                         │ • Searchable              │
└─────────────────────────────────────────────────────┘
```

### Workflow Chi Tiết

#### A. Chạy Spark Job (Auto Mode) - KHUYẾN NGHỊ

**Use Case**: Chạy nhanh một Python script

**Steps**:

1. **Chọn File**
   ```
   Click 📂 button → Browse to file
   Hoặc: Paste đường dẫn vào text box
   Hoặc: Chọn từ dropdown "Lịch sử"
   ```

2. **Verify Configuration** (Optional)
   ```
   Container: spark-worker (default)
   Master: spark://spark-master:7077 (default)
   ```

3. **Click RUN JOB NOW** (hoặc Ctrl+R)

4. **Theo dõi log**
   ```
   [12:34:56] → BƯỚC 1: Copy file
   [12:34:57] ✅ Bước 1 hoàn thành
   [12:34:57] → BƯỚC 2: Chạy Spark job
   [12:35:02] 📊 Spark Output:
   ...
   [12:35:10] ✅ TẤT CẢ CÁC BƯỚC HOÀN THÀNH!
   ```

**Demo Example**:

```python
# File: word_count.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("WordCount").getOrCreate()
sc = spark.sparkContext

# Read file from HDFS
text = sc.textFile("hdfs://namenode:8020/input/data.txt")

# Count words
word_count = text.flatMap(lambda line: line.split()) \
                 .map(lambda word: (word, 1)) \
                 .reduceByKey(lambda a, b: a + b)

# Print results
for word, count in word_count.collect():
    print(f"{word}: {count}")

spark.stop()
```

**Chạy job**:
1. Save code trên as `word_count.py`
2. Browse và chọn file
3. Click **RUN JOB NOW**
4. Xem kết quả trong log

#### B. Chạy Step-by-Step (Manual Mode)

**Use Case**: Debug hoặc cần control từng bước

**Steps**:

1. **Generate Commands** (F5)
   ```
   Tạo Docker commands trong command box
   Review commands trước khi chạy
   ```

2. **Step 1: COPY FILE**
   ```
   Copy Python file vào container
   File được đặt tại /tmp/<filename>
   ```

3. **Step 2: OPEN BASH** (Optional)
   ```
   Mở interactive terminal
   Có thể chạy commands thủ công
   Explore container filesystem
   ```

4. **Step 3: SUBMIT JOB**
   ```
   Chạy spark-submit
   Xem output real-time
   Có thể stop bất cứ lúc nào (Esc)
   ```

#### C. Docker Container Management

**Use Cases**: Quản lý lifecycle của containers

**Operations**:

1. **START CONTAINERS**
   ```
   ✅ Auto-detect Docker Desktop status
   ✅ Clean up old containers
   ✅ Pull images if needed
   ✅ Start all services
   ✅ Wait for ready state
   ```

2. **STOP CONTAINERS**
   ```
   ✅ Graceful shutdown
   ✅ Cleanup resources
   ✅ Remove networks
   ✅ Preserve data volumes
   ```

3. **RESTART CONTAINERS**
   ```
   ✅ Quick restart without rebuild
   ✅ Preserve configurations
   ✅ Faster than stop+start
   ```

4. **CHECK STATUS**
   ```
   ✅ List all containers
   ✅ Show status (Up/Down)
   ✅ Display ports
   ✅ Update status label
   ```

5. **BUILD IMAGES**
   ```
   ✅ Rebuild from Dockerfile
   ✅ Use for custom images
   ✅ Apply configuration changes
   ```

6. **CLEAN RESOURCES**
   ```
   ⚠️ CAUTION: Removes everything
   ✅ Stop all containers
   ✅ Remove unused images
   ✅ Clean volumes
   ✅ Free disk space
   ```

#### D. Compose File Management

**Edit docker-compose.yml**:

1. Click **✏️ Edit** button

2. Built-in editor mở ra với:
   - Syntax highlighting
   - Line numbers
   - Auto-save draft

3. **Actions**:
   - **💾 Save**: Lưu changes (creates backup)
   - **🔄 Reload**: Discard changes
   - **✓ Validate**: Check YAML syntax
   - **✖ Close**: Exit editor

4. **Validation Features**:
   ```yaml
   ✅ Check YAML syntax
   ✅ Verify required fields
   ✅ Validate service definitions
   ✅ Check port conflicts
   ```

**Create New Compose File**:

1. Click **Browse...** → "Create New"

2. Chọn template:
   - **Hadoop + Spark Cluster**: Full setup
   - **Spark Standalone**: Spark only
   - **Basic HDFS**: HDFS only
   - **Empty Template**: Start from scratch

3. Preview template

4. Click **✓ Create**

### Advanced Features

#### A. Command Export

**Use Case**: Lưu commands để chạy sau hoặc document

**Steps**:
1. Generate commands (F5)
2. Right-click command box
3. Select **💾 Save to file...**
4. Choose format:
   - `.sh` - Shell script (Linux/Mac)
   - `.bat` - Batch file (Windows)
   - `.txt` - Plain text

#### B. Log Management

**Export Logs**:
```
Ctrl+S hoặc Menu → File → Export Log
Format: Plain text với timestamps
Use for: Debugging, reporting, documentation
```

**Filter Logs**:
```
Right-click log → Select All
Ctrl+F (in exported file) → Search
```

**Clear Logs**:
```
Ctrl+L hoặc Right-click → Clear Log
Fresh start cho new operations
```

#### C. History Management

**File History**:
- Automatically saves last 10 files
- Quick access from dropdown
- Persists across sessions

**Clear History**:
```
Right-click history dropdown
Select "🗑️ Clear History"
Confirm action
```

**Refresh History**:
```
Menu → File → Refresh History
Reload from config file
```

---

## HDFS Upload Tab

### Overview

Upload files và folders lên Hadoop HDFS:
- ✅ Multiple file types support
- ✅ Batch upload với progress tracking
- ✅ Auto-extract compressed files
- ✅ Retry failed uploads
- ✅ Parallel upload operations

### Supported File Types

```
📊 Data Files:    .csv, .json, .parquet, .avro, .orc
📝 Text Files:    .txt, .log, .md
🗜️ Compressed:    .zip, .gz, .tar, .tar.gz
🖼️ Images:        .jpg, .jpeg, .png, .gif
📦 Others:        Any file type
```

### Configuration

**HDFS Settings**:

```
┌────────────────────────────────────────┐
│ HDFS Container:  namenode              │
│ HDFS Host:       hdfs://namenode:8020  │
│ Default Path:    /user/spark/data      │
│                                         │
│ ☑ Auto-extract compressed files        │
│ ☑ Delete archive after extraction      │
└────────────────────────────────────────┘
```

**Test Connection**:
```
Click "🔍 Test Connection"
Verifies:
  ✅ Container is running
  ✅ HDFS is accessible
  ✅ Path exists or can be created
```

### Upload Workflows

#### A. Single File Upload

**Steps**:

1. **Add File**
   ```
   Click "➕ Add Files"
   Select file(s) from browser
   Files appear in list
   ```

2. **Configure Destination**
   ```
   Default Path: /user/spark/data
   Change if needed
   ```

3. **Upload**
   ```
   Click "▶️ Start Upload"
   Watch progress bar
   Check status column
   ```

**Status States**:
- `Pending`: Waiting to upload
- `Uploading...`: In progress
- `✅ Success`: Uploaded
- `❌ Failed`: Error occurred
- `⚠️ Retry`: Auto-retry in progress

#### B. Folder Upload

**Steps**:

1. **Add Folder**
   ```
   Click "📂 Add Folder"
   Select folder
   All files recursively added
   ```

2. **Review File List**
   ```
   Check files in treeview
   Remove unwanted files if needed
   ```

3. **Batch Upload**
   ```
   Click "▶️ Start Upload"
   Files uploaded in parallel
   Overall progress shown
   ```

#### C. Compressed File Handling

**Auto-Extract Feature**:

```
If enabled (☑ Auto-extract):
  1. Upload .zip/.gz/.tar to HDFS
  2. Extract contents on HDFS
  3. Delete archive (if enabled)
  4. Contents available in path
```

**Example**:
```
Upload: data.zip (contains data.csv, data2.csv)
Result:
  /user/spark/data/data.csv
  /user/spark/data/data2.csv
```

### Advanced Features

#### A. Progress Tracking

**Overall Progress**:
```
Progress bar: Shows total % complete
Label: "Uploading 3/10 files (30%)"
```

**Per-File Status**:
```
File Name      | Size    | Type | Status
data.csv       | 2.5 MB  | CSV  | ✅ Success
logs.txt       | 500 KB  | TXT  | Uploading... (45%)
archive.zip    | 10 MB   | ZIP  | Pending
```

#### B. Error Handling & Retry

**Auto-Retry Logic**:
```
Failed uploads automatically retry:
  - Attempt 1: Immediate
  - Attempt 2: After 2s
  - Attempt 3: After 5s
  - Final: Mark as failed
```

**Manual Retry**:
```
Right-click failed item
Select "Retry Upload"
```

#### C. File Validation

**Pre-Upload Checks**:
- ✅ File exists
- ✅ File readable
- ✅ Size within limits
- ✅ HDFS path valid
- ✅ Sufficient HDFS space

**Validation Errors**:
```
⚠️ File too large (>10GB)
⚠️ Invalid characters in path
⚠️ File not found
⚠️ Permission denied
```

---

## AI Code Generator Tab

### Overview

Tạo PySpark code từ mô tả tự nhiên:
- ✅ Natural language processing
- ✅ Pre-built templates
- ✅ Syntax highlighting
- ✅ Code validation
- ✅ Direct execution

### Interface

```
┌─────────────────────────────────────────┐
│ 📝 Input Section                        │
│   • HDFS Path input                     │
│   • App Name input                      │
│   • Description text area               │
│   • Template buttons                    │
│   • Generate button                     │
├─────────────────────────────────────────┤
│ 💻 Output Section                       │
│   • Syntax-highlighted code             │
│   • Line numbers                        │
│   • Save/Copy/Run buttons               │
└─────────────────────────────────────────┘
```

### Workflow

#### A. Using Templates

**Available Templates**:

1. **Word Count**
   ```
   Đếm tần suất xuất hiện của từng từ
   Input: Text file
   Output: Word counts in console
   ```

2. **CSV Analysis**
   ```
   Phân tích file CSV
   Operations: Load, filter, aggregate
   Output: Statistics và summary
   ```

3. **Data Filter**
   ```
   Lọc dữ liệu theo điều kiện
   Input: CSV/JSON file
   Operations: Filter, select columns
   Output: Filtered dataset
   ```

4. **Top N**
   ```
   Tìm top N records
   Input: Any structured data
   Operations: Sort, limit
   Output: Top N items
   ```

**Steps**:

1. Click template button (e.g., "Word Count")

2. Template auto-fills inputs:
   ```
   HDFS Path: /input/harrypotter.txt
   App Name: HDFSDataProcessing
   Description: (template description)
   ```

3. Customize nếu cần

4. Click **✨ Generate Code**

5. Review generated code

6. **Actions**:
   - **💾 Save to File**: Export to .py
   - **📋 Copy Code**: Copy to clipboard
   - **▶️ Run in Spark Tab**: Execute immediately

#### B. Custom Description

**Writing Effective Descriptions**:

**Good Example**:
```
Đọc file CSV từ HDFS path /data/sales.csv
Lọc các bản ghi có sales > 1000
Group by category và tính tổng sales
Sort theo tổng sales giảm dần
Lưu kết quả vào /output/top_categories.csv
```

**Generated Code**:
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, col

spark = SparkSession.builder.appName("SalesAnalysis").getOrCreate()

try:
    # Read CSV
    df = spark.read.csv("hdfs://namenode:8020/data/sales.csv", header=True)
    
    # Filter
    filtered = df.filter(col("sales") > 1000)
    
    # Group and aggregate
    result = filtered.groupBy("category").agg(sum("sales").alias("total_sales"))
    
    # Sort
    sorted_result = result.orderBy(col("total_sales").desc())
    
    # Save
    sorted_result.write.csv("hdfs://namenode:8020/output/top_categories.csv")
    
finally:
    spark.stop()
```

**Bad Example** (too vague):
```
Phân tích dữ liệu sales
→ Thiếu details về input, operations, output
```

**Tips for Better Descriptions**:
- ✅ Specify input file path và format
- ✅ List exact operations (filter, group, sort...)
- ✅ Mention output destination
- ✅ Include business logic
- ✅ Use specific numbers/thresholds

### Generated Code Features

#### A. Syntax Highlighting

```python
# Keywords in blue
from pyspark.sql import SparkSession

# Strings in orange
file_path = "hdfs://namenode:8020/data.txt"

# Functions in yellow
def process_data():
    pass

# Comments in green
# This is a comment
```

#### B. Code Structure

**Standard Template**:
```python
# 1. Imports
from pyspark.sql import SparkSession

# 2. Main function
def main():
    # 3. Initialize Spark
    spark = SparkSession.builder.appName("AppName").getOrCreate()
    
    try:
        # 4. Your code here
        # ...
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # 5. Cleanup
        spark.stop()

# 6. Entry point
if __name__ == "__main__":
    main()
```

#### C. Code Actions

**Save to File**:
```
Click "💾 Save to File"
Choose location
File saved as .py
Ready to run
```

**Copy Code**:
```
Click "📋 Copy Code"
Code copied to clipboard
Paste anywhere (IDE, email, docs)
```

**Run in Spark Tab**:
```
Click "▶️ Run in Spark Tab"
Code saved to temp file
Auto-switched to Spark Runner tab
File loaded and ready to run
```

### Advanced Usage

#### A. Code Customization

**Edit Generated Code**:
1. Review generated code
2. Click in code editor
3. Make modifications
4. Save or run

**Common Customizations**:
- Change HDFS paths
- Adjust filter conditions
- Add logging
- Modify output format
- Add error handling

#### B. Code Snippets Library

**Save Custom Templates**:
```
Currently saved in generated code
Future: Template library feature
Can manually save .py files
Reuse across projects
```

---

## Performance Monitor Tab

### Overview

Real-time monitoring của Docker containers:
- ✅ CPU usage
- ✅ Memory consumption
- ✅ Network I/O
- ✅ Block I/O
- ✅ Historical data
- ✅ Export statistics

### Views

#### A. Table View (📊)

**Tổng Quan Nhanh**:

```
┌──────────────────────────────────────────────────────────┐
│ Container    │ CPU %  │ Memory Usage │ Memory % │ Net I/O │
├──────────────────────────────────────────────────────────┤
│ spark-master │ 15.2%  │ 512MB/2GB    │ 25.6%    │ 1.5MB   │
│ spark-worker │ 45.8%  │ 1.2GB/4GB    │ 30.0%    │ 5.2MB   │
│ namenode     │ 8.1%   │ 256MB/1GB    │ 25.6%    │ 850KB   │
│ datanode     │ 12.3%  │ 384MB/2GB    │ 19.2%    │ 1.1MB   │
└──────────────────────────────────────────────────────────┘
```

**Features**:
- Sortable columns
- Auto-refresh
- Color-coded thresholds
- Scrollable list

#### B. Detail View (📋)

**Thông Tin Chi Tiết**:

```
╔═══════════════════════════════════════════╗
  DOCKER CONTAINER PERFORMANCE MONITOR
  Updated: 2025-01-12 14:30:45
╚═══════════════════════════════════════════╝

[1] Container: spark-master
    CPU Usage:      15.2%
    Memory Usage:   512MB / 2GB
    Memory %:       25.6%
    Network I/O:    1.5MB / 850KB
    Block I/O:      120MB / 45MB

[2] Container: spark-worker
    CPU Usage:      45.8% (HIGH!)
    Memory Usage:   1.2GB / 4GB
    Memory %:       30.0%
    Network I/O:    5.2MB / 2.1MB
    Block I/O:      450MB / 120MB
```

**Features**:
- Detailed metrics
- High-usage alerts
- Read/Write breakdown
- Timestamp tracking

#### C. History View (📉)

**Timeline Data**:

```
╔════════════════════════════════════════════╗
  PERFORMANCE HISTORY (Last 50 Records)
╚════════════════════════════════════════════╝

[14:30:45]
  spark-master         | CPU: 15.2%   | MEM: 25.6%
  spark-worker         | CPU: 45.8%   | MEM: 30.0%
  namenode             | CPU: 8.1%    | MEM: 25.6%
  datanode             | CPU: 12.3%   | MEM: 19.2%

[14:30:43]
  spark-master         | CPU: 14.8%   | MEM: 25.4%
  spark-worker         | CPU: 44.2%   | MEM: 29.8%
  ...
```

**Features**:
- Rolling 50 records
- Reverse chronological
- Compact format
- Trend analysis

### Monitoring Operations

#### A. Start Monitoring

**Steps**:

1. Set update interval (1-10 seconds)
   ```
   Default: 2 seconds
   Faster: More data, higher load
   Slower: Less data, lower load
   ```

2. Click **▶️ Start Monitoring**

3. Auto-refresh begins
   ```
   ✅ Fetches stats every N seconds
   ✅ Updates all views
   ✅ Adds to history
   ✅ Logs operations
   ```

4. Monitor in real-time
   ```
   Switch between views
   Watch for high usage
   Track trends
   ```

#### B. Stop Monitoring

**Steps**:

1. Click **⏹️ Stop Monitoring**

2. Refresh stops
   ```
   ✅ Last data preserved
   ✅ History available
   ✅ Can restart anytime
   ```

#### C. Manual Refresh

**One-Time Update**:
```
Click "🔄 Refresh Once"
Gets current stats
No auto-refresh
Good for quick checks
```

#### D. Export Statistics

**Steps**:

1. Click **💾 Export Stats**

2. Choose location:
   ```
   Filename: docker_stats_YYYYMMDD_HHMMSS.json
   Format: JSON
   ```

3. File structure:
   ```json
   {
     "2025-01-12T14:30:45": [
       {
         "name": "spark-master",
         "cpu": "15.2%",
         "mem_usage": "512MB / 2GB",
         "mem_perc": "25.6%",
         "net_io": "1.5MB / 850KB",
         "block_io": "120MB / 45MB",
         "timestamp": "2025-01-12T14:30:45"
       },
       ...
     ],
     ...
   }
   ```

4. Use cases:
   - Performance analysis
   - Capacity planning
   - Troubleshooting
   - Reporting

### Interpreting Metrics

#### CPU Usage

**Normal Range**:
- Idle: 0-10%
- Light load: 10-30%
- Medium load: 30-60%
- Heavy load: 60-80%
- Critical: >80%

**Actions**:
- >80%: Investigate processes
- Sustained high: Scale up
- Spikes: Normal for batch jobs

#### Memory Usage

**Normal Range**:
- Idle: <30%
- Working: 30-60%
- Busy: 60-80%
- Critical: >80%

**Actions**:
- >80%: Check for memory leaks
- OOM risk: Add more memory
- Swap usage: Performance hit

#### Network I/O

**Indicates**:
- Data transfer activity
- HDFS operations
- Container communication

**High Network**:
- Large file uploads
- Distributed computations
- Data replication

#### Block I/O

**Indicates**:
- Disk read/write
- HDFS data operations
- Logging activity

**High Block I/O**:
- Reading large datasets
- Writing results
- Checkpointing

### Tips & Best Practices

#### Monitoring Tips

1. **Set Appropriate Interval**
   ```
   Dev/Testing: 1-2 seconds
   Production: 5-10 seconds
   Long-running jobs: 10+ seconds
   ```

2. **Watch for Patterns**
   ```
   Periodic spikes: Normal
   Constant high: Problem
   Sudden drops: Container issue
   ```

3. **Export Regularly**
   ```
   Before major changes
   During incidents
   For capacity planning
   ```

4. **Use Multiple Views**
   ```
   Table: Quick overview
   Detail: Deep dive
   History: Trend analysis
   ```

#### Resource Optimization

1. **CPU Optimization**
   ```
   - Tune Spark executors
   - Adjust parallelism
   - Optimize code
   ```

2. **Memory Optimization**
   ```
   - Configure heap size
   - Enable compression
   - Tune caching
   ```

3. **I/O Optimization**
   ```
   - Use efficient formats (Parquet)
   - Enable compression
   - Batch operations
   ```

---

## Tips & Tricks

### General Tips

1. **Keyboard Shortcuts**
   ```
   Master these for efficiency:
   Ctrl+R: Quick run
   F5: Generate
   Ctrl+S: Save/Export
   F1: Help
   ```

2. **Context Menus**
   ```
   Right-click everywhere:
   - File entries
   - Log areas
   - Command boxes
   - Tree views
   Hidden features await!
   ```

3. **Drag & Drop**
   ```
   Drag files directly:
   - Into file entry
   - Into HDFS upload list
   ```

4. **Auto-Save**
   ```
   Config auto-saves every 30s
   No need to click Save constantly
   Backup config regularly
   ```

### Spark Tips

1. **Resource Tuning**
   ```bash
   # Edit compose file for more resources
   spark-worker:
     environment:
       - SPARK_WORKER_CORES=4
       - SPARK_WORKER_MEMORY=4g
   ```

2. **Debugging Failed Jobs**
   ```
   1. Check file exists in container
   2. Verify HDFS connectivity
   3. Review Python syntax
   4. Check Spark logs:
      docker logs spark-worker
   ```

3. **Performance**
   ```
   - Use broadcast variables
   - Cache frequently used RDDs
   - Avoid shuffles when possible
   - Use appropriate file formats
   ```

### HDFS Tips

1. **Organize Files**
   ```
   /user/spark/
     ├── input/       # Source data
     ├── output/      # Results
     ├── temp/        # Intermediate
     └── archive/     # Old files
   ```

2. **Large File Uploads**
   ```
   - Split into chunks
   - Upload during off-hours
   - Use compressed formats
   - Monitor progress
   ```

3. **HDFS Commands**
   ```bash
   # List files
   docker exec namenode hdfs dfs -ls /user/spark/data
   
   # Check file
   docker exec namenode hdfs dfs -cat /path/file.txt | head
   
   # Remove file
   docker exec namenode hdfs dfs -rm /path/file.txt
   ```

### Performance Tips

1. **Monitor Resources**
   ```
   - Start monitoring before jobs
   - Watch for bottlenecks
   - Export stats for analysis
   - Compare across runs
   ```

2. **Container Health**
   ```
   Check status regularly:
   - Use CHECK STATUS button
   - Monitor logs
   - Restart if unstable
   ```

3. **Disk Space**
   ```
   Clean periodically:
   - Remove old containers
   - Prune unused images
   - Clear HDFS temp files
   ```

---

## Best Practices

### Development Workflow

```
1. START CONTAINERS
   ↓
2. VERIFY STATUS
   ↓
3. UPLOAD TEST DATA (HDFS Tab)
   ↓
4. GENERATE/WRITE CODE (AI Tab)
   ↓
5. TEST ON SMALL DATASET
   ↓
6. ITERATE AND DEBUG
   ↓
7. SCALE TO FULL DATASET
   ↓
8. MONITOR PERFORMANCE (Monitor Tab)
   ↓
9. EXPORT RESULTS
   ↓
10. STOP CONTAINERS (if done)
```

### Production Workflow

```
1. BACKUP CONFIGURATION
   ↓
2. PREPARE DATA (validate, clean)
   ↓
3. TEST CODE LOCALLY
   ↓
4. START CONTAINERS
   ↓
5. VERIFY CLUSTER HEALTH
   ↓
6. UPLOAD PRODUCTION DATA
   ↓
7. RUN JOB WITH MONITORING
   ↓
8. VERIFY RESULTS
   ↓
9. EXPORT LOGS AND STATS
   ↓
10. SCHEDULE CLEANUP
```

### Maintenance

**Daily**:
- ✅ Check container status
- ✅ Review logs for errors
- ✅ Monitor disk space

**Weekly**:
- ✅ Backup configuration
- ✅ Clean old containers
- ✅ Update Docker images
- ✅ Review performance stats

**Monthly**:
- ✅ Audit HDFS storage
- ✅ Archive old data
- ✅ Update documentation
- ✅ Review resource usage

### Security

1. **Network Security**
   ```
   - Use internal networks
   - Restrict port exposure
   - Enable authentication
   ```

2. **Data Security**
   ```
   - Encrypt sensitive data
   - Use HDFS permissions
   - Regular backups
   ```

3. **Access Control**
   ```
   - Limit GUI access
   - Audit operations
   - Secure credentials
   ```

---

## Kết Luận

Spark Runner GUI giúp bạn:
- 🚀 Tăng năng suất development
- 💡 Đơn giản hóa DevOps tasks
- 📊 Giám sát hiệu năng real-time
- 🎯 Focus vào code, không lo infrastructure

**Happy Sparking! 🎉**

---

*Last Updated: 2025-01-12*
*Version: 3.0.0*
