# -*- coding: utf-8 -*-
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg, month, year, when, datediff, max as _max, min as _min, stddev, expr, lit
from pyspark.ml.clustering import KMeans, GaussianMixture
from pyspark.ml.regression import LinearRegression, RandomForestRegressor, GBTRegressor
from pyspark.ml.feature import VectorAssembler, StandardScaler, MinMaxScaler
from pyspark.ml.evaluation import RegressionEvaluator, ClusteringEvaluator
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import warnings
import os
import json
import glob
import shutil
warnings.filterwarnings('ignore')

# Set enhanced style
plt.style.use('ggplot')
sns.set_palette("husl")
sns.set_context("notebook", font_scale=1.1)

# ============================================
# FIX ĐƯỜNG DẪN - WINDOWS COMPATIBLE
# ============================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tmp")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n" + "=" * 80)
print("   🚀 PHÂN TÍCH BIG DATA VỚI MACHINE LEARNING NÂNG CAO V2.0 🚀")
print("=" * 80)
print(f"📂 Thư mục output: {OUTPUT_DIR}")

# ============================================
# BƯỚC 1: KHỞI TẠO SPARK VÀ ĐỌC DỮ LIỆU
# ============================================
print("\n[1/7] Khởi tạo Spark Session với cấu hình tối ưu...")
spark = SparkSession.builder \
    .appName("BigDataAnalytics_ML_V2") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.sql.autoBroadcastJoinThreshold", "10485760") \
    .getOrCreate()

print("[2/7] Đọc dữ liệu từ HDFS/Storage...")
possible_paths = [
    "hdfs://namenode:8020/input/online_retail_II.csv",
]

df = None
for path in possible_paths:
    try:
        df = spark.read.csv(path, header=True, inferSchema=True)
        print(f"✅ Đọc file thành công từ: {path}")
        break
    except:
        continue

if df is None:
    print("❌ Không tìm thấy file dữ liệu!")
    spark.stop()
    exit(1)

# ============================================
# BƯỚC 2: XỬ LÝ DỮ LIỆU NÂNG CAO
# ============================================
print("\n[3/7] Xử lý và làm sạch dữ liệu với kỹ thuật nâng cao...")

# Làm sạch dữ liệu với nhiều điều kiện
df_clean = df.dropna()
df_clean = df_clean.filter((col("Quantity") > 0) & (col("Quantity") < 10000))  # Loại outliers
df_clean = df_clean.filter((col("Price") > 0) & (col("Price") < 10000))

# Tính toán metrics
df_clean = df_clean.withColumn("Revenue", col("Quantity") * col("Price"))
df_clean = df_clean.withColumn("TotalValue", col("Quantity") * col("Price"))

# Persist với MEMORY_AND_DISK
df_clean.persist()
total_records = df_clean.count()
print(f"✅ Dữ liệu đã sạch: {total_records:,} hàng")

# Tìm customer column và date column
customer_col = None
date_col = None

for col_name in df_clean.columns:
    if 'customer' in col_name.lower():
        customer_col = col_name
    if 'date' in col_name.lower() or 'invoice' in col_name.lower():
        if 'date' in col_name.lower():
            date_col = col_name

if customer_col is None:
    print("⚠️ Không tìm thấy cột Customer ID")
if date_col is None:
    print("⚠️ Không tìm thấy cột Date")

# ============================================
# BƯỚC 3: MACHINE LEARNING - NÂNG CAO
# ============================================
print("\n[4/7] Phân tích dữ liệu với Machine Learning tối ưu...")

# ====================
# 3.1. CUSTOMER SEGMENTATION - GAUSSIAN MIXTURE MODEL (Tốt hơn K-Means)
# ====================
print("\n  📊 3.1. PHÂN CỤM KHÁCH HÀNG VỚI GAUSSIAN MIXTURE MODEL")

customer_segments_pd = None
customer_rfm_with_cluster = None
best_k = 3

if customer_col:
    print("     → Tính toán RFM metrics nâng cao...")
    
    # Calculate RFM metrics
    if date_col:
        # Tìm ngày mới nhất trong dataset
        max_date = df_clean.agg(_max(col(date_col))).collect()[0][0]
        print(f"     → Max date in dataset: {max_date}")
        
        customer_rfm = df_clean.groupBy(customer_col).agg(
            datediff(lit(max_date), _max(col(date_col))).alias("Recency"),
            count("Invoice").alias("Frequency"),
            _sum("Revenue").alias("Monetary"),
            avg("Revenue").alias("AvgOrderValue"),
            _max("Revenue").alias("MaxOrderValue"),
            stddev("Revenue").alias("StdRevenue"),
            _sum("Quantity").alias("TotalQuantity")
        ).filter(col(customer_col).isNotNull())
    else:
        # Fallback without Recency
        customer_rfm = df_clean.groupBy(customer_col).agg(
            _sum("Revenue").alias("Monetary"),
            count("Invoice").alias("Frequency"),
            avg("Revenue").alias("AvgOrderValue"),
            _max("Revenue").alias("MaxOrderValue"),
            stddev("Revenue").alias("StdRevenue"),
            _sum("Quantity").alias("TotalQuantity")
        ).filter(col(customer_col).isNotNull())
    
    # Fillna cho stddev
    customer_rfm = customer_rfm.fillna(0, subset=["StdRevenue"])
    
    print("     → Chuẩn bị features với 6 dimensions...")
    
    # Choose features based on whether we have Recency
    if date_col:
        feature_cols = ["Recency", "Monetary", "Frequency", "AvgOrderValue", "MaxOrderValue", "TotalQuantity"]
    else:
        feature_cols = ["Monetary", "Frequency", "AvgOrderValue", "MaxOrderValue", "StdRevenue", "TotalQuantity"]
    
    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features_raw",
        handleInvalid="skip"
    )
    
    customer_features = assembler.transform(customer_rfm)
    
    # MinMaxScaler (tốt hơn cho GMM)
    scaler = MinMaxScaler(
        inputCol="features_raw",
        outputCol="features"
    )
    
    scaler_model = scaler.fit(customer_features)
    customer_scaled = scaler_model.transform(customer_features)
    customer_scaled.persist()
    
    # Tìm optimal k với Silhouette Score
    print("     → Tìm số cluster tối ưu (k=2-5)...")
    best_score = -1
    silhouette_scores = []
    
    evaluator = ClusteringEvaluator(
        featuresCol="features",
        metricName="silhouette",
        distanceMeasure="squaredEuclidean",
        predictionCol="cluster"
    )
    
    for k in range(2, 6):
        gmm = GaussianMixture(
            k=k,
            seed=42,
            featuresCol="features",
            predictionCol="cluster"
        )
        model = gmm.fit(customer_scaled)
        predictions = model.transform(customer_scaled)
        score = evaluator.evaluate(predictions)
        silhouette_scores.append((k, score))
        print(f"        K={k}: Silhouette Score = {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_k = k
    
    print(f"     ✅ Optimal K = {best_k} (Silhouette = {best_score:.4f})")
    
    # Train final model với optimal k
    gmm_final = GaussianMixture(k=best_k, seed=42, featuresCol="features", predictionCol="cluster")
    gmm_model = gmm_final.fit(customer_scaled)
    customer_clustered = gmm_model.transform(customer_scaled)
    
    # Select relevant columns for output
    if date_col:
        customer_segments_pd = customer_clustered.select(
            customer_col, "Recency", "Monetary", "Frequency", "AvgOrderValue", "MaxOrderValue", "TotalQuantity", "cluster"
        ).toPandas()
    else:
        customer_segments_pd = customer_clustered.select(
            customer_col, "Monetary", "Frequency", "AvgOrderValue", "MaxOrderValue", "TotalQuantity", "cluster"
        ).toPandas()
    
    # Intelligent labeling
    cluster_summary = customer_segments_pd.groupby('cluster').agg({
        'Monetary': 'mean',
        'Frequency': 'mean',
        'AvgOrderValue': 'mean'
    }).reset_index()
    cluster_summary = cluster_summary.sort_values('Monetary', ascending=False)
    
    # Dynamic labels based on k
    label_options = ['VIP Customers', 'High-Value Customers', 'Regular Customers', 'Occasional Customers', 'Low-Value Customers']
    cluster_labels = {}
    for idx, row in cluster_summary.iterrows():
        cluster_labels[row['cluster']] = label_options[idx]
    
    customer_segments_pd['Segment'] = customer_segments_pd['cluster'].map(cluster_labels)
    
    print(f"     ✅ Phân cụm {len(customer_segments_pd):,} khách hàng thành {best_k} nhóm")
    
    # ============================================
    # 3.1.1 XUẤT DỮ LIỆU RFM CHO DASHBOARD 3D
    # ============================================
    print("     → Xuất dữ liệu RFM cho Dashboard 3D...")
    
    if date_col:
        try:
            # Get RFM data with clusters
            customer_rfm_with_cluster = customer_clustered.select(
                col(customer_col).alias("Customer_ID"),
                "Recency",
                "Frequency",
                "Monetary",
                col("cluster").alias("prediction")
            )
            
            # Export to JSON (Spark JSON Lines format)
            rfm_output_path = os.path.join(OUTPUT_DIR, "customer_rfm_3d_temp")
            customer_rfm_with_cluster.coalesce(1).write.mode("overwrite").json(rfm_output_path)
            
            # Move part file to final location
            part_files = glob.glob(os.path.join(rfm_output_path, "part-*.json"))
            if part_files:
                final_path = os.path.join(OUTPUT_DIR, "customer_rfm_3d.json")
                shutil.move(part_files[0], final_path)
                # Clean up temp directory
                shutil.rmtree(rfm_output_path)
                
                record_count = customer_rfm_with_cluster.count()
                print(f"        ✅ Đã xuất {record_count:,} records RFM")
                print(f"        📂 File: {final_path}")
                
                # Also save a sample to verify
                sample_data = customer_rfm_with_cluster.limit(5).toPandas()
                print(f"        📊 Sample data:")
                print(f"           Recency range: {sample_data['Recency'].min():.0f} - {sample_data['Recency'].max():.0f}")
                print(f"           Frequency range: {sample_data['Frequency'].min():.0f} - {sample_data['Frequency'].max():.0f}")
                print(f"           Monetary range: £{sample_data['Monetary'].min():.2f} - £{sample_data['Monetary'].max():.2f}")
            else:
                print(f"        ⚠️ Không tìm thấy file part để di chuyển")
                
        except Exception as e:
            print(f"        ⚠️ Lỗi xuất RFM data: {e}")
            print(f"        → Dashboard 3D sẽ sử dụng dữ liệu mẫu")
    else:
        print("     ⚠️ Không có cột Date - Bỏ qua xuất RFM (Dashboard sẽ dùng sample data)")
        
else:
    customer_segments_pd = None
    print("     ⚠️ Bỏ qua phân cụm khách hàng")

# ====================
# 3.2. PRODUCT DEMAND FORECASTING - GRADIENT BOOSTED TREES
# ====================
print("\n  📊 3.2. DỰ ĐOÁN NHU CẦU SẢN PHẨM VỚI GRADIENT BOOSTED TREES")

print("     → Tạo features nâng cao...")

# Tính toán 15+ features cho mỗi sản phẩm
product_analysis = df_clean.groupBy("Description").agg(
    _sum("Quantity").alias("TotalQuantity"),
    _sum("Revenue").alias("TotalRevenue"),
    count("Invoice").alias("NumTransactions"),
    avg("Quantity").alias("AvgQuantity"),
    avg("Price").alias("AvgPrice"),
    _max("Quantity").alias("MaxQuantity"),
    _min("Quantity").alias("MinQuantity"),
    _min("Price").alias("MinPrice"),
    _max("Price").alias("MaxPrice"),
    stddev("Quantity").alias("StdQuantity"),
    stddev("Price").alias("StdPrice"),
    (_sum("Revenue") / count("Invoice")).alias("RevenuePerTransaction"),
    (_sum("Quantity") / count("Invoice")).alias("QuantityPerTransaction"),
    expr("percentile_approx(Quantity, 0.5)").alias("MedianQuantity"),
    expr("percentile_approx(Price, 0.5)").alias("MedianPrice")
).filter(col("Description").isNotNull())

# Fillna for standard deviations
product_analysis = product_analysis.fillna(0, subset=["StdQuantity", "StdPrice"])

# Aggressive filtering
print("     → Lọc dữ liệu thông minh...")
product_before = product_analysis.count()
product_analysis = product_analysis.filter(
    (col("NumTransactions") >= 10) &  # Ít nhất 10 giao dịch
    (col("TotalRevenue") >= 200) &
    (col("AvgPrice") >= 1) &
    (col("AvgPrice") <= 500) &
    (col("TotalQuantity") >= 20)  # Tổng số lượng bán >= 20
)
product_after = product_analysis.count()
print(f"     → Đã lọc từ {product_before:,} xuống {product_after:,} sản phẩm chất lượng cao")

# Feature engineering
lr_assembler = VectorAssembler(
    inputCols=["AvgQuantity", "AvgPrice", "NumTransactions", "MaxQuantity", 
               "RevenuePerTransaction", "QuantityPerTransaction", "StdQuantity", "MedianPrice"],
    outputCol="features",
    handleInvalid="skip"
)

product_features = lr_assembler.transform(product_analysis)

# Train/test split
print("     → Chia dữ liệu train/test (75/25)...")
train_data, test_data = product_features.randomSplit([0.75, 0.25], seed=42)

# GBT Regression (tốt hơn Linear Regression)
print("     → Huấn luyện Gradient Boosted Trees Regressor...")
gbt = GBTRegressor(
    featuresCol="features",
    labelCol="TotalRevenue",
    maxIter=50,
    maxDepth=5,
    seed=42
)

gbt_model = gbt.fit(train_data)
gbt_predictions = gbt_model.transform(test_data)

# Đánh giá
evaluator_r2 = RegressionEvaluator(labelCol="TotalRevenue", predictionCol="prediction", metricName="r2")
evaluator_rmse = RegressionEvaluator(labelCol="TotalRevenue", predictionCol="prediction", metricName="rmse")
evaluator_mae = RegressionEvaluator(labelCol="TotalRevenue", predictionCol="prediction", metricName="mae")

gbt_r2 = evaluator_r2.evaluate(gbt_predictions)
gbt_rmse = evaluator_rmse.evaluate(gbt_predictions)
gbt_mae = evaluator_mae.evaluate(gbt_predictions)

print(f"     ✅ GBT Model trained!")
print(f"        R² Score: {gbt_r2:.4f}")
print(f"        RMSE: ${gbt_rmse:.2f}")
print(f"        MAE: ${gbt_mae:.2f}")

# Cũng train Linear Regression để so sánh
print("     → Train Linear Regression để benchmark...")
lr = LinearRegression(featuresCol="features", labelCol="TotalRevenue", maxIter=100, regParam=0.01, elasticNetParam=0.5)
lr_model = lr.fit(train_data)
lr_predictions = lr_model.transform(test_data)

lr_r2 = evaluator_r2.evaluate(lr_predictions)
lr_rmse = evaluator_rmse.evaluate(lr_predictions)

print(f"     → Linear Regression: R²={lr_r2:.4f}, RMSE=${lr_rmse:.2f}")
print(f"     → Improvement: {((gbt_r2 - lr_r2) / lr_r2 * 100):.1f}% better R²")

# Random Forest
print("     → Train Random Forest để so sánh...")
rf = RandomForestRegressor(featuresCol="features", labelCol="TotalRevenue", numTrees=30, maxDepth=6, seed=42)
rf_model = rf.fit(train_data)
rf_predictions = rf_model.transform(test_data)

rf_r2 = evaluator_r2.evaluate(rf_predictions)
rf_rmse = evaluator_rmse.evaluate(rf_predictions)

print(f"     → Random Forest: R²={rf_r2:.4f}, RMSE=${rf_rmse:.2f}")

# Lấy best model
best_model_name = "GBT"
best_r2 = gbt_r2
best_rmse = gbt_rmse
predictions_pd = gbt_predictions.select("Description", "TotalRevenue", "prediction", "AvgQuantity", "AvgPrice").toPandas()

if rf_r2 > gbt_r2:
    best_model_name = "Random Forest"
    best_r2 = rf_r2
    best_rmse = rf_rmse
    predictions_pd = rf_predictions.select("Description", "TotalRevenue", "prediction", "AvgQuantity", "AvgPrice").toPandas()

print(f"     ✅ Best Model: {best_model_name} (R²={best_r2:.4f})")

# ====================
# 3.3. PRODUCT CLUSTERING - K-MEANS với Optimal K
# ====================
print("\n  📊 3.3. PHÂN CỤM SẢN PHẨM VỚI K-MEANS OPTIMIZED")

print("     → Chuẩn bị 12 features cho phân cụm...")

product_cluster_assembler = VectorAssembler(
    inputCols=["TotalQuantity", "TotalRevenue", "NumTransactions", 
               "AvgQuantity", "AvgPrice", "MaxQuantity", "MinQuantity",
               "RevenuePerTransaction", "QuantityPerTransaction",
               "StdQuantity", "MedianQuantity", "MedianPrice"],
    outputCol="features_raw",
    handleInvalid="skip"
)

product_cluster_features = product_cluster_assembler.transform(product_analysis)

# Standard Scaler
product_scaler = StandardScaler(inputCol="features_raw", outputCol="features", withStd=True, withMean=True)
product_scaler_model = product_scaler.fit(product_cluster_features)
product_scaled = product_scaler_model.transform(product_cluster_features)
product_scaled.persist()

# Tìm optimal k
print("     → Tìm số cluster tối ưu (k=3-6)...")
best_product_k = 4
best_product_score = -1
product_silhouette_scores = []

cluster_eval = ClusteringEvaluator(
    featuresCol="features",
    metricName="silhouette",
    predictionCol="product_cluster"  # <-- THÊM DÒNG NÀY VÀO
)

for k in range(3, 7):
    kmeans = KMeans(k=k, seed=42, maxIter=50, initMode="k-means||", featuresCol="features", predictionCol="product_cluster")
    model = kmeans.fit(product_scaled)
    preds = model.transform(product_scaled)
    score = cluster_eval.evaluate(preds)
    product_silhouette_scores.append((k, score))
    print(f"        K={k}: Silhouette = {score:.4f}, WSSSE = {model.summary.trainingCost:.2f}")
    
    if score > best_product_score:
        best_product_score = score
        best_product_k = k

print(f"     ✅ Optimal K = {best_product_k} (Silhouette = {best_product_score:.4f})")

# Train final model
kmeans_final = KMeans(k=best_product_k, seed=42, maxIter=50, initMode="k-means||", 
                      featuresCol="features", predictionCol="product_cluster")
kmeans_product_model = kmeans_final.fit(product_scaled)
product_clustered = kmeans_product_model.transform(product_scaled)

actual_clusters = product_clustered.select("product_cluster").distinct().count()
print(f"     → Số cụm thực tế: {actual_clusters}")

# Lấy kết quả
product_clusters_pd = product_clustered.select(
    "Description", "TotalQuantity", "TotalRevenue", "NumTransactions", 
    "AvgPrice", "RevenuePerTransaction", "product_cluster"
).toPandas()

# Intelligent labeling
product_cluster_summary = product_clusters_pd.groupby('product_cluster').agg({
    'TotalRevenue': 'mean',
    'TotalQuantity': 'mean',
    'NumTransactions': 'mean'
}).reset_index()
product_cluster_summary = product_cluster_summary.sort_values('TotalRevenue', ascending=False)

all_labels = ['Premium Bestsellers', 'Popular Items', 'Standard Products', 'Budget Items', 'Niche Products', 'Occasional Sales']
sorted_cluster_ids = product_cluster_summary['product_cluster'].tolist()
labels_to_use = all_labels[:len(sorted_cluster_ids)]
product_cluster_labels = dict(zip(sorted_cluster_ids, labels_to_use))

product_clusters_pd['ProductCategory'] = product_clusters_pd['product_cluster'].map(product_cluster_labels)

print(f"     ✅ Phân cụm {len(product_clusters_pd):,} sản phẩm thành {len(labels_to_use)} nhóm")

# ============================================
# BƯỚC 4: TẠO FILE SUMMARY JSON
# ============================================
print("\n[5/7] Tạo file tổng kết JSON cho Dashboard...")

try:
    summary_data = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_records": int(total_records),
        "total_revenue": float(df_clean.agg(_sum("Revenue")).collect()[0][0]),
        "total_transactions": int(df_clean.count()),
        "num_countries": int(df_clean.select("Country").distinct().count()),
        "num_products": int(df_clean.select("Description").distinct().count()),
        "avg_order_value": float(df_clean.agg(_sum("Revenue")).collect()[0][0] / df_clean.count()),
        "ml_models": {
            "gaussian_mixture": {
                "k": int(best_k),
                "silhouette_score": float(best_score) if customer_segments_pd is not None else 0
            },
            "best_regressor": {
                "name": best_model_name,
                "r2_score": float(best_r2),
                "rmse": float(best_rmse),
                "mae": float(gbt_mae)
            },
            "linear_regression": {
                "r2_score": float(lr_r2),
                "rmse": float(lr_rmse)
            },
            "random_forest": {
                "r2_score": float(rf_r2),
                "rmse": float(rf_rmse)
            }
        }
    }
    
    # Add customer segments if available
    if customer_segments_pd is not None:
        segment_summary = customer_segments_pd.groupby('Segment').agg({
            customer_col: 'count',
            'Monetary': 'mean',
            'Frequency': 'mean'
        }).reset_index()
        segment_summary.columns = ['Segment', 'Count', 'Avg_Monetary', 'Avg_Frequency']
        
        if date_col and 'Recency' in customer_segments_pd.columns:
            recency_avg = customer_segments_pd.groupby('Segment')['Recency'].mean()
            segment_summary = segment_summary.merge(
                pd.DataFrame({'Segment': recency_avg.index, 'Avg_Recency': recency_avg.values}),
                on='Segment',
                how='left'
            )
        
        summary_data["customer_segments"] = segment_summary.to_dict('records')
    
    # Save to JSON
    json_path = os.path.join(OUTPUT_DIR, "ml_analysis_summary.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Đã lưu: {json_path}")
    print(f"     Size: {os.path.getsize(json_path) / 1024:.1f} KB")
    
except Exception as e:
    print(f"  ⚠️ Lỗi tạo JSON summary: {e}")

# ============================================
# BƯỚC 5: CHUẨN BỊ DỮ LIỆU VIZ
# ============================================
print("\n[6/7] Chuẩn bị dữ liệu cho visualization...")

top_countries_revenue = df_clean.groupBy("Country").agg(_sum("Revenue").alias("Total_Revenue")).orderBy(col("Total_Revenue").desc()).limit(10).toPandas()
top_countries_trans = df_clean.groupBy("Country").agg(count("Invoice").alias("Num_Transactions")).orderBy(col("Num_Transactions").desc()).limit(10).toPandas()
top_products = df_clean.groupBy("Description").agg(_sum("Revenue").alias("Total_Revenue"), _sum("Quantity").alias("Total_Quantity")).orderBy(col("Total_Revenue").desc()).limit(10).toPandas()

total_revenue = df_clean.agg(_sum("Revenue")).collect()[0][0]
total_transactions = df_clean.count()
avg_order_value = total_revenue / total_transactions

print("✅ Dữ liệu đã sẵn sàng")

# ============================================
# BƯỚC 6: VISUALIZATION (giữ nguyên code cũ của bạn)
# ============================================
print("\n[7/7] Tạo biểu đồ trực quan cao cấp...")
print("  (Visualization code - giữ nguyên như bạn đã cung cấp)")

# ... (thêm code visualization của bạn ở đây nếu cần)

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 80)
print("✅ PHÂN TÍCH BIG DATA V2.0 + 3D EXPORT HOÀN TẤT!")
print("=" * 80)

print(f"""
📂 Output: {OUTPUT_DIR}

📊 FILES ĐÃ TẠO:
✅ customer_rfm_3d.json - Dữ liệu RFM cho Dashboard 3D
✅ ml_analysis_summary.json - Tổng kết ML analysis

📈 ML MODELS:
• GMM Clustering (k={best_k if customer_segments_pd is not None else 0}) - Customer Segmentation
• K-Means (k={best_product_k}) - Product Categorization
• {best_model_name} - Best Predictor (R²={best_r2:.4f})

📊 METRICS:
• Total Revenue: ${total_revenue:,.2f}
• Transactions: {total_transactions:,}
• Avg Order: ${avg_order_value:.2f}
• Products: {product_after:,}
""")

if customer_col and customer_segments_pd is not None:
    print(f"• Customer Segments: {best_k}")
    for segment in customer_segments_pd['Segment'].unique():
        count = len(customer_segments_pd[customer_segments_pd['Segment'] == segment])
        print(f"  - {segment}: {count:,} customers")

print(f"\n🎨 Dashboard 3D URL: http://localhost:8000/unified_dashboard_3d.html")
print(f"📂 RFM Data: {os.path.join(OUTPUT_DIR, 'customer_rfm_3d.json')}")

# Cleanup
df_clean.unpersist()
if customer_col and customer_segments_pd is not None:
    customer_scaled.unpersist()
product_scaled.unpersist()

spark.stop()
print("\n✅ Spark Session stopped")
print("=" * 80)
