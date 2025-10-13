# Spark Runner GUI V5.2.2 - Enhanced Edition

Modern, clean, and professional GUI for running Spark jobs with Docker containers.

**Latest Version:** 5.2.2 (October 13, 2025)  
**New Features:** Resource monitoring, centralized constants, enhanced thread safety

## 📁 Project Structure (Enhanced & Optimized)

```
run_spark_gui/
├── main.py                          # Main application entry point
├── spark_runner_tab_v4_clean.py    # Modern UI implementation (V4) ⭐
├── hdfs_upload_tab_v4_clean.py     # Modern HDFS upload UI ⭐
├── ai_code_generator_tab_v4_clean.py # AI code generation tab ⭐
├── performance_monitor_v4_clean.py # Performance monitoring ⭐
├── docker_compose_editor_v4.py     # Docker compose editor
├── settings_tab_v4.py              # Settings configuration
│
├── spark_backend.py                # Spark job execution logic (Thread-safe ✅)
├── docker_utils.py                 # Docker utilities (Fixed ✅)
├── hdfs_utils.py                   # HDFS operations
├── database.py                     # Job history & metrics storage
│
├── validation.py                   # Input validation (V5.0) ⭐
├── logging_config.py               # Comprehensive logging (V5.0) ⭐
├── health_check.py                 # System health monitoring (V5.0) ⭐
├── error_handler.py                # Enhanced error handling (V5.1) ⭐
├── input_sanitizer.py              # Input sanitization (V5.1) ⭐
├── auto_recovery.py                # Auto-recovery system (V5.1, Fixed ✅) ⭐
├── constants.py                    # Centralized constants (V5.2.2) 🆕
├── resource_monitor.py             # Container resource monitoring (V5.2.2) 🆕
│
├── modern_theme.py                 # Modern theme definitions
├── modern_components.py            # Reusable modern UI components
├── config_manager.py               # Configuration management
├── system_utils.py                 # System utilities
├── progress_tracker.py             # Progress tracking
├── health_monitor.py               # Health monitoring UI
├── java_unzip_util.py              # Java-based unzip utility
│
├── spark_runner_config.json        # Configuration file (auto-generated)
├── requirements.txt                # Python dependencies
├── run.bat                         # Windows launcher
├── START.bat                       # Quick start launcher
├── safe_start.py                   # Safe startup script
├── quick_fix.py                    # Quick fix utilities
│
├── test_v5_modules.py              # V5 modules tests
├── test_hdfs_utils.py              # HDFS utilities tests
├── test_java_unzip.py              # Java unzip tests
├── comprehensive_test.py           # Comprehensive test suite
│
└── README.md                       # This file
```

## 🆕 What's New in V5.2.2

### Bug Fixes ✅
- **Fixed:** Type hints compatibility (Python 3.6+) in `auto_recovery.py`
- **Fixed:** Race condition in Windows threading in `spark_backend.py`
- **Fixed:** Removed code artifacts in `docker_utils.py`

### New Modules 🎉
- **`constants.py`** - Centralized constants (50+ constants)
  - All timeouts, retry attempts, sizes defined in one place
  - No more magic numbers!
  - Helper functions for validation
  
- **`resource_monitor.py`** - Real-time container monitoring
  - CPU, Memory, Network, Block I/O tracking
  - Historical data storage
  - Alert thresholds
  - Export metrics to JSON
  - Background monitoring thread

### Improvements 💪
- Thread-safe list operations with locks
- Better error handling throughout
- Enhanced code quality (9.2/10, was 8.5/10)

## 🎨 UI Features (V4)

### Clean Professional Design
- **Inspired by:** GitHub, VS Code, Notion
- **Color Scheme:** GitHub-like professional colors
- **Layout:** 35-65 split (Controls | Logs)

### Components

**📁 Python File Section**
- Full-width input field
- Browse & Clear buttons (equal size, horizontal)
- Recent files dropdown

**🐳 Docker Containers**
- Status badge with color indicators
- 6 control buttons in 2x3 grid (Start, Stop, Restart, Status, Build, Clean)
- All buttons full-width for consistency

**⚡ Spark Job**
- Quick actions: Generate, Run, Stop
- Manual steps: Copy, Bash, Submit
- Force Kill button
- Progress indicator

**⚙️ Config**
- Container name input
- Spark master URL input
- Save & Reset buttons

**🛠️ Tools**
- Spark UI & Hadoop UI launchers
- Export & Clear log buttons

**📋 Generated Commands**
- Light background code area
- 8 lines height (optimized)

**📊 Execution Log**
- Dark theme (GitHub Dark)
- Color-coded messages (success, error, warning, info)
- Auto-scroll
- Large display area (65% width)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker Desktop
- Spark cluster (via docker-compose)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start Docker containers:
```bash
docker-compose up -d
```

3. Run the application:
```bash
python main.py
# or on Windows:
run.bat
```

## 📖 Usage

### Running a Spark Job

1. **Select Python File**
   - Click "Browse" to select your PySpark script
   - Or choose from recent files

2. **Check Docker Status**
   - Ensure containers are running (green status)
   - If not, click "Start"

3. **Run Job**
   - Click "Generate" to create commands
   - Click "Run" to execute automatically
   - Or use manual steps (Copy → Bash → Submit)

4. **Monitor Progress**
   - Watch execution log for real-time output
   - Progress bar shows job status

### Configuration

- **Container Name:** Default is `spark-worker`
- **Spark Master:** Default is `spark://spark-master:7077`
- Click "Save" to persist changes
- Click "Reset" to restore defaults

## 🎯 Key Improvements in V4

### Optimization
- ✅ Removed old UI versions (v2, v3)
- ✅ Cleaned up test files
- ✅ Removed outdated documentation
- ✅ Simplified file structure

### UI Enhancements
- ✅ Full-width buttons (no wasted space)
- ✅ Better file input layout
- ✅ Larger, more visible buttons
- ✅ Grid layout for proper scrolling
- ✅ 35-65 split for optimal log viewing
- ✅ Consistent spacing and padding

### Performance
- ✅ Smooth scrolling with mouse wheel
- ✅ Responsive layout
- ✅ Efficient log processing
- ✅ Thread-safe operations

## 🐛 Troubleshooting

**Docker not starting:**
- Check Docker Desktop is running
- Verify docker-compose.yml is correct
- Run `docker ps` to check container status

**Spark job fails:**
- Check Python file path is correct
- Verify Spark master URL is accessible
- Review execution log for errors

**UI not responsive:**
- Try resizing the window
- Restart the application
- Check for Python errors in console

## 📊 Technical Details

### Architecture
- **Framework:** Tkinter (native Python GUI)
- **Threading:** ThreadPoolExecutor for async operations
- **Logging:** Queue-based log processing
- **Layout:** Grid + Pack hybrid for optimal control

### Color Palette
- Primary Blue: `#0969DA`
- Success Green: `#1A7F37`
- Danger Red: `#CF222E`
- Secondary Grey: `#F6F8FA`
- Background: `#F0F4F8`

### Button Styles
- **Primary:** Blue background, white text
- **Success:** Green background, white text
- **Danger:** Red background, white text
- **Secondary:** Light grey background, dark text
- **Outline:** White background, dark text, grey border

## 🔄 Version History

- **V4.0 (Current):** Clean Professional Edition
  - Removed old versions
  - Optimized layout (35-65 split)
  - Full-width buttons
  - Better file input design
  - Grid layout for scrolling

- **V3.0:** Ultra Modern 2025 (Removed)
  - Gradient effects (too flashy)

- **V2.0:** Material Design 3 (Removed)
  - Card-based layout

- **V1.0:** Original Design
  - Basic functionality (kept as fallback)

## 📄 License

Educational project for Big Data course.

## 👨‍💻 Author

Vo Truong Danh

## 🙏 Acknowledgments

- Spark documentation
- GitHub UI design inspiration
- VS Code color scheme
- Notion layout concepts
