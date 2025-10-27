#!/usr/bin/env python3
"""
Test script để kiểm tra các packages đã cài trong Spark Worker
Chạy file này qua GUI hoặc spark-submit
"""

from pyspark.sql import SparkSession
import pandas as pd
import numpy as np
import yaml
import requests

def main():
    print("=" * 60)
    print("🧪 KIỂM TRA CÁC PACKAGES TRONG SPARK WORKER")
    print("=" * 60)
    
    # 1. Test pandas
    print("\n✅ Testing pandas...")
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000, 60000, 70000]
    })
    print(f"   pandas version: {pd.__version__}")
    print(f"   Created DataFrame with {len(df)} rows")
    print(df.to_string(index=False))
    
    # 2. Test numpy
    print("\n✅ Testing numpy...")
    arr = np.array([1, 2, 3, 4, 5])
    print(f"   numpy version: {np.__version__}")
    print(f"   Array sum: {arr.sum()}")
    print(f"   Array mean: {arr.mean()}")
    
    # 3. Test PyYAML
    print("\n✅ Testing PyYAML...")
    config = {'database': 'postgres', 'port': 5432}
    yaml_str = yaml.dump(config)
    print(f"   YAML output:\n{yaml_str}")
    
    # 4. Test requests
    print("\n✅ Testing requests...")
    print(f"   requests version: {requests.__version__}")
    print("   (Có thể gọi APIs từ Spark jobs)")
    
    # 5. Test PySpark
    print("\n✅ Testing PySpark integration...")
    spark = SparkSession.builder \
        .appName("PackageTest") \
        .getOrCreate()
    
    # Convert pandas DataFrame to Spark DataFrame
    spark_df = spark.createDataFrame(df)
    print(f"   Created Spark DataFrame:")
    spark_df.show()
    
    # Do some Spark operations
    avg_salary = spark_df.selectExpr("avg(salary) as avg_salary").collect()[0][0]
    print(f"   Average salary (calculated by Spark): ${avg_salary:,.2f}")
    
    spark.stop()
    
    print("\n" + "=" * 60)
    print("✅ TẤT CẢ PACKAGES HOẠT ĐỘNG HOÀN HẢO!")
    print("=" * 60)

if __name__ == "__main__":
    main()

