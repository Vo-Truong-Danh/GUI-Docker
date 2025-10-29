from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel

# 1. Khởi tạo Spark Session
spark = SparkSession.builder.appName("UseMyModel").getOrCreate()

# 2. Định nghĩa đường dẫn model
model_path = "hdfs://namenode:8020/output/model/als_model"

# 3. Tải model đã được huấn luyện
try:
    als_model = ALSModel.load(model_path)
    print(f"Tải model thành công từ: {model_path}")
except Exception as e:
    print(f"Không thể tải model: {e}")
    spark.stop()
    exit()

# 4. Chuẩn bị dữ liệu người dùng (user) cần gợi ý
#    Giả sử bạn muốn gợi ý cho người dùng có chỉ số (user_int) là 10 và 25
users_to_recommend = spark.createDataFrame([(10,), (25,)], ["user"])

# 5. Lấy 500 gợi ý hàng đầu cho những người dùng đó
N_RECOMMENDATIONS = 500
recommendations = als_model.recommendForUserSubset(users_to_recommend, N_RECOMMENDATIONS)

# 6. Hiển thị kết quả
print("Các gợi ý hàng đầu:")
recommendations.show(truncate=False)

# Kết quả sẽ có dạng:
# +----+-----------------------------------------------------+
# |user|recommendations                                      |
# +----+-----------------------------------------------------+
# |10  |[{item: 123, rating: 0.5}, {item: 456, rating: 0.45}, ...]|
# |25  |[{item: 789, rating: 0.6}, {item: 101, rating: 0.55}, ...]|
# +----+-----------------------------------------------------+

spark.stop()