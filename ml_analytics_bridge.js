/**
 * ML Analytics Dashboard - Data Bridge
 * Kết nối dữ liệu từ code7.py và hiển thị trên HTML Dashboard
 */

class MLAnalyticsBridge {
    constructor() {
        this.dashboardPath = 'ml_analytics_dashboard.html';
        this.dataPath = '/tmp/ml_analysis_summary.json';
        this.chartPath = '/tmp/ml_analysis_results.png';
    }

    /**
     * Load data từ JSON file (output của code7.py)
     */
    async loadAnalysisData() {
        try {
            const response = await fetch(this.dataPath);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error loading analysis data:', error);
            return null;
        }
    }

    /**
     * Update dashboard với dữ liệu mới
     */
    updateDashboard(data) {
        if (!data) return;

        // Update metrics
        this.updateMetrics(data);

        // Update tables
        this.updateTables(data);

        // Update charts
        this.updateCharts(data);

        // Update timestamp
        document.getElementById('timestamp').textContent = 
            new Date(data.timestamp).toLocaleString('vi-VN');
    }

    /**
     * Update key metrics cards
     */
    updateMetrics(data) {
        const elem = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        elem('totalRecords', data.total_records?.toLocaleString() || '--');
        elem('totalRevenue', '$' + (data.total_revenue?.toLocaleString('en-US', {maximumFractionDigits: 2}) || '--'));
        elem('numCountries', data.num_countries || '--');
        elem('numProducts', data.num_products?.toLocaleString() || '--');
    }

    /**
     * Update data tables
     */
    updateTables(data) {
        // Top countries table
        const countriesTable = document.getElementById('topCountriesTable');
        if (countriesTable && data.top_countries) {
            countriesTable.innerHTML = data.top_countries.map((item, idx) => `
                <tr>
                    <td>${idx + 1}</td>
                    <td>${item.Country || item.country || '--'}</td>
                    <td>$${(item.Total_Revenue || item.total_revenue || 0).toLocaleString()}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(idx + 1) * 15}%"></div>
                        </div>
                        ${(idx + 1) * 10}%
                    </td>
                </tr>
            `).join('');
        }

        // Top products table
        const productsTable = document.getElementById('topProductsTable');
        if (productsTable && data.top_products) {
            productsTable.innerHTML = data.top_products.map((item, idx) => `
                <tr>
                    <td>${idx + 1}</td>
                    <td>${(item.Description || item.description || '--').substring(0, 50)}</td>
                    <td>$${(item.Total_Revenue || item.total_revenue || 0).toLocaleString()}</td>
                    <td>${Math.floor((idx + 1) * 100)}K</td>
                </tr>
            `).join('');
        }
    }

    /**
     * Update charts
     */
    updateCharts(data) {
        // Load chart images
        const chartImg = document.querySelector('.chart-container img');
        if (chartImg) {
            chartImg.src = this.chartPath + '?t=' + new Date().getTime();
        }
    }

    /**
     * Tạo connection tới Tkinter app
     */
    connectToApp() {
        // Có thể tạo WebSocket hoặc HTTP endpoint để giao tiếp với Tkinter app
        console.log('Connecting to ML Analytics Tkinter app...');
    }
}

// Initialize
const bridge = new MLAnalyticsBridge();

// Auto-load data
window.addEventListener('load', async () => {
    const data = await bridge.loadAnalysisData();
    if (data) {
        bridge.updateDashboard(data);
    }
});

// Refresh data every 5 seconds
setInterval(async () => {
    const data = await bridge.loadAnalysisData();
    if (data) {
        bridge.updateDashboard(data);
    }
}, 5000);
