#!/bin/bash
# 🚀 QUICK START - Unified Dashboard

echo "📊 Big Data Analytics Dashboard - Unified Version"
echo "=================================================="
echo ""

# Check if running from correct directory
if [ ! -f "unified_dashboard.html" ]; then
    echo "❌ ERROR: Run this from GUI-Docker directory!"
    echo "   cd 'd:\BaiTapSinhVien\TH BigData\GUI-Docker'"
    exit 1
fi

# Show options
echo "Choose option:"
echo ""
echo "1️⃣  Start GUI (Dashboard + Server)"
echo "   cd run_spark_gui && python main.py"
echo ""
echo "2️⃣  Start HTTP Server only"
echo "   python -m http.server 8000"
echo ""
echo "3️⃣  Generate Real Data (code7.py)"
echo "   cd run_spark_gui && python code7.py"
echo ""
echo "4️⃣  Open Dashboard in Browser"
echo "   http://localhost:8000/unified_dashboard.html"
echo ""

read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting GUI..."
        cd run_spark_gui
        python main.py
        ;;
    2)
        echo "🚀 Starting HTTP Server..."
        python -m http.server 8000
        ;;
    3)
        echo "🚀 Running code7.py..."
        cd run_spark_gui
        python code7.py
        ;;
    4)
        echo "🚀 Opening Dashboard..."
        start http://localhost:8000/unified_dashboard.html
        ;;
    *)
        echo "❌ Invalid choice!"
        exit 1
        ;;
esac
