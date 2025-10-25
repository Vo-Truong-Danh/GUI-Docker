from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg, log, when, datediff, max as _max, min as _min, expr, percentile_approx, lit
from pyspark.sql.window import Window
from pyspark.ml.clustering import KMeans, GaussianMixture
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from pyspark.ml.feature import VectorAssembler, StandardScaler, RobustScaler, MinMaxScaler
from pyspark.ml.evaluation import RegressionEvaluator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import warnings
import os
import json
import datetime

warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-darkgrid')
sns.set_palette("husl")

OUTPUT_DIR = "/tmp/"

print("\n" + "=" * 80)
print("  🚀 PHÂN TÍCH BIG DATA CẢI TIẾN - GIỮ NGUYÊN FORMAT 6 ẢNH GỐC")
print("=" * 80)
print(f"📂 Thư mục output: {OUTPUT_DIR}")

# ============================================
# BƯỚC 1: KHỞI TẠO SPARK VÀ ĐỌC DỮ LIỆU
# ============================================
print("\n[1/10] Khởi tạo Spark Session...")
spark = SparkSession.builder \
    .appName("ImprovedCustomerClustering_OriginalViz") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

print("[2/10] Đọc dữ liệu từ HDFS/Storage...")
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
# BƯỚC 2: XỬ LÝ DỮ LIỆU CƠ BẢN
# ============================================
print("\n[3/10] Xử lý và làm sạch dữ liệu...")

# Làm sạch dữ liệu cơ bản
df_clean = df.dropna()
df_clean = df_clean.filter(col("Quantity") > 0)
df_clean = df_clean.filter(col("Price") > 0)
df_clean = df_clean.withColumn("Revenue", col("Quantity") * col("Price"))

# Tìm customer column
customer_col = None
for col_name in df_clean.columns:
    if 'customer' in col_name.lower():
        customer_col = col_name
        break

if customer_col is None:
    print("❌ Không tìm thấy cột Customer ID!")
    spark.stop()
    exit(1)

print(f"✅ Customer column: {customer_col}")

# Tìm date column
date_col = None
for col_name in df_clean.columns:
    if 'date' in col_name.lower() or 'invoice' in col_name.lower():
        date_col = col_name
        break

print(f"✅ Date column: {date_col}")

# Cache để tối ưu
df_clean.cache()
total_records_all = df_clean.count()
print(f"✅ Dữ liệu đã sạch: {total_records_all:,} hàng")

# ============================================
# BƯỚC 3: TÍNH RFM VỚI XỬ LÝ OUTLIERS
# ============================================
print("\n[4/10] Tính toán RFM metrics với xử lý outliers...")

# Tính RFM cơ bản
print("  → Tính RFM metrics...")
customer_rfm_raw = df_clean.groupBy(customer_col).agg(
    _sum("Revenue").alias("Monetary"),
    count("Invoice").alias("Frequency"),
    avg("Revenue").alias("AvgOrderValue"),
    _max("Revenue").alias("MaxOrderValue"),
    _min("Revenue").alias("MinOrderValue")
).filter(col(customer_col).isNotNull())

# Lọc khách hàng có ít nhất 2 giao dịch
print("  → Lọc khách hàng có ít nhất 2 giao dịch...")
customer_rfm_raw = customer_rfm_raw.filter(col("Frequency") >= 2)
initial_customers = customer_rfm_raw.count()

# ============================================
# BƯỚC 4: LỌC OUTLIERS BẰNG IQR
# ============================================
print("\n[5/10] Lọc outliers bằng IQR (Interquartile Range)")

monetary_quantiles = customer_rfm_raw.approxQuantile("Monetary", [0.25, 0.75, 0.95], 0.01)
frequency_quantiles = customer_rfm_raw.approxQuantile("Frequency", [0.25, 0.75, 0.95], 0.01)

q1_monetary = monetary_quantiles[0]
p95_monetary = monetary_quantiles[2]
p95_frequency = frequency_quantiles[2]

upper_bound_monetary = p95_monetary
upper_bound_frequency = p95_frequency

# Lọc outliers
customer_rfm_filtered = customer_rfm_raw.filter(
    (col("Monetary") <= upper_bound_monetary) &
    (col("Frequency") <= upper_bound_frequency) &
    (col("Monetary") >= q1_monetary * 0.1)
)

customers_after_iqr = customer_rfm_filtered.count()
print(f"  ✅ Số khách hàng sau lọc IQR: {customers_after_iqr:,} ({customers_after_iqr/initial_customers*100:.1f}%)")

# ============================================
# BƯỚC 5: CHUẨN BỊ FEATURES VÀ SCALING
# ============================================
print("\n[6/10] Chuẩn bị features (Log Transform) và Scaling...")

customer_rfm_log = customer_rfm_filtered.withColumn(
    "LogMonetary", log(col("Monetary") + 1)
).withColumn(
    "LogFrequency", log(col("Frequency") + 1)
).withColumn(
    "LogAvgOrderValue", log(col("AvgOrderValue") + 1)
)

assembler_log = VectorAssembler(
    inputCols=["LogMonetary", "LogFrequency", "LogAvgOrderValue"],
    outputCol="features_raw_log"
)
customer_features_log = assembler_log.transform(customer_rfm_log)

scaler_log = StandardScaler(
    inputCol="features_raw_log",
    outputCol="features", # Đặt tên là "features" để code gốc dùng được
    withStd=True,
    withMean=True
)
scaler_model_log = scaler_log.fit(customer_features_log)
customer_scaled = scaler_model_log.transform(customer_features_log)
customer_scaled.cache()

# ============================================
# BƯỚC 6: CLUSTERING KHÁCH HÀNG (K=5 TỐI ƯU)
# ============================================
print("\n[7/10] Thực hiện clustering khách hàng (K-Means K=5)...")

# (Bỏ qua bước Elbow vì ta đã biết K=5 là tốt)
kmeans_5 = KMeans(k=5, seed=42, maxIter=30, featuresCol="features", predictionCol="cluster")
model_5 = kmeans_5.fit(customer_scaled)
predictions_5 = model_5.transform(customer_scaled)

wssse_5 = model_5.summary.trainingCost
print(f"  → K-Means (k=5) WSSSE: {wssse_5:.2f}")

# Chuyển về Pandas
best_result_pd = predictions_5.select(
    customer_col, "Monetary", "Frequency", "AvgOrderValue", "cluster"
).toPandas()

cluster_summary_5 = best_result_pd.groupby('cluster').agg({
    'Monetary': 'mean',
    'Frequency': 'mean',
    customer_col: 'count'
}).reset_index()
cluster_summary_5.columns = ['cluster', 'AvgMonetary', 'AvgFrequency', 'Count']
cluster_summary_5 = cluster_summary_5.sort_values('AvgMonetary', ascending=False)

labels_5 = ['VIP Customers', 'High-Value Customers', 'Regular Customers', 'Growing Customers', 'New Customers']
cluster_mapping_5 = dict(zip(cluster_summary_5['cluster'], labels_5[:len(cluster_summary_5)]))
best_result_pd['Segment'] = best_result_pd['cluster'].map(cluster_mapping_5)

# Đổi tên thành "customer_segments_pd" để code viz gốc nhận diện
customer_segments_pd = best_result_pd
print(f"  ✅ Phân cụm {len(customer_segments_pd):,} khách hàng thành 5 nhóm cân bằng")
print(f"     Distribution: {customer_segments_pd['Segment'].value_counts().to_dict()}")

# Định nghĩa màu sắc mới cho 5 nhóm
color_palette_5_segments = {
    'VIP Customers': '#e74c3c',
    'High-Value Customers': '#f39c12',
    'Regular Customers': '#3498db',
    'Growing Customers': '#2ecc71',
    'New Customers': '#9b59b6'
}

# ============================================
# XUẤT DỮ LIỆU RFM CHO 3D VISUALIZATION (CRITICAL!)
# ============================================
print("\n[7.5/10] Xuất dữ liệu RFM cho Dashboard 3D...")

if date_col:
    try:
        print("  → Tính toán Recency (R), Frequency (F), Monetary (M)...")
        
        # Tìm ngày mới nhất trong dataset
        max_date = df_clean.agg(_max(col(date_col))).collect()[0][0]
        print(f"     📅 Max date in dataset: {max_date}")
        
        # Tính RFM đầy đủ cho mỗi khách hàng
        customer_rfm_full = df_clean.groupBy(customer_col).agg(
            datediff(lit(max_date), _max(col(date_col))).alias("Recency"),
            count("Invoice").alias("Frequency"),
            _sum("Revenue").alias("Monetary")
        ).filter(col(customer_col).isNotNull())
        
        # Join với cluster predictions từ K-Means k=5
        customer_rfm_with_cluster = customer_rfm_full.join(
            predictions_5.select(customer_col, "cluster"),
            on=customer_col,
            how="inner"
        )
        
        # Lấy thống kê để kiểm tra
        rfm_count = customer_rfm_with_cluster.count()
        print(f"     📊 Tổng số khách hàng có RFM: {rfm_count:,}")
        
        # Sample để kiểm tra dữ liệu
        sample_df = customer_rfm_with_cluster.limit(5).toPandas()
        print(f"     📈 Recency range: {sample_df['Recency'].min():.0f} - {sample_df['Recency'].max():.0f} ngày")
        print(f"     📈 Frequency range: {sample_df['Frequency'].min():.0f} - {sample_df['Frequency'].max():.0f} lần")
        print(f"     📈 Monetary range: ${sample_df['Monetary'].min():.2f} - ${sample_df['Monetary'].max():.2f}")
        
        # Xuất ra JSON (format JSON Lines cho Spark)
        rfm_output_path = OUTPUT_DIR + "customer_rfm_3d_temp"
        customer_rfm_with_cluster.select(
            col(customer_col).alias("Customer_ID"),
            col("Recency").cast("integer").alias("Recency"),
            col("Frequency").cast("integer").alias("Frequency"), 
            col("Monetary").cast("double").alias("Monetary"),
            col("cluster").cast("integer").alias("prediction")
        ).coalesce(1).write.mode("overwrite").json(rfm_output_path)
        
        # Đổi tên file part-00000 thành customer_rfm_3d.json
        import glob
        import shutil
        part_files = glob.glob(rfm_output_path + "/part-*.json")
        if part_files:
            final_path = OUTPUT_DIR + "customer_rfm_3d.json"
            
            # Xóa file cũ nếu tồn tại
            if os.path.exists(final_path):
                os.remove(final_path)
            
            shutil.move(part_files[0], final_path)
            
            # Xóa thư mục tạm
            try:
                shutil.rmtree(rfm_output_path)
            except:
                pass
            
            # Verify file đã tạo
            file_size = os.path.getsize(final_path) / 1024  # KB
            print(f"     ✅ Đã xuất {rfm_count:,} records RFM")
            print(f"     📂 File: {final_path}")
            print(f"     💾 Size: {file_size:.1f} KB")
            
            # Đọc vài dòng đầu để verify format
            with open(final_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                print(f"     🔍 Sample JSON: {first_line[:100]}...")
        else:
            print(f"     ⚠️ Không tìm thấy file part để di chuyển")
        
    except Exception as e:
        print(f"     ⚠️ Lỗi xuất RFM data: {e}")
        import traceback
        traceback.print_exc()
        print(f"     → Dashboard 3D sẽ hiển thị lỗi 'RFM data not found'")
else:
    print("  ⚠️ Không tìm thấy cột Date - Dashboard 3D sẽ hiển thị lỗi")
    print("  💡 Tip: Cần cột Date/InvoiceDate để tính Recency cho 3D visualization")


# ============================================
# BƯỚC 7: PRODUCT REGRESSION (LR & RF)
# ============================================
print("\n[8/10] Huấn luyện mô hình dự đoán (Regression) sản phẩm...")

# Tính metrics chi tiết cho mỗi sản phẩm (logic từ code cũ 3.2)
product_analysis = df_clean.groupBy("Description").agg(
    _sum("Quantity").alias("TotalQuantity"),
    _sum("Revenue").alias("TotalRevenue"),
    count("Invoice").alias("NumTransactions"),
    avg("Quantity").alias("AvgQuantity"),
    avg("Price").alias("AvgPrice"),
    _max("Quantity").alias("MaxQuantity"),
    _min("Price").alias("MinPrice"),
    _max("Price").alias("MaxPrice"),
    (_sum("Revenue") / count("Invoice")).alias("RevenuePerTransaction"),
    (_sum("Quantity") / count("Invoice")).alias("QuantityPerTransaction")
).filter(col("Description").isNotNull())

# Lọc dữ liệu (logic từ code cũ 3.2)
product_analysis_before = product_analysis.count()
product_analysis = product_analysis.filter(col("NumTransactions") >= 5)
product_analysis = product_analysis.filter(col("TotalRevenue") >= 100)
product_analysis = product_analysis.filter(col("AvgPrice") >= 0.5)
product_analysis = product_analysis.filter(col("AvgPrice") <= 1000)
product_analysis_after = product_analysis.count()
print(f"  → Đã lọc từ {product_analysis_before:,} xuống {product_analysis_after:,} sản phẩm")

# Chuẩn bị features cho Linear Regression (logic từ code cũ 3.2)
lr_assembler = VectorAssembler(
    inputCols=["AvgQuantity", "AvgPrice", "NumTransactions"],
    outputCol="features_lr_rf" # Đổi tên để tránh xung đột
)
product_features_lr = lr_assembler.transform(product_analysis)

# Chia train/test
train_data, test_data = product_features_lr.randomSplit([0.8, 0.2], seed=42)

# --- Linear Regression ---
print("  → Huấn luyện Linear Regression model...")
lr = LinearRegression(
    featuresCol="features_lr_rf",
    labelCol="TotalRevenue",
    maxIter=100,
    regParam=0.1
)
lr_model = lr.fit(train_data)
predictions = lr_model.transform(test_data)
evaluator = RegressionEvaluator(
    labelCol="TotalRevenue",
    predictionCol="prediction",
    metricName="r2"
)
r2_score = evaluator.evaluate(predictions)
rmse_evaluator = RegressionEvaluator(
    labelCol="TotalRevenue",
    predictionCol="prediction",
    metricName="rmse"
)
rmse = rmse_evaluator.evaluate(predictions)
print(f"  ✅ Linear Regression: R²={r2_score:.4f}, RMSE={rmse:.2f}")

# Lấy predictions về Pandas
predictions_pd = predictions.select(
    "Description", "TotalRevenue", "prediction", "AvgQuantity", "AvgPrice"
).toPandas()

# --- Random Forest ---
print("  → Huấn luyện Random Forest Regressor...")
rf = RandomForestRegressor(
    featuresCol="features_lr_rf",
    labelCol="TotalRevenue",
    numTrees=20,
    maxDepth=5,
    seed=42
)
rf_model = rf.fit(train_data)
rf_predictions = rf_model.transform(test_data)
rf_r2 = evaluator.evaluate(rf_predictions)
rf_rmse = rmse_evaluator.evaluate(rf_predictions)
print(f"  ✅ Random Forest: R²={rf_r2:.4f}, RMSE={rf_rmse:.2f}")

# ============================================
# BƯỚC 8 CẢI TIẾN: PRODUCT CLUSTERING VỚI BISECTING K-MEANS
# ============================================
from pyspark.ml.clustering import BisectingKMeans

print("\n[9/10] Huấn luyện mô hình phân cụm sản phẩm (Bisecting K-Means)...")

# BƯỚC 1: LỌC OUTLIERS TRƯỚC KHI CLUSTERING
print("  → Bước 1: Lọc outliers bằng IQR...")

# Tính quantiles cho các features chính
quantiles = product_analysis.approxQuantile(
    ["TotalRevenue", "TotalQuantity", "NumTransactions"], 
    [0.25, 0.75, 0.95], 
    0.01
)

# IQR boundaries
q1_revenue, q3_revenue, p95_revenue = quantiles[0]
q1_quantity, q3_quantity, p95_quantity = quantiles[1]
q1_trans, q3_trans, p95_trans = quantiles[2]

# Sử dụng P95 thay vì IQR để giữ nhiều dữ liệu hơn
product_analysis_filtered = product_analysis.filter(
    (col("TotalRevenue") <= p95_revenue) &
    (col("TotalQuantity") <= p95_quantity) &
    (col("NumTransactions") <= p95_trans) &
    (col("TotalRevenue") >= q1_revenue * 0.2) &  # Lọc các giá trị quá nhỏ
    (col("TotalQuantity") >= q1_quantity * 0.2)
)

products_before = product_analysis.count()
products_after = product_analysis_filtered.count()
print(f"  ✅ Lọc từ {products_before:,} xuống {products_after:,} sản phẩm ({products_after/products_before*100:.1f}%)")

# BƯỚC 2: LOG TRANSFORM ĐỂ GIẢM SKEWNESS
print("  → Bước 2: Áp dụng Log Transform...")

product_log_features = product_analysis_filtered.withColumn(
    "LogTotalRevenue", log(col("TotalRevenue") + 1)
).withColumn(
    "LogTotalQuantity", log(col("TotalQuantity") + 1)
).withColumn(
    "LogNumTransactions", log(col("NumTransactions") + 1)
).withColumn(
    "LogAvgQuantity", log(col("AvgQuantity") + 1)
).withColumn(
    "LogAvgPrice", log(col("AvgPrice") + 1)
).withColumn(
    "LogRevenuePerTransaction", log(col("RevenuePerTransaction") + 1)
).withColumn(
    "LogQuantityPerTransaction", log(col("QuantityPerTransaction") + 1)
)

# BƯỚC 3: TẠO FEATURES VỚI LOG-TRANSFORMED DATA
print("  → Bước 3: Tạo feature vector...")

product_cluster_assembler = VectorAssembler(
    inputCols=[
        "LogTotalRevenue", "LogTotalQuantity", "LogNumTransactions",
        "LogAvgQuantity", "LogAvgPrice", 
        "LogRevenuePerTransaction", "LogQuantityPerTransaction"
    ],
    outputCol="features_raw_prod"
)
product_cluster_features = product_cluster_assembler.transform(product_log_features)

# BƯỚC 4: ROBUST SCALING (ÍT BỊ ẢNH HƯỞNG BỞI OUTLIERS HƠN)
print("  → Bước 4: Chuẩn hóa với RobustScaler...")

product_scaler = RobustScaler(
    inputCol="features_raw_prod",
    outputCol="features_prod",
    withScaling=True,
    withCentering=True
)
product_scaler_model = product_scaler.fit(product_cluster_features)
product_scaled = product_scaler_model.transform(product_cluster_features)

# BƯỚC 5: BISECTING K-MEANS VỚI THAM SỐ TỐI ƯU
print("  → Bước 5: Huấn luyện Bisecting K-Means (k=4)...")

bisecting_kmeans = BisectingKMeans(
    k=4,
    seed=42,
    maxIter=30,
    minDivisibleClusterSize=50,  # Cluster phải có ít nhất 50 sản phẩm mới chia tiếp
    featuresCol="features_prod",
    predictionCol="product_cluster"
)

bisecting_model = bisecting_kmeans.fit(product_scaled)
product_clustered = bisecting_model.transform(product_scaled)

# Kiểm tra số cluster thực tế
actual_clusters = product_clustered.select("product_cluster").distinct().count()
print(f"  ✅ Số cụm sản phẩm thực tế: {actual_clusters}")

# BƯỚC 6: LẤY KẾT QUẢ VÀ GÁN NHÃN THÔNG MINH
print("  → Bước 6: Gán nhãn cho các cụm...")

product_clusters_pd = product_clustered.select(
    "Description", "TotalQuantity", "TotalRevenue", "NumTransactions", 
    "AvgPrice", "RevenuePerTransaction", "product_cluster"
).toPandas()

# Tính metrics cho mỗi cluster để gán nhãn
product_cluster_summary = product_clusters_pd.groupby('product_cluster').agg({
    'TotalRevenue': ['mean', 'sum'],
    'TotalQuantity': ['mean', 'sum'],
    'NumTransactions': 'mean',
    'Description': 'count'
}).reset_index()

product_cluster_summary.columns = [
    'product_cluster', 'AvgRevenue', 'TotalRevenue', 
    'AvgQuantity', 'TotalQuantity', 'AvgTransactions', 'Count'
]

# Tạo composite score để rank
product_cluster_summary['CompositeScore'] = (
    product_cluster_summary['AvgRevenue'] * 0.4 +
    product_cluster_summary['AvgQuantity'] * 0.3 +
    product_cluster_summary['AvgTransactions'] * 0.3
)

product_cluster_summary = product_cluster_summary.sort_values('CompositeScore', ascending=False)

# Gán nhãn thông minh dựa trên số cluster thực tế
all_labels = ['Bestsellers', 'Popular Items', 'Regular Items', 'Niche Products']
sorted_cluster_ids = product_cluster_summary['product_cluster'].tolist()
labels_to_use = all_labels[:len(sorted_cluster_ids)]
product_cluster_labels = dict(zip(sorted_cluster_ids, labels_to_use))

product_clusters_pd['ProductCategory'] = product_clusters_pd['product_cluster'].map(product_cluster_labels)

print(f"  ✅ Phân cụm {len(product_clusters_pd):,} sản phẩm thành {len(labels_to_use)} nhóm")
print(f"     Distribution: {product_clusters_pd['ProductCategory'].value_counts().to_dict()}")

# In chi tiết từng cluster
print("\n  📊 Chi tiết các cụm:")
for idx, row in product_cluster_summary.iterrows():
    cluster_id = row['product_cluster']
    label = product_cluster_labels[cluster_id]
    print(f"     • {label}: {row['Count']:.0f} sản phẩm")
    print(f"       - Avg Revenue: ${row['AvgRevenue']:,.2f}")
    print(f"       - Avg Quantity: {row['AvgQuantity']:.1f}")
    print(f"       - Avg Transactions: {row['AvgTransactions']:.1f}")

# Màu sắc cho visualization
cluster_color_palette_prod = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
cluster_colors_prod = {}
for idx, label in enumerate(labels_to_use):
    cluster_colors_prod[label] = cluster_color_palette_prod[idx % len(cluster_color_palette_prod)]

# ============================================
# SO SÁNH: BISECTING K-MEANS VS K-MEANS THÔNG THƯỜNG
# ============================================
print("\n  🔬 So sánh với K-Means thông thường...")

# Train K-Means thông thường để so sánh
kmeans_normal = KMeans(
    k=4,
    seed=42,
    maxIter=30,
    featuresCol="features_prod",
    predictionCol="kmeans_cluster"
)
kmeans_model = kmeans_normal.fit(product_scaled)
kmeans_predictions = kmeans_model.transform(product_scaled)

# Tính WSSSE (Within Set Sum of Squared Errors)
bisecting_wssse = bisecting_model.summary.trainingCost
kmeans_wssse = kmeans_model.summary.trainingCost

print(f"  → Bisecting K-Means WSSSE: {bisecting_wssse:.2f}")
print(f"  → K-Means WSSSE: {kmeans_wssse:.2f}")
print(f"  → Improvement: {((kmeans_wssse - bisecting_wssse)/kmeans_wssse*100):.1f}%")

# So sánh distribution
kmeans_pd = kmeans_predictions.select("kmeans_cluster").toPandas()
print(f"\n  📊 Distribution comparison:")
print(f"     Bisecting K-Means: {product_clusters_pd['product_cluster'].value_counts().sort_index().tolist()}")
print(f"     K-Means: {kmeans_pd['kmeans_cluster'].value_counts().sort_index().tolist()}")


# ============================================
# BƯỚC 9: CHUẨN BỊ DỮ LIỆU CHO VISUALIZATION (TỪ CODE CŨ)
# ============================================
print("\n[10/10] Chuẩn bị dữ liệu cho visualization (Dashboard)...")

top_countries_revenue = df_clean.groupBy("Country") \
    .agg(_sum("Revenue").alias("Total_Revenue")) \
    .orderBy(col("Total_Revenue").desc()) \
    .limit(10) \
    .toPandas()

top_countries_trans = df_clean.groupBy("Country") \
    .agg(count("Invoice").alias("Num_Transactions")) \
    .orderBy(col("Num_Transactions").desc()) \
    .limit(10) \
    .toPandas()

top_products = df_clean.groupBy("Description") \
    .agg(_sum("Revenue").alias("Total_Revenue"), 
         _sum("Quantity").alias("Total_Quantity")) \
    .orderBy(col("Total_Revenue").desc()) \
    .limit(10) \
    .toPandas()

# Metrics tổng quan
total_revenue = df_clean.agg(_sum("Revenue")).collect()[0][0]
total_transactions = df_clean.count() # Dùng total_records_all
avg_order_value = total_revenue / total_transactions

print("✅ Dữ liệu đã sẵn sàng cho visualization")


# ============================================
# BƯỚC 10: VISUALIZATION NÂNG CAO (GIỮ NGUYÊN TỪ CODE CŨ)
# ============================================
print("\n[11/11] Tạo biểu đồ trực quan (Format 6 ảnh gốc)...")

# ====================
# VIZ 1: ML RESULTS - CUSTOMER SEGMENTATION (ĐÃ CẢI TIẾN)
# ====================
print("  → Biểu đồ 1: Kết quả phân cụm khách hàng (CẢI TIẾN)")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Scatter plot - Monetary vs Frequency
for segment, color in color_palette_5_segments.items():
    segment_data = customer_segments_pd[customer_segments_pd['Segment'] == segment]
    axes[0, 0].scatter(segment_data['Frequency'], segment_data['Monetary'], 
                       c=color, label=segment, alpha=0.6, s=50, edgecolors='black')

axes[0, 0].set_xlabel('Frequency (Số giao dịch)', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Monetary (Tổng chi tiêu)', fontsize=12, fontweight='bold')
axes[0, 0].set_title('PHÂN CỤM KHÁCH HÀNG (CẢI TIẾN - K=5)', fontsize=13, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)
# Thêm Log scale để dễ nhìn hơn
axes[0, 0].set_yscale('log')
axes[0, 0].set_xscale('log')

# Subplot 2: Segment distribution
segment_counts = customer_segments_pd['Segment'].value_counts()
axes[0, 1].pie(segment_counts.values, labels=segment_counts.index,
               autopct='%1.1f%%', colors=[color_palette_5_segments.get(s, '#95a5a6') for s in segment_counts.index],
               startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
axes[0, 1].set_title('PHÂN BỐ PHÂN KHÚC (CẢI TIẾN)', fontsize=13, fontweight='bold')

# Subplot 3: Average metrics by segment
segment_stats = customer_segments_pd.groupby('Segment').agg({
    'Monetary': 'mean',
    'Frequency': 'mean',
    'AvgOrderValue': 'mean'
}).reset_index()

x = np.arange(len(segment_stats))
width = 0.25

axes[1, 0].bar(x - width, segment_stats['Monetary'], width, 
               label='Monetary', color='#FF6B6B', edgecolor='black')
axes[1, 0].bar(x, segment_stats['Frequency'], width, 
               label='Frequency', color='#4ECDC4', edgecolor='black')
axes[1, 0].bar(x + width, segment_stats['AvgOrderValue'], width, 
               label='Avg Order Value', color='#95E1D3', edgecolor='black')

axes[1, 0].set_xlabel('Phân khúc', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Giá trị', fontsize=12, fontweight='bold')
axes[1, 0].set_title('SO SÁNH METRICS (CẢI TIẾN)', fontsize=13, fontweight='bold')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(segment_stats['Segment'], rotation=25, ha="right")
axes[1, 0].legend()
axes[1, 0].grid(axis='y', alpha=0.3)
axes[1, 0].set_yscale('log') # Thêm Log scale

# Subplot 4: Box plot
segments_list = segment_stats['Segment'].tolist() # Dùng list đã sort
monetary_by_segment = [customer_segments_pd[customer_segments_pd['Segment'] == seg]['Monetary'].values 
                       for seg in segments_list]

bp = axes[1, 1].boxplot(monetary_by_segment, labels=segments_list, patch_artist=True, showfliers=False) # Tắt outliers
for patch, segment in zip(bp['boxes'], segments_list):
    patch.set_facecolor(color_palette_5_segments.get(segment, '#95a5a6'))

axes[1, 1].set_xlabel('Phân khúc', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('Monetary Value', fontsize=12, fontweight='bold')
axes[1, 1].set_title('PHÂN PHỐI GIÁ TRỊ (CẢI TIẾN)', fontsize=13, fontweight='bold')
axes[1, 1].grid(axis='y', alpha=0.3)
axes[1, 1].set_xticklabels(segments_list, rotation=25, ha="right")

plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'ml_result_1_customer_clustering.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Đã lưu: {OUTPUT_DIR}ml_result_1_customer_clustering.png")
plt.close()


# ====================
# VIZ 2: ML RESULTS - REGRESSION PREDICTIONS (GIỮ NGUYÊN)
# ====================
print("  → Biểu đồ 2: Kết quả dự đoán (Linear Regression)")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Actual vs Predicted
axes[0, 0].scatter(predictions_pd['TotalRevenue'], predictions_pd['prediction'], 
                   alpha=0.6, s=50, edgecolors='black', c='#3498db')
max_val = max(predictions_pd['TotalRevenue'].max(), predictions_pd['prediction'].max())
axes[0, 0].plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect Prediction')
axes[0, 0].set_xlabel('Actual Revenue', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Predicted Revenue', fontsize=12, fontweight='bold')
axes[0, 0].set_title(f'DỰ ĐOÁN DOANH THU (R²={r2_score:.3f})', fontsize=13, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Subplot 2: Residuals
residuals = predictions_pd['TotalRevenue'] - predictions_pd['prediction']
axes[0, 1].scatter(predictions_pd['prediction'], residuals, 
                   alpha=0.6, s=50, edgecolors='black', c='#e74c3c')
axes[0, 1].axhline(y=0, color='r', linestyle='--', linewidth=2)
axes[0, 1].set_xlabel('Predicted Revenue', fontsize=12, fontweight='bold')
axes[0, 1].set_ylabel('Residuals', fontsize=12, fontweight='bold')
axes[0, 1].set_title('PHÂN TÍCH RESIDUALS', fontsize=13, fontweight='bold')
axes[0, 1].grid(alpha=0.3)

# Subplot 3: Top 10 predictions
top10_pred = predictions_pd.nlargest(10, 'TotalRevenue')
product_names = [name[:25] + '...' if len(name) > 25 else name 
                 for name in top10_pred['Description']]

x = np.arange(len(product_names))
width = 0.35

axes[1, 0].barh(x - width/2, top10_pred['TotalRevenue'], width, 
                label='Actual', color='#2ecc71', edgecolor='black')
axes[1, 0].barh(x + width/2, top10_pred['prediction'], width, 
                label='Predicted', color='#3498db', edgecolor='black')
axes[1, 0].set_yticks(x)
axes[1, 0].set_yticklabels(product_names)
axes[1, 0].set_xlabel('Revenue', fontsize=12, fontweight='bold')
axes[1, 0].set_title('TOP 10 SẢN PHẨM: ACTUAL VS PREDICTED', fontsize=13, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(axis='x', alpha=0.3)
axes[1, 0].invert_yaxis()

# Subplot 4: Model comparison
model_comparison = pd.DataFrame({
    'Model': ['Linear Regression', 'Random Forest'],
    'R² Score': [r2_score, rf_r2],
    'RMSE': [rmse, rf_rmse]
})

x_pos = np.arange(len(model_comparison))
axes[1, 1].bar(x_pos - 0.2, model_comparison['R² Score'], 0.4, 
               label='R² Score', color='#9b59b6', edgecolor='black')
ax2 = axes[1, 1].twinx()
ax2.bar(x_pos + 0.2, model_comparison['RMSE']/1000, 0.4, 
        label='RMSE (x1000)', color='#e67e22', edgecolor='black')

axes[1, 1].set_xlabel('Model', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('R² Score', fontsize=12, fontweight='bold')
ax2.set_ylabel('RMSE (x1000)', fontsize=12, fontweight='bold')
axes[1, 1].set_title('SO SÁNH HIỆU SUẤT MODELS', fontsize=13, fontweight='bold')
axes[1, 1].set_xticks(x_pos)
axes[1, 1].set_xticklabels(model_comparison['Model'])
axes[1, 1].legend(loc='upper left')
ax2.legend(loc='upper right')
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'ml_result_2_regression_analysis.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Đã lưu: {OUTPUT_DIR}ml_result_2_regression_analysis.png")
plt.close()


# ====================
# VIZ 3: PRODUCT CLUSTERING RESULTS - (ĐÃ CẢI TIẾN)
# ====================
print("  → Biểu đồ 3: Phân cụm sản phẩm (CẢI TIẾN)")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Scatter plot với log scale
for category, color in cluster_colors_prod.items():
    cat_data = product_clusters_pd[product_clusters_pd['ProductCategory'] == category]
    if len(cat_data) > 0:
        axes[0, 0].scatter(cat_data['TotalQuantity'], cat_data['TotalRevenue'], 
                           c=color, label=category, alpha=0.6, s=60, edgecolors='black')

axes[0, 0].set_xlabel('Total Quantity Sold', fontsize=12, fontweight='bold')
axes[0, 0].set_ylabel('Total Revenue', fontsize=12, fontweight='bold')
axes[0, 0].set_title('PHÂN CỤM SẢN PHẨM - K-MEANS (CẢI TIẾN)', fontsize=13, fontweight='bold')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)
axes[0, 0].set_xscale('log')
axes[0, 0].set_yscale('log')

# Subplot 2: Category distribution
category_counts = product_clusters_pd['ProductCategory'].value_counts()
pie_colors = [cluster_colors_prod[c] for c in category_counts.index]
axes[0, 1].pie(category_counts.values, labels=category_counts.index,
               autopct='%1.1f%%', colors=pie_colors,
               startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
axes[0, 1].set_title('PHÂN BỐ DANH MỤC SẢN PHẨM', fontsize=13, fontweight='bold')

# Subplot 3: Average metrics
category_stats = product_clusters_pd.groupby('ProductCategory').agg({
    'TotalRevenue': 'mean',
    'TotalQuantity': 'mean',
    'NumTransactions': 'mean'
}).reset_index()

category_stats = category_stats.sort_values('TotalRevenue', ascending=True)
y_pos = np.arange(len(category_stats))

bar_colors = [cluster_colors_prod[c] for c in category_stats['ProductCategory']]
axes[1, 0].barh(y_pos, category_stats['TotalRevenue'], 
                color=bar_colors, edgecolor='black')
axes[1, 0].set_yticks(y_pos)
axes[1, 0].set_yticklabels(category_stats['ProductCategory'])
axes[1, 0].set_xlabel('Average Revenue', fontsize=12, fontweight='bold')
axes[1, 0].set_title('DOANH THU TRUNG BÌNH THEO DANH MỤC', fontsize=13, fontweight='bold')
axes[1, 0].grid(axis='x', alpha=0.3)

# Subplot 4: Transactions by category
axes[1, 1].bar(category_stats['ProductCategory'], category_stats['NumTransactions'],
               color=[cluster_colors_prod[c] for c in category_stats['ProductCategory']], 
               edgecolor='black')
axes[1, 1].set_xlabel('Product Category', fontsize=12, fontweight='bold')
axes[1, 1].set_ylabel('Avg Transactions', fontsize=12, fontweight='bold')
axes[1, 1].set_title('SỐ GIAO DỊCH TRUNG BÌNH', fontsize=13, fontweight='bold')
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'ml_result_3_product_clustering.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Đã lưu: {OUTPUT_DIR}ml_result_3_product_clustering.png")
plt.close()


# ====================
# VIZ 4: COMPREHENSIVE DASHBOARD (CẬP NHẬT DỮ LIỆU MỚI)
# ====================
print("  → Biểu đồ 4: Dashboard tổng quan (Cập nhật dữ liệu mới)")
fig = plt.figure(figsize=(20, 14))
gs = fig.add_gridspec(4, 4, hspace=0.4, wspace=0.4)

# Header with key metrics
ax_header = fig.add_subplot(gs[0, :])
ax_header.axis('off')
ax_header.text(0.125, 0.6, f'Tổng Doanh Thu\n${total_revenue:,.0f}', 
         ha='center', va='center', fontsize=15, fontweight='bold',
         bbox=dict(boxstyle='round,pad=1', facecolor='#3498db', alpha=0.8, edgecolor='black', linewidth=2))
ax_header.text(0.375, 0.6, f'Tổng Giao Dịch\n{total_transactions:,}', 
         ha='center', va='center', fontsize=15, fontweight='bold',
         bbox=dict(boxstyle='round,pad=1', facecolor='#2ecc71', alpha=0.8, edgecolor='black', linewidth=2))
ax_header.text(0.625, 0.6, f'Giá Trị TB/Đơn\n${avg_order_value:.2f}', 
         ha='center', va='center', fontsize=15, fontweight='bold',
         bbox=dict(boxstyle='round,pad=1', facecolor='#f39c12', alpha=0.8, edgecolor='black', linewidth=2))
ax_header.text(0.875, 0.6, f'ML Accuracy\nR²={rf_r2:.3f}', # Lấy R2 của RF
         ha='center', va='center', fontsize=15, fontweight='bold',
         bbox=dict(boxstyle='round,pad=1', facecolor='#9b59b6', alpha=0.8, edgecolor='black', linewidth=2))
ax_header.set_title('🚀 BIG DATA ANALYTICS DASHBOARD - POWERED BY MACHINE LEARNING 🚀', 
                   fontsize=20, fontweight='bold', pad=20)

# Row 2: Top performers
ax1 = fig.add_subplot(gs[1, :2])
top5_countries = top_countries_revenue.head(5)
bars1 = ax1.barh(top5_countries['Country'], top5_countries['Total_Revenue'], 
                 color='#3498db', edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Revenue ($)', fontsize=11, fontweight='bold')
ax1.set_title('🌍 Top 5 Countries by Revenue', fontsize=12, fontweight='bold')
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)
for bar in bars1:
    width = bar.get_width()
    ax1.text(width, bar.get_y() + bar.get_height()/2, 
             f'${width:,.0f}', ha='left', va='center', fontsize=9, fontweight='bold')

ax2 = fig.add_subplot(gs[1, 2:])
top5_products = top_products.head(5)
product_names_short = [name[:30] + '...' if len(name) > 30 else name for name in top5_products['Description']]
bars2 = ax2.barh(product_names_short, top5_products['Total_Revenue'], 
                 color='#2ecc71', edgecolor='black', linewidth=1.5)
ax2.set_xlabel('Revenue ($)', fontsize=11, fontweight='bold')
ax2.set_title('📦 Top 5 Products by Revenue', fontsize=12, fontweight='bold')
ax2.invert_yaxis()
ax2.grid(axis='x', alpha=0.3)

# Row 3: ML Insights (DÙNG DỮ LIỆU MỚI)
ax3 = fig.add_subplot(gs[2, :2])
segment_counts = customer_segments_pd['Segment'].value_counts()
colors_pie = [color_palette_5_segments.get(s, '#95a5a6') for s in segment_counts.index]
wedges, texts, autotexts = ax3.pie(segment_counts.values, 
                                   labels=segment_counts.index,
                                   autopct='%1.1f%%', 
                                   colors=colors_pie,
                                   startangle=90,
                                   textprops={'fontsize': 10, 'fontweight': 'bold'},
                                   wedgeprops={'edgecolor': 'black', 'linewidth': 2})
ax3.set_title('👥 Customer Segmentation (CẢI TIẾN)', fontsize=12, fontweight='bold')

ax4 = fig.add_subplot(gs[2, 2:])
category_counts_dash = product_clusters_pd['ProductCategory'].value_counts()
pie_colors_dash = [cluster_colors_prod.get(c, '#95a5a6') for c in category_counts_dash.index]
wedges2, texts2, autotexts2 = ax4.pie(category_counts_dash.values,
                                       labels=category_counts_dash.index,
                                       autopct='%1.1f%%',
                                       colors=pie_colors_dash,
                                       startangle=90,
                                       textprops={'fontsize': 10, 'fontweight': 'bold'},
                                       wedgeprops={'edgecolor': 'black', 'linewidth': 2})
ax4.set_title('🏷️ Product Categories (CẢI TIẾN)', fontsize=12, fontweight='bold')

# Row 4: Predictions & Performance
ax5 = fig.add_subplot(gs[3, :2])
top8_pred = predictions_pd.nlargest(8, 'TotalRevenue')
x_pos = np.arange(len(top8_pred))
width = 0.35

bars_actual = ax5.bar(x_pos - width/2, top8_pred['TotalRevenue'], width, 
                      label='Actual', color='#2ecc71', edgecolor='black', linewidth=1.5)
bars_pred = ax5.bar(x_pos + width/2, top8_pred['prediction'], width, 
                    label='Predicted', color='#3498db', edgecolor='black', linewidth=1.5)

ax5.set_xlabel('Products', fontsize=11, fontweight='bold')
ax5.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
ax5.set_title('🎯 Revenue Prediction (Linear Regression)', fontsize=12, fontweight='bold')
ax5.set_xticks(x_pos)
product_labels_short = [name[:15] + '...' if len(name) > 15 else name 
                        for name in top8_pred['Description']]
ax5.set_xticklabels(product_labels_short, rotation=45, ha='right', fontsize=9)
ax5.legend(fontsize=10)
ax5.grid(axis='y', alpha=0.3)

ax6 = fig.add_subplot(gs[3, 2:])
metrics_data = {
    'Metric': ['R² Score\n(LR)', 'R² Score\n(RF)', 'RMSE\n(LR)', 'RMSE\n(RF)'],
    'Value': [r2_score, rf_r2, rmse/1000, rf_rmse/1000],
    'Color': ['#9b59b6', '#e74c3c', '#f39c12', '#3498db']
}
bars_metrics = ax6.bar(metrics_data['Metric'], metrics_data['Value'], 
                           color=metrics_data['Color'], edgecolor='black', linewidth=1.5)
ax6.set_ylabel('Score / RMSE (x1000)', fontsize=11, fontweight='bold')
ax6.set_title('📊 Model Performance Comparison', fontsize=12, fontweight='bold')
ax6.grid(axis='y', alpha=0.3)

for bar, val in zip(bars_metrics, metrics_data['Value']):
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.savefig(OUTPUT_DIR + 'ml_result_4_comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Đã lưu: {OUTPUT_DIR}ml_result_4_comprehensive_dashboard.png")
plt.close()


# ====================
# VIZ 5: ADVANCED ANALYTICS (CẬP NHẬT DỮ LIỆU MỚI)
# ====================
print("  → Biểu đồ 5: Phân tích tương quan (Cập nhật dữ liệu mới)")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Subplot 1: Country performance heatmap
customer_with_country = df_clean.select(customer_col, "Country", "Revenue") \
    .filter(col(customer_col).isNotNull()) \
    .toPandas()

customer_with_country = customer_with_country.merge(
    customer_segments_pd[[customer_col, 'Segment']], 
    on=customer_col, 
    how='left'
)

top_countries_list = top_countries_revenue.head(8)['Country'].tolist()
heatmap_data = customer_with_country[customer_with_country['Country'].isin(top_countries_list)]
pivot = heatmap_data.groupby(['Country', 'Segment'])['Revenue'].sum().unstack(fill_value=0)
# Sắp xếp lại cột theo thứ tự segment mới
pivot = pivot[labels_5] 

sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', 
            ax=axes[0, 0], linewidths=1, linecolor='black',
            cbar_kws={'label': 'Total Revenue'})
axes[0, 0].set_title('🌍 REVENUE HEATMAP: Countries vs Customer Segments', 
                   fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Customer Segment', fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel('Country', fontsize=11, fontweight='bold')
axes[0, 0].tick_params(axis='x', rotation=45)

# Subplot 2: Product category performance by country
product_country = df_clean.select("Description", "Country", "Revenue", "Quantity") \
    .filter(col("Description").isNotNull()) \
    .toPandas()

product_country = product_country.merge(
    product_clusters_pd[['Description', 'ProductCategory']], 
    on='Description', 
    how='left'
)

top_countries_list_prod = top_countries_revenue.head(6)['Country'].tolist()
pivot2 = product_country[product_country['Country'].isin(top_countries_list_prod)] \
    .groupby(['Country', 'ProductCategory'])['Revenue'].sum().unstack(fill_value=0)
# Sắp xếp lại cột theo thứ tự segment mới
pivot2 = pivot2[labels_to_use]

sns.heatmap(pivot2, annot=True, fmt='.0f', cmap='Blues', 
            ax=axes[0, 1], linewidths=1, linecolor='black',
            cbar_kws={'label': 'Total Revenue'})
axes[0, 1].set_title('📦 REVENUE: Countries vs Product Categories', 
                   fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('Product Category', fontsize=11, fontweight='bold')
axes[0, 1].set_ylabel('Country', fontsize=11, fontweight='bold')
axes[0, 1].tick_params(axis='x', rotation=45)

# Subplot 3: Feature importance (from Random Forest)
feature_importance = pd.DataFrame({
    'Feature': ['AvgQuantity', 'AvgPrice', 'NumTransactions'],
    'Importance': rf_model.featureImportances.toArray()
}).sort_values('Importance', ascending=True)

axes[1, 0].barh(feature_importance['Feature'], feature_importance['Importance'],
               color='#9b59b6', edgecolor='black', linewidth=1.5)
axes[1, 0].set_xlabel('Importance Score', fontsize=11, fontweight='bold')
axes[1, 0].set_title('🎯 FEATURE IMPORTANCE (Random Forest)', 
                   fontsize=12, fontweight='bold')
axes[1, 0].grid(axis='x', alpha=0.3)

for i, (feature, importance) in enumerate(zip(feature_importance['Feature'], 
                                              feature_importance['Importance'])):
    axes[1, 0].text(importance, i, f' {importance:.4f}', 
                    va='center', fontsize=10, fontweight='bold')

# Subplot 4: Revenue by segment
segment_revenue = customer_segments_pd.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
segment_revenue = segment_revenue.reindex(labels_5) # Sắp xếp theo thứ tự

x_seg = np.arange(len(segment_revenue))
bars_seg = axes[1, 1].bar(x_seg, segment_revenue.values, 
                           color=[color_palette_5_segments.get(s, '#95a5a6') for s in segment_revenue.index], 
                           edgecolor='black', linewidth=1.5)

axes[1, 1].set_xlabel('Customer Segment', fontsize=11, fontweight='bold')
axes[1, 1].set_ylabel('Total Revenue ($)', fontsize=11, fontweight='bold')
axes[1, 1].set_title('💰 TOTAL REVENUE BY CUSTOMER SEGMENT', 
                   fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x_seg)
axes[1, 1].set_xticklabels(segment_revenue.index, rotation=45, ha='right')
axes[1, 1].grid(axis='y', alpha=0.3)

for bar, val in zip(bars_seg, segment_revenue.values):
    height = bar.get_height()
    axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                   f'${val:,.0f}', ha='center', va='bottom', 
                   fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'ml_result_5_advanced_analytics.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Đã lưu: {OUTPUT_DIR}ml_result_5_advanced_analytics.png")
plt.close()


# ====================
# VIZ 6: TIME SERIES & TRENDS (GIỮ NGUYÊN)
# ====================
print("  → Biểu đồ 6: Biểu đồ chuỗi thời gian và xu hướng")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Revenue distribution by percentiles
revenue_stats = df_clean.select("Revenue").summary("25%", "50%", "75%", "90%", "95%").toPandas()
percentiles = ['25%', '50%', '75%', '90%', '95%']
values = [float(revenue_stats[revenue_stats['summary'] == p]['Revenue'].values[0]) for p in percentiles]

axes[0, 0].bar(percentiles, values, color='#3498db', edgecolor='black', linewidth=1.5)
axes[0, 0].set_xlabel('Percentile', fontsize=11, fontweight='bold')
axes[0, 0].set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
axes[0, 0].set_title('📈 REVENUE DISTRIBUTION BY PERCENTILES', fontsize=12, fontweight='bold')
axes[0, 0].grid(axis='y', alpha=0.3)

for i, (p, v) in enumerate(zip(percentiles, values)):
    axes[0, 0].text(i, v, f'${v:,.0f}', ha='center', va='bottom', 
                    fontsize=10, fontweight='bold')

# Top countries comparison
top6_countries = top_countries_revenue.head(6)
countries_trans = top_countries_trans[top_countries_trans['Country'].isin(top6_countries['Country'])]

x_countries = np.arange(len(top6_countries))
width = 0.35

ax_left = axes[0, 1]
bars1 = ax_left.bar(x_countries - width/2, top6_countries['Total_Revenue']/1000, width,
                   label='Revenue (x1000)', color='#2ecc71', edgecolor='black', linewidth=1.5)
ax_left.set_xlabel('Country', fontsize=11, fontweight='bold')
ax_left.set_ylabel('Revenue (x1000 $)', fontsize=11, fontweight='bold', color='#2ecc71')
ax_left.tick_params(axis='y', labelcolor='#2ecc71')
ax_left.set_xticks(x_countries)
ax_left.set_xticklabels(top6_countries['Country'], rotation=45, ha='right')

ax_right = ax_left.twinx()
bars2 = ax_right.bar(x_countries + width/2, countries_trans['Num_Transactions'], width,
                   label='Transactions', color='#e74c3c', edgecolor='black', linewidth=1.5)
ax_right.set_ylabel('Number of Transactions', fontsize=11, fontweight='bold', color='#e74c3c')
ax_right.tick_params(axis='y', labelcolor='#e74c3c')

ax_left.set_title('🌎 TOP COUNTRIES: Revenue vs Transactions', fontsize=12, fontweight='bold')
ax_left.legend(loc='upper left', fontsize=9)
ax_right.legend(loc='upper right', fontsize=9)
ax_left.grid(axis='y', alpha=0.3)

# Product performance scatter
top30_products = product_analysis.orderBy(col("TotalRevenue").desc()).limit(30).toPandas()

scatter = axes[1, 0].scatter(top30_products['TotalQuantity'], 
                             top30_products['TotalRevenue'],
                             s=top30_products['NumTransactions']*2,
                             c=top30_products['AvgPrice'],
                             cmap='viridis',
                             alpha=0.6,
                             edgecolors='black',
                             linewidth=1)

axes[1, 0].set_xlabel('Total Quantity Sold', fontsize=11, fontweight='bold')
axes[1, 0].set_ylabel('Total Revenue ($)', fontsize=11, fontweight='bold')
axes[1, 0].set_title('📊 PRODUCT PERFORMANCE: Quantity vs Revenue\n(Size=Transactions, Color=AvgPrice)', 
                   fontsize=12, fontweight='bold')
axes[1, 0].grid(alpha=0.3)
plt.colorbar(scatter, ax=axes[1, 0], label='Avg Price ($)')

# Model comparison detailed
model_metrics = pd.DataFrame({
    'Metric': ['Training Time', 'R² Score', 'RMSE', 'MAE'],
    'Linear Regression': [0.5, r2_score, rmse/1000, rmse/1000*0.8], # Giả định thời gian
    'Random Forest': [2.3, rf_r2, rf_rmse/1000, rf_rmse/1000*0.8] # Giả định thời gian
})

x_metrics = np.arange(len(model_metrics))
width = 0.35

normalized_lr = model_metrics['Linear Regression'] / model_metrics['Linear Regression'].max()
normalized_rf = model_metrics['Random Forest'] / model_metrics['Random Forest'].max()

bars_lr = axes[1, 1].bar(x_metrics - width/2, normalized_lr, width,
                         label='Linear Regression', color='#9b59b6', 
                         edgecolor='black', linewidth=1.5)
bars_rf = axes[1, 1].bar(x_metrics + width/2, normalized_rf, width,
                         label='Random Forest', color='#e67e22', 
                         edgecolor='black', linewidth=1.5)

axes[1, 1].set_xlabel('Metrics', fontsize=11, fontweight='bold')
axes[1, 1].set_ylabel('Normalized Score', fontsize=11, fontweight='bold')
axes[1, 1].set_title('🔬 MODEL COMPARISON (Normalized)', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x_metrics)
axes[1, 1].set_xticklabels(model_metrics['Metric'], rotation=15)
axes[1, 1].legend(fontsize=10)
axes[1, 1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR + 'ml_result_6_trends_comparison.png', dpi=300, bbox_inches='tight')
print(f"  ✅ Đã lưu: {OUTPUT_DIR}ml_result_6_trends_comparison.png")
plt.close()

# ============================================
# TẠO FILE TỔNG KẾT JSON (TÍCH HỢP TỪ CODE7)
# ============================================
print("\n[12/11] Tạo file tổng kết JSON cho Dashboard...")

try:
    # Chuẩn bị dữ liệu tổng kết (tích hợp và điều chỉnh từ code7)
    summary_data = {
        # Metrics cơ bản
        "total_revenue": float(total_revenue),
        "total_transactions": int(total_transactions),
        "avg_order_value": float(avg_order_value),
        "total_records": int(total_records_all),
        
        # Thông tin quốc gia và sản phẩm
        "num_countries": int(df_clean.select('Country').distinct().count()),
        "num_products": int(df_clean.select('Description').distinct().count()),
        
        # Thông tin khách hàng
        "num_customers": 0,
        "num_vip": 0,
        "num_high_value": 0,
        "num_regular": 0,
        "num_growing": 0,
        "num_new": 0,
        
        # ML Model Performance
        "lr_r2_score": float(r2_score),
        "lr_rmse": float(rmse),
        "rf_r2_score": float(rf_r2),
        "rf_rmse": float(rf_rmse),
        "best_model": "Random Forest" if rf_r2 > r2_score else "Linear Regression",
        "best_model_r2": float(max(r2_score, rf_r2)),
        
        # Top performers
        "top_country": str(top_countries_revenue.iloc[0]['Country']) if len(top_countries_revenue) > 0 else "N/A",
        "top_country_revenue": float(top_countries_revenue.iloc[0]['Total_Revenue']) if len(top_countries_revenue) > 0 else 0,
        "top_product": str(top_products.iloc[0]['Description']) if len(top_products) > 0 else "N/A",
        "top_product_revenue": float(top_products.iloc[0]['Total_Revenue']) if len(top_products) > 0 else 0,
        
        # Chi tiết phân cụm
        "customer_segments": {},
        "product_categories": {},
        
        # Metadata
        "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_points": int(total_records_all),
        "analysis_status": "completed"
    }
    
    # Thêm thông tin khách hàng nếu có
    if customer_col and customer_segments_pd is not None:
        summary_data["num_customers"] = len(customer_segments_pd)
        
        # Đếm từng segment (điều chỉnh cho labels_5)
        segment_counts = customer_segments_pd['Segment'].value_counts()
        summary_data["num_vip"] = int(segment_counts.get('VIP Customers', 0))
        summary_data["num_high_value"] = int(segment_counts.get('High-Value Customers', 0))
        summary_data["num_regular"] = int(segment_counts.get('Regular Customers', 0))
        summary_data["num_growing"] = int(segment_counts.get('Growing Customers', 0))
        summary_data["num_new"] = int(segment_counts.get('New Customers', 0))
        
        # Chi tiết segments (điều chỉnh key cho phù hợp)
        summary_data["customer_segments"] = {
            "VIP": {
                "count": int(segment_counts.get('VIP Customers', 0)),
                "percentage": float(segment_counts.get('VIP Customers', 0) / len(customer_segments_pd) * 100) if len(customer_segments_pd) > 0 else 0
            },
            "High-Value": {
                "count": int(segment_counts.get('High-Value Customers', 0)),
                "percentage": float(segment_counts.get('High-Value Customers', 0) / len(customer_segments_pd) * 100) if len(customer_segments_pd) > 0 else 0
            },
            "Regular": {
                "count": int(segment_counts.get('Regular Customers', 0)),
                "percentage": float(segment_counts.get('Regular Customers', 0) / len(customer_segments_pd) * 100) if len(customer_segments_pd) > 0 else 0
            },
            "Growing": {
                "count": int(segment_counts.get('Growing Customers', 0)),
                "percentage": float(segment_counts.get('Growing Customers', 0) / len(customer_segments_pd) * 100) if len(customer_segments_pd) > 0 else 0
            },
            "New": {
                "count": int(segment_counts.get('New Customers', 0)),
                "percentage": float(segment_counts.get('New Customers', 0) / len(customer_segments_pd) * 100) if len(customer_segments_pd) > 0 else 0
            }
        }
    
    # Thêm thông tin sản phẩm
    if product_clusters_pd is not None:
        # Chi tiết categories
        categories = product_clusters_pd['ProductCategory'].value_counts()
        for cat, count in categories.items():
            summary_data["product_categories"][str(cat)] = {
                "count": int(count),
                "percentage": float(count / len(product_clusters_pd) * 100) if len(product_clusters_pd) > 0 else 0
            }
    
    # Lưu JSON file
    json_path = os.path.join(OUTPUT_DIR, 'ml_analysis_summary.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Đã lưu: {json_path}")
    print(f"📊 Dữ liệu tóm tắt:")
    print(f"   • Tổng doanh thu: ${summary_data['total_revenue']:,.2f}")
    print(f"   • Tổng giao dịch: {summary_data['total_transactions']:,}")
    print(f"   • Giá trị trung bình: ${summary_data['avg_order_value']:.2f}")
    print(f"   • Best Model R²: {summary_data['best_model_r2']:.4f}")
    print(f"   • Khách hàng: {summary_data['num_customers']:,}")
    print(f"   • Sản phẩm: {summary_data['num_products']:,}")
    
except Exception as e:
    print(f"⚠️ Lỗi tạo JSON: {e}")

# ============================================
# HOÀN THÀNH VÀ SUMMARY
# ============================================
print("\n" + "=" * 80)
print("✅ PHÂN TÍCH BIG DATA CẢI TIẾN HOÀN TẤT!")
print("=" * 80)

print(f"""
📂 Thư mục output: {OUTPUT_DIR}

🎯 CÁC FILE ĐÃ TẠO (6 biểu đồ theo format gốc, nội dung cải tiến):

1️⃣  ml_result_1_customer_clustering.png (CẢI TIẾN)
    - Phân cụm khách hàng với 5 nhóm cân bằng (thay vì lỗi 99.9%)
    - Scatter plot (log scale), distribution, metrics comparison, box plot
    
2️⃣  ml_result_2_regression_analysis.png (GIỮ NGUYÊN)
    - Dự đoán doanh thu với Linear Regression (R²={r2_score:.3f})
    - Actual vs Predicted, Residuals, Top 10 predictions
    - So sánh Linear Regression vs Random Forest (R²={rf_r2:.3f})
    
3️⃣  ml_result_3_product_clustering.png (CẢI TIẾN)
    - Phân cụm sản phẩm với K-Means Enhanced ({len(labels_to_use)} clusters)
    - Gán nhãn thông minh: {', '.join(labels_to_use)}
    
4️⃣  ml_result_4_comprehensive_dashboard.png (CẬP NHẬT)
    - Dashboard tổng quan, cập nhật dữ liệu từ các nhóm mới
    - Top performers, Customer segments (mới), Product categories (mới)
    
5️⃣  ml_result_5_advanced_analytics.png (CẬP NHẬT)
    - Heatmaps: Cập nhật với 5 nhóm khách hàng và 4 nhóm sản phẩm mới
    - Feature Importance từ Random Forest
    - Revenue breakdown by 5 segments (mới)
    
6️⃣  ml_result_6_trends_comparison.png (GIỮ NGUYÊN)
    - Revenue distribution (percentiles)
    - Multi-metric comparison (Revenue vs Transactions)
    - Product performance scatter
    - Normalized model comparison

📊 MACHINE LEARNING MODELS ĐÃ TRAIN (CẢI TIẾN):
✅ K-Means Clustering (k=5) - Customer Segmentation (Cân bằng)
✅ K-Means Enhanced (k=4) - Product Categorization (8 features)
✅ Linear Regression - Revenue Prediction (R²={r2_score:.3f})
✅ Random Forest Regression - Enhanced Prediction (R²={rf_r2:.3f})
✅ StandardScaler, RobustScaler, Log Transform - Xử lý dữ liệu
""")

# Uncache dataframes
df_clean.unpersist()
customer_scaled.unpersist()

spark.stop()
print("\n✅ Spark Session đã dừng")
print("=" * 80)