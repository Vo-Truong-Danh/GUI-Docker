#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("CountSnapeOccurrences") \
    .master("local[*]") \
    .getOrCreate()

# Read file from HDFS
hdfs_path = "hdfs://namenode:8020/input/harrypotter.txt"

# Method 1: Using DataFrame + explode
df = spark.read.text(hdfs_path)

# Split each line into words, explode to rows, filter 'snape'
word_counts = df \
    .select(F.explode(F.split(F.lower(F.col("value")), r"\W+")).alias("word")) \
    .filter(F.col("word") == "snape") \
    .count()

print(f"Count of 'snape' using DataFrame: {word_counts}")

# Method 2: Using RDD (classic Spark)
text_rdd = spark.sparkContext.textFile(hdfs_path)

snape_count = text_rdd \
    .flatMap(lambda line: line.lower().split()) \
    .filter(lambda word: word == "snape") \
    .count()

print(f"Count of 'snape' using RDD: {snape_count}")

# Stop Spark
spark.stop()
