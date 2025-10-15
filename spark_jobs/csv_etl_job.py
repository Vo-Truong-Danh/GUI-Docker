"""
Spark ETL Job - Large CSV Processing
Optimized for Reddit comments or similar large datasets

Features:
- Read large CSV from HDFS
- Extract required fields
- Clean data (filter deleted comments)
- Write to Parquet for efficient storage
- Partitioning for faster queries
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, when, lit, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType
import sys
from datetime import datetime


def create_spark_session(app_name="CSV_ETL_Job"):
    """Create optimized Spark session for large CSV processing"""
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.files.maxPartitionBytes", "128MB") \
        .config("spark.sql.shuffle.partitions", "200") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "1g") \
        .config("spark.memory.fraction", "0.8") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


def define_csv_schema():
    """
    Define schema for Reddit comments CSV
    Adjust based on your actual CSV structure
    """
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("created_utc", LongType(), True),
        StructField("author", StringType(), True),
        StructField("body", StringType(), True),
        StructField("score", IntegerType(), True),
        StructField("subreddit", StringType(), True),
        StructField("link_flair_text", StringType(), True),
        StructField("parent_id", StringType(), True),
        StructField("link_id", StringType(), True),
    ])
    return schema


def read_large_csv(spark, input_path, schema=None):
    """
    Read large CSV with optimizations
    
    Args:
        spark: SparkSession
        input_path: HDFS path to CSV file(s)
        schema: Optional predefined schema
    
    Returns:
        DataFrame
    """
    print(f"📖 Reading CSV from: {input_path}")
    start_time = datetime.now()
    
    # Read with optimizations
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false" if schema else "true") \
        .option("multiLine", "true") \
        .option("escape", '"') \
        .option("mode", "DROPMALFORMED") \
        .schema(schema) \
        .csv(input_path)
    
    # Trigger count to measure read time
    record_count = df.count()
    read_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ Read {record_count:,} records in {read_time:.2f}s")
    print(f"📊 Partitions: {df.rdd.getNumPartitions()}")
    
    return df


def extract_required_fields(df):
    """
    Extract and transform required fields
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with selected and transformed columns
    """
    print("\n🔍 Extracting required fields...")
    
    # Select and transform columns
    extracted_df = df.select(
        col("created_utc"),
        col("body"),
        col("score"),
        col("subreddit"),
        col("link_flair_text"),
        col("author"),
        col("id")
    ).withColumn(
        # Convert Unix timestamp to readable datetime
        "created_datetime",
        to_timestamp(col("created_utc"))
    ).withColumn(
        # Clean subreddit names (lowercase, trim)
        "subreddit_clean",
        trim(lower(col("subreddit")))
    )
    
    print(f"✅ Extracted {len(extracted_df.columns)} columns")
    return extracted_df


def clean_data(df):
    """
    Clean data by filtering and validating
    
    Removes:
    - Deleted comments ([deleted])
    - Removed comments ([removed])
    - Null bodies
    - Empty bodies
    
    Args:
        df: Input DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    print("\n🧹 Cleaning data...")
    
    initial_count = df.count()
    print(f"   Initial records: {initial_count:,}")
    
    # Filter out deleted/removed/empty comments
    cleaned_df = df.filter(
        (col("body").isNotNull()) &
        (col("body") != "") &
        (col("body") != "[deleted]") &
        (col("body") != "[removed]") &
        (trim(col("body")) != "")
    )
    
    # Filter out deleted authors
    cleaned_df = cleaned_df.filter(
        (col("author").isNotNull()) &
        (col("author") != "[deleted]")
    )
    
    # Filter out invalid scores (if score is null, default to 0)
    cleaned_df = cleaned_df.withColumn(
        "score",
        when(col("score").isNull(), lit(0)).otherwise(col("score"))
    )
    
    final_count = cleaned_df.count()
    removed = initial_count - final_count
    removed_pct = (removed / initial_count * 100) if initial_count > 0 else 0
    
    print(f"   Final records: {final_count:,}")
    print(f"   Removed: {removed:,} ({removed_pct:.2f}%)")
    print(f"   ✅ Data cleaned")
    
    return cleaned_df


def add_partitioning_columns(df):
    """
    Add year/month columns for partitioning
    
    Args:
        df: Input DataFrame
    
    Returns:
        DataFrame with partition columns
    """
    print("\n📅 Adding partitioning columns...")
    
    from pyspark.sql.functions import year, month
    
    partitioned_df = df.withColumn(
        "year",
        year(col("created_datetime"))
    ).withColumn(
        "month",
        month(col("created_datetime"))
    )
    
    print(f"   ✅ Added year/month columns for partitioning")
    return partitioned_df


def write_to_parquet(df, output_path, partition_by=None):
    """
    Write DataFrame to Parquet format
    
    Args:
        df: Input DataFrame
        output_path: HDFS output path
        partition_by: List of columns to partition by (e.g., ['year', 'month'])
    """
    print(f"\n💾 Writing to Parquet: {output_path}")
    start_time = datetime.now()
    
    writer = df.write \
        .mode("overwrite") \
        .option("compression", "snappy")
    
    if partition_by:
        print(f"   📂 Partitioning by: {', '.join(partition_by)}")
        writer = writer.partitionBy(*partition_by)
    
    writer.parquet(output_path)
    
    write_time = (datetime.now() - start_time).total_seconds()
    print(f"✅ Written in {write_time:.2f}s")


def generate_summary_stats(df):
    """
    Generate summary statistics
    
    Args:
        df: Input DataFrame
    
    Returns:
        None (prints stats)
    """
    print("\n📊 Summary Statistics:")
    print("=" * 60)
    
    # Top subreddits
    print("\n🏆 Top 10 Subreddits:")
    top_subreddits = df.groupBy("subreddit_clean") \
        .count() \
        .orderBy(col("count").desc()) \
        .limit(10)
    top_subreddits.show(truncate=False)
    
    # Score statistics
    print("\n⭐ Score Statistics:")
    df.select("score").describe().show()
    
    # Records by year
    print("\n📅 Records by Year:")
    df.groupBy("year") \
        .count() \
        .orderBy("year") \
        .show()


def main(input_path, output_path):
    """
    Main ETL pipeline
    
    Args:
        input_path: HDFS path to input CSV
        output_path: HDFS path for output Parquet
    """
    print("=" * 60)
    print("🚀 Starting Spark ETL Job - Large CSV Processing")
    print("=" * 60)
    print(f"📥 Input: {input_path}")
    print(f"📤 Output: {output_path}")
    print()
    
    # Step 1: Create Spark session
    spark = create_spark_session()
    
    try:
        # Step 2: Read CSV with schema
        schema = define_csv_schema()
        df = read_large_csv(spark, input_path, schema)
        
        # Step 3: Extract required fields
        df_extracted = extract_required_fields(df)
        
        # Step 4: Clean data
        df_cleaned = clean_data(df_extracted)
        
        # Step 5: Add partitioning columns
        df_partitioned = add_partitioning_columns(df_cleaned)
        
        # Step 6: Cache for reuse (stats + write)
        df_partitioned.cache()
        
        # Step 7: Generate summary statistics
        generate_summary_stats(df_partitioned)
        
        # Step 8: Write to Parquet
        write_to_parquet(
            df_partitioned, 
            output_path,
            partition_by=['year', 'month']
        )
        
        # Step 9: Verify output
        print("\n🔍 Verifying output...")
        output_df = spark.read.parquet(output_path)
        output_count = output_df.count()
        print(f"✅ Verified: {output_count:,} records in output")
        
        print("\n" + "=" * 60)
        print("✅ ETL Job Completed Successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ETL Job Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        spark.stop()


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: spark-submit csv_etl_job.py <input_hdfs_path> <output_hdfs_path>")
        print()
        print("Example:")
        print("  spark-submit csv_etl_job.py \\")
        print("    hdfs:///user/data/reddit_comments.csv \\")
        print("    hdfs:///user/data/reddit_comments_cleaned")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(input_path, output_path)
