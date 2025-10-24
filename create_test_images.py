#!/usr/bin/env python3
"""
Tạo ảnh PNG test và JSON data cho dashboard
"""
import json
import os
from PIL import Image, ImageDraw

# Đảm bảo thư mục tmp tồn tại
os.makedirs('tmp', exist_ok=True)

# Thông tin 6 biểu đồ
charts = [
    ('ml_result_1_customer_clustering.png', 'Customer Clustering', 'K-Means Analysis'),
    ('ml_result_2_regression_analysis.png', 'Regression Analysis', 'Linear & Random Forest'),
    ('ml_result_3_product_clustering.png', 'Product Clustering', 'Bisecting K-Means'),
    ('ml_result_4_comprehensive_dashboard.png', 'Comprehensive Dashboard', 'All Metrics'),
    ('ml_result_5_advanced_analytics.png', 'Advanced Analytics', 'Heatmaps & Importance'),
    ('ml_result_6_trends_comparison.png', 'Trends Comparison', 'Time Series Analysis')
]

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']

for idx, (filename, title, subtitle) in enumerate(charts):
    # Tạo ảnh 800x600 với background trắng
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Convert hex color to RGB
    color_hex = colors[idx]
    color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
    
    # Vẽ header bar với màu
    draw.rectangle([(0, 0), (800, 120)], fill=color_rgb)
    
    # Vẽ border
    draw.rectangle([(0, 0), (799, 599)], outline=(200, 200, 200), width=2)
    
    # Vẽ title
    draw.text((400, 40), title, fill=(255, 255, 255), anchor='mm')
    draw.text((400, 75), subtitle, fill=(255, 255, 255), anchor='mm')
    
    # Vẽ content area
    draw.rectangle([(40, 150), (760, 550)], outline=(220, 220, 220), width=2)
    
    # Vẽ placeholder text
    draw.text((400, 350), 'Chart Placeholder', fill=(150, 150, 150), anchor='mm')
    draw.text((400, 380), 'Run code7.py for real data', fill=(180, 180, 180), anchor='mm')
    
    # Lưu file PNG
    path = os.path.join('tmp', filename)
    img.save(path, 'PNG')
    size_kb = os.path.getsize(path) / 1024
    print(f'✓ {filename} ({size_kb:.1f} KB)')

# Tạo JSON test data
json_data = {
    "total_revenue": 9989237.5,
    "total_records": 797885,
    "avg_order_value": 12.52,
    "num_countries": 37,
    "num_products": 4070,
    "num_customers": 30398,
    "num_vip": 1245,
    "num_regular": 8932,
    "num_occasional": 20221,
    "lr_r2_score": 0.8247,
    "lr_rmse": 31.45,
    "rf_r2_score": 0.8301,
    "rf_rmse": 30.12,
    "best_model": "Random Forest",
    "best_model_r2": 0.8301,
    "top_country": "United Kingdom",
    "top_country_revenue": 8187000.5,
    "top_product": "WHITE HANGING HEART T-LIGHT HOLDER",
    "top_product_revenue": 284000.0,
    "analysis_date": "2025-10-25",
    "analysis_status": "Success",
    "customer_segments": {
        "VIP": {"count": 1245, "percentage": 4.1},
        "Regular": {"count": 8932, "percentage": 29.4},
        "Occasional": {"count": 20221, "percentage": 66.5}
    }
}

json_path = os.path.join('tmp', 'ml_analysis_summary.json')
with open(json_path, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f'✓ ml_analysis_summary.json ({os.path.getsize(json_path) / 1024:.1f} KB)')
print('\n✅ Tất cả files đã được tạo thành công!')
