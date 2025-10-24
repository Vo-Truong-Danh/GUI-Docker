# HTML Dashboard Integration Guide

## 📊 Overview

The ML Analytics Dashboard (`ml_analytics_dashboard.html`) is a modern web-based visualization tool that displays results from the ML Analytics Tab in the Tkinter GUI application.

## 🎯 Features

### Dashboard Components

1. **Header Section**
   - Application title with branding
   - Last update timestamp
   - Status indicators

2. **Key Metrics Cards**
   - Total Records processed
   - Total Revenue generated
   - Number of Countries analyzed
   - Number of Products found

3. **Data Visualization Tabs**
   - **Overview**: Revenue distribution pie chart and analysis summary
   - **Countries**: Top countries by revenue with market share
   - **Products**: Top products by revenue with units sold
   - **Visualizations**: ML analysis charts and graphs

4. **Interactive Tables**
   - Ranking badges (#1, #2, etc.)
   - Data sorting and filtering ready
   - Progress bars for market share
   - Responsive design for mobile devices

5. **Real-time Charts**
   - Interactive pie charts using Chart.js
   - Auto-refresh every 10 seconds
   - Cache busting for image updates

## 📁 File Structure

```
GUI-Docker/
├── ml_analytics_dashboard.html    # Main HTML dashboard
├── ml_analytics_bridge.js         # Data bridge for connectivity
├── run_spark_gui/
│   ├── main.py                    # Main Tkinter app
│   ├── ml_analytics_tab.py        # ML Analytics Tab
│   └── code7.py                   # ML analysis logic
└── /tmp/                          # Output directory
    ├── ml_analysis_summary.json   # Analysis results (JSON)
    └── ml_analysis_results.png    # Visualization charts (PNG)
```

## 🚀 How It Works

### Data Flow

```
code7.py (PySpark ML)
    ↓
    ├─→ Generates: ml_analysis_summary.json
    ├─→ Generates: ml_analysis_results.png
    └─→ Creates visualizations (K-Means, Linear Regression, etc.)
    
    ↓
    
ml_analytics_dashboard.html
    ├─→ Reads JSON data
    ├─→ Updates metrics cards
    ├─→ Populates data tables
    ├─→ Loads visualization images
    └─→ Auto-refreshes every 10 seconds
```

### Output Format (ml_analysis_summary.json)

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "total_records": 500000,
  "total_revenue": 1250000.50,
  "num_countries": 25,
  "num_products": 500,
  "top_countries": [
    {
      "Country": "United States",
      "Total_Revenue": 450000.00
    },
    {
      "Country": "United Kingdom",
      "Total_Revenue": 320000.00
    }
  ],
  "top_products": [
    {
      "Description": "Product Name A",
      "Total_Revenue": 80000.00
    },
    {
      "Description": "Product Name B",
      "Total_Revenue": 75000.00
    }
  ]
}
```

## 🎨 Visual Design

### Color Scheme (Modern Purple Theme)
- **Primary**: #667eea (Purple Blue)
- **Secondary**: #764ba2 (Dark Purple)
- **Success**: #48bb78 (Green)
- **Warning**: #ed8936 (Orange)
- **Danger**: #f56565 (Red)
- **Background**: Linear gradient (667eea → 764ba2)

### Typography
- **Headlines**: Segoe UI, 700 weight
- **Body Text**: Segoe UI, 400 weight
- **Monospace**: For metrics values

### Responsive Breakpoints
- **Desktop**: Full grid layout with side-by-side tables
- **Tablet**: Adjusted card sizes, stacked components
- **Mobile**: Single column layout, touch-friendly elements

## 🔄 Integration Steps

### Step 1: Run ML Analysis in Tkinter Tab
```
1. Open GUI application (main.py)
2. Navigate to "ML Analytics" tab
3. Select input CSV file
4. Click "🚀 Start Analysis"
5. Wait for "✅ ANALYSIS COMPLETED SUCCESSFULLY!"
```

### Step 2: View Results in HTML Dashboard
```
1. Open ml_analytics_dashboard.html in web browser
2. Dashboard automatically loads JSON data from /tmp/
3. Visualizations appear in tabs
4. Data auto-refreshes every 10 seconds
```

### Step 3: Monitor Live Updates
```
- Timestamp shows last update time
- Metrics cards update automatically
- Tables refresh with new data
- Charts re-render on data changes
```

## 💡 Usage Examples

### View Top Performing Countries
1. Click "Countries" tab
2. Review ranked list with market share percentages
3. Sort by revenue to see top performers

### Analyze Product Performance
1. Click "Products" tab
2. Check top products by revenue
3. Review unit sales estimates

### Monitor Data Quality
1. Check "Overview" tab
2. Verify total records processed
3. Review analysis date and status

## 🛠️ Configuration

### Auto-Refresh Interval
Edit the refresh interval in `ml_analytics_dashboard.html` (line ~450):

```javascript
// Change 10000 to desired milliseconds
// 10000 = 10 seconds, 5000 = 5 seconds
this.autoRefreshInterval = setInterval(async () => {
    console.log('🔄 Auto-refreshing data...');
    const data = await this.loadData();
    if (data) {
        this.updateMetrics(data);
        this.updateTables(data);
    }
}, 10000);  // ← Modify this value
```

### Data Path Configuration
Update the default data path in dashboard initialization:

```javascript
// Change /tmp/ to your output directory
async loadData(dataPath = '/tmp/ml_analysis_summary.json') {
    // ...
}
```

### Theme Customization
Modify CSS variables in the `<style>` section:

```css
/* Change primary color */
--primary-color: #667eea;
--secondary-color: #764ba2;

/* Change gradient background */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 📊 Supported Data Types

### Metrics
- Integer values (records, countries, products)
- Float values (revenue, percentages)
- Strings (timestamps, country names, product descriptions)

### Tables
- Rankings with automatic badge generation
- Progress bars for percentages
- Currency formatting ($)
- Locale-aware number formatting (Vietnamese/English)

### Charts
- Pie/Doughnut charts (revenue distribution)
- Bar charts (top performers)
- Line charts (trends over time)
- PNG images (ML visualization outputs)

## 🐛 Troubleshooting

### Dashboard shows "No data available"
- Ensure ML analysis has been run in Tkinter tab
- Check if `/tmp/ml_analysis_summary.json` exists
- Verify file permissions are readable

### Charts not loading
- Check if `/tmp/ml_analysis_results.png` exists
- Clear browser cache (Ctrl+Shift+Delete)
- Reload page (F5 or Ctrl+R)

### Data not updating
- Check browser console for errors (F12)
- Verify auto-refresh interval is running
- Run a new analysis to generate fresh data

### Mobile display issues
- Use responsive browser zoom (Ctrl+/Ctrl+-)
- Check CSS media queries in source
- Test on different screen sizes

## 🔗 Related Files

- **ml_analytics_tab.py**: Generates analysis data
- **code7.py**: ML algorithms and visualization logic
- **main.py**: Main Tkinter GUI application
- **ml_analytics_bridge.js**: Data connectivity layer

## 📝 Notes

- Dashboard is read-only (no data editing)
- All data comes from JSON output of analysis
- Images cached with timestamp to prevent stale data
- Auto-refresh pauses when page is not focused (browser optimization)

## ✅ Best Practices

1. **Keep Browser Open**
   - Monitor live data updates
   - See real-time analysis progress

2. **Organize Output Files**
   - Store in consistent `/tmp/` location
   - Name files clearly (ml_analysis_*)
   - Backup important results

3. **Regular Analysis Runs**
   - Run analysis periodically
   - Compare results over time
   - Track trends and patterns

4. **Error Checking**
   - Verify data quality before analysis
   - Check browser console for errors
   - Enable logging in Tkinter tab

## 📞 Support

For issues or questions:
1. Check browser console (F12)
2. Review Tkinter app logs
3. Verify data output files exist
4. Run test suite (test_bugfix.py)

---

**Dashboard Version**: 1.0  
**Last Updated**: 2024  
**Framework**: HTML5 + Bootstrap 5 + Chart.js  
**Compatibility**: All modern browsers (Chrome, Firefox, Safari, Edge)
