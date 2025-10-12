#!/usr/bin/env python3
"""
Demo Spark Job - Simple Word Count
File này để test Spark Runner GUI
"""

from pyspark.sql import SparkSession

def main():
    # Tạo Spark session
    spark = SparkSession.builder \
        .appName("Demo Word Count") \
        .getOrCreate()
    
    print("=" * 60)
    print("🚀 DEMO SPARK JOB - WORD COUNT")
    print("=" * 60)
    
    # Tạo sample data
    data = [
        "Hello Spark",
        "Hello World",
        "Spark is awesome",
        "Python and Spark",
        "Big Data processing with Spark"
    ]
    
    # Tạo RDD
    rdd = spark.sparkContext.parallelize(data)
    
    # Word count
    word_counts = rdd \
        .flatMap(lambda line: line.split()) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda a, b: a + b) \
        .sortBy(lambda x: x[1], ascending=False)
    
    # Hiển thị kết quả
    print("\n📊 Word Count Results:")
    print("-" * 40)
    for word, count in word_counts.collect():
        print(f"{word:20s} : {count}")
    
    print("\n" + "=" * 60)
    print("✅ Job completed successfully!")
    print("=" * 60)
    
    spark.stop()

if __name__ == "__main__":
    main()
