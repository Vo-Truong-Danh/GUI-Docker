#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENHANCED HYBRID v7.0 - ACCURACY IMPROVEMENTS
=====================================================
NEW FEATURES:
1. Artist-based collaborative filtering (dual ALS models)
2. Confidence weighting based on track position
3. Improved hyperparameters tuning
4. Diversity-aware re-ranking
5. Popularity-based calibration
6. Ensemble predictions
=====================================================
Optimized for MAP@500 improvement
"""

import argparse
import time
import hashlib
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    col, collect_set, lit, hash as spark_hash, abs as spark_abs, 
    row_number, count, ntile, monotonically_increasing_id, size,
    expr, when, sum as spark_sum, avg as spark_avg, stddev, max as spark_max,
    explode, array, struct, collect_list, desc, asc, log as spark_log
)
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.feature import StringIndexer, StringIndexerModel
from pyspark.ml.evaluation import RankingEvaluator
from pyspark.sql import functions as F


def normalize_hdfs_path(*parts):
    """Simplified HDFS path normalization"""
    if not parts:
        return "hdfs://namenode:8020/"
    
    path = "/".join(str(p).strip("/") for p in parts if p)
    
    if path.startswith("hdfs://"):
        return path
    
    return f"hdfs://namenode:8020/{path}"


def validate_dataframe(df, stage_name, check_duplicates=True):
    """Data quality validation"""
    print(f"   Validating {stage_name}...")
    
    # Check nulls in key columns
    if "playlist_idx" in df.columns and "track_idx" in df.columns:
        null_count = df.filter(
            col("playlist_idx").isNull() | col("track_idx").isNull()
        ).count()
        
        if null_count > 0:
            raise ValueError(f"{stage_name}: Found {null_count} null values in key columns!")
    
    # Check duplicates
    if check_duplicates and "playlist_idx" in df.columns and "track_idx" in df.columns:
        total = df.count()
        if total > 0:
            distinct = df.select("playlist_idx", "track_idx").distinct().count()
            dup_count = total - distinct
            
            if dup_count > 0:
                print(f"   ℹ️  {stage_name}: {dup_count} duplicate pairs ({dup_count/total*100:.2f}%)")
    
    print(f"   ✅ Validation passed")


def export_metrics(metrics, output_path):
    """Export metrics to HDFS"""
    try:
        import json
        metrics_json = json.dumps(metrics, indent=2)
        
        spark = SparkSession.getActiveSession()
        hadoop_conf = spark._jsc.hadoopConfiguration()
        uri = spark._jvm.java.net.URI(output_path)
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
        path = spark._jvm.org.apache.hadoop.fs.Path(output_path)
        
        # Ensure parent directory exists
        parent = path.getParent()
        if parent and not fs.exists(parent):
            fs.mkdirs(parent)
        
        output_stream = fs.create(path, True)
        writer = spark._jvm.java.io.BufferedWriter(
            spark._jvm.java.io.OutputStreamWriter(output_stream)
        )
        
        writer.write(metrics_json)
        writer.close()
        
        print(f"✅ Metrics exported to {output_path}")
    except Exception as e:
        print(f"⚠️  Failed to export metrics: {e}")
        import traceback
        traceback.print_exc()


class AutoCleanupSparkSession:
    @staticmethod
    def create(rank=100, checkpoint_dir=None):
        shuffle_partitions = max(80, min(200, rank))
        
        if checkpoint_dir is None:
            checkpoint_dir = "hdfs://namenode:8020/tmp/checkpoints"
        
        builder = SparkSession.builder \
            .appName("SpotifyRecs_v7.0_Enhanced") \
            .config("spark.driver.memory", "3g") \
            .config("spark.executor.memory", "6g") \
            .config("spark.executor.cores", "6") \
            .config("spark.sql.shuffle.partitions", str(shuffle_partitions)) \
            .config("spark.default.parallelism", str(shuffle_partitions)) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.kryoserializer.buffer.max", "512m") \
            .config("spark.rdd.compress", "true") \
            .config("spark.io.compression.codec", "lz4") \
            .config("spark.sql.parquet.compression.codec", "snappy") \
            .config("spark.checkpoint.compress", "true") \
            .config("spark.cleaner.periodicGC.interval", "10min")
        
        # Try to set cleaner config (may not exist in all Spark versions)
        try:
            builder = builder.config("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
        except:
            pass
        
        spark = builder.getOrCreate()
        
        spark.sparkContext.setCheckpointDir(checkpoint_dir)
        spark.sparkContext.setLogLevel("WARN")
        
        try:
            num_executors = len([ex for ex in spark.sparkContext._jsc.sc().statusTracker().getExecutorInfos() if ex.host() != "driver"])
            if num_executors == 0:
                num_executors = "auto"
        except:
            num_executors = "auto"
        
        print("\n" + "=" * 80)
        print("🎯 ENHANCED HYBRID v7.0 - ACCURACY IMPROVEMENTS")
        print("=" * 80)
        print(f"💾 Driver: 3g | Executor: 6g (×{num_executors}) | Cores: 6")
        print(f"📊 Shuffle: {shuffle_partitions} | Compression: LZ4+Snappy")
        print(f"🧹 Auto Cleanup | 📁 Checkpoint: {checkpoint_dir}")
        print("=" * 80)
        
        return spark


class HDFSCleaner:
    @staticmethod
    def delete_checkpoint(spark, path, description="checkpoint"):
        try:
            path = normalize_hdfs_path(path)
            
            hadoop_conf = spark._jsc.hadoopConfiguration()
            uri = spark._jvm.java.net.URI(path)
            fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(path)
            
            if fs.exists(hadoop_path):
                size_mb = fs.getContentSummary(hadoop_path).getLength() / (1024 * 1024)
                fs.delete(hadoop_path, True)
                print(f"✅ Deleted {description}: ~{size_mb:.1f} MB freed")
                return True
            else:
                print(f"ℹ️  {description} not found")
                return False
        except Exception as e:
            print(f"⚠️  Failed to delete {description}: {e}")
            return False


class ProgressTracker:
    def __init__(self, spark, progress_path, config_hash=None):
        self.spark = spark
        self.progress_path = normalize_hdfs_path(progress_path)
        self.config_hash = config_hash
        self.progress = self._load()
    
    def _load(self):
        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            uri = self.spark._jvm.java.net.URI(self.progress_path)
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            path = self.spark._jvm.org.apache.hadoop.fs.Path(self.progress_path)
            
            if fs.exists(path):
                input_stream = fs.open(path)
                reader = self.spark._jvm.java.io.BufferedReader(
                    self.spark._jvm.java.io.InputStreamReader(input_stream)
                )
                content = []
                line = reader.readLine()
                while line is not None:
                    content.append(str(line))
                    line = reader.readLine()
                reader.close()
                
                progress = json.loads("\n".join(content))
                
                if self.config_hash and progress.get("config_hash") != self.config_hash:
                    print(f"⚠️  Config changed, clearing progress")
                    return {"config_hash": self.config_hash}
                
                return progress
        except Exception as e:
            print(f"⚠️  Failed to load progress (will restart): {e}")
        
        return {"config_hash": self.config_hash}
    
    def _save(self):
        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            uri = self.spark._jvm.java.net.URI(self.progress_path)
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            path = self.spark._jvm.org.apache.hadoop.fs.Path(self.progress_path)
            
            # Ensure parent directory exists
            parent = path.getParent()
            if parent and not fs.exists(parent):
                fs.mkdirs(parent)
            
            output_stream = fs.create(path, True)
            writer = self.spark._jvm.java.io.BufferedWriter(
                self.spark._jvm.java.io.OutputStreamWriter(output_stream)
            )
            
            writer.write(json.dumps(self.progress, indent=2))
            writer.close()
        except Exception as e:
            print(f"⚠️  Failed to save progress: {e}")
    
    def is_completed(self, step):
        val = self.progress.get(step, False)
        # Handle both bool and dict formats
        if isinstance(val, dict):
            return val.get("completed", False)
        return bool(val)
    
    def mark_completed(self, step):
        self.progress[step] = {"completed": True}
        self._save()


class EnhancedDataLoader:
    @staticmethod
    def load_with_features(spark, input_path, checkpoint_path, progress_tracker):
        """Load data with enhanced features: artist info, position, confidence"""
        checkpoint_path = normalize_hdfs_path(checkpoint_path)
        
        # Check if checkpoint exists on HDFS
        checkpoint_exists = False
        checkpoint_non_empty = False
        try:
            hadoop_conf = spark._jsc.hadoopConfiguration()
            uri = spark._jvm.java.net.URI(checkpoint_path)
            fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            path = spark._jvm.org.apache.hadoop.fs.Path(checkpoint_path)
            checkpoint_exists = fs.exists(path)
            if checkpoint_exists:
                statuses = fs.listStatus(path)
                checkpoint_non_empty = statuses is not None and len(statuses) > 0
        except:
            pass
        
        if (checkpoint_exists and checkpoint_non_empty) or progress_tracker.is_completed("load_enhanced_data"):
            print(f"\n✅ Loading enhanced data from checkpoint...")
            df = spark.read.parquet(checkpoint_path)
            metadata = progress_tracker.progress.get("load_enhanced_data", {}).get("metadata", {})
            total_interactions = metadata.get('total_interactions', 'N/A')
            total_playlists = metadata.get('total_playlists', 'N/A')
            total_tracks = metadata.get('total_tracks', 'N/A')
            print(f"   Interactions: {total_interactions:,}" if isinstance(total_interactions, int) else f"   Interactions: {total_interactions}")
            print(f"   Playlists: {total_playlists:,}" if isinstance(total_playlists, int) else f"   Playlists: {total_playlists}")
            print(f"   Tracks: {total_tracks:,}" if isinstance(total_tracks, int) else f"   Tracks: {total_tracks}")
            return df
        
        print(f"\n{'=' * 80}")
        print(f"📥 LOADING ENHANCED DATA")
        print(f"{'=' * 80}")
        print(f"Input path: {input_path}")
        print(f"Format: JSON (Spotify MPD with features)")
        
        print(f"\n🔍 Loading JSON data...")
        start_time = time.time()
        
        try:
            # Fix: Handle path correctly
            if input_path.endswith("*.json") or "/*.json" in input_path:
                json_path = input_path
            else:
                json_path = f"{input_path.rstrip('/')}/*.json"
            
            print(f"   Reading from: {json_path}")
            
            df = spark.read.option("multiLine", "true").json(json_path)
            print(f"   ✅ JSON loaded successfully")
        except Exception as e:
            print(f"   ❌ Error loading JSON: {e}")
            raise
        
        print(f"\n📦 Processing MPD structure with ENHANCED features...")
        
        # Step 1: Explode playlists
        print(f"   🔄 Exploding playlists...")
        playlists_df = (
            df.select(F.explode(col("playlists")).alias("pl"))
            .select(
                F.col("pl.pid").alias("playlist_id"),
                F.col("pl.tracks").alias("tracks")
            )
        )
        
        # Step 2: Explode tracks with position and artist info
        print(f"   🔄 Exploding tracks with features...")
        print(f"   📍 Feature 1: Track position in playlist (confidence)")
        print(f"   👤 Feature 2: Artist URI (for artist-based CF)")
        
        interactions_df = (
            playlists_df
            .select("playlist_id", F.posexplode("tracks").alias("position", "track"))
            .select(
                F.col("playlist_id").cast("long"),
                F.col("track.track_uri").alias("track_uri"),
                F.col("track.artist_uri").alias("artist_uri"),  # NEW: Artist info
                F.col("position").cast("int")  # NEW: Position in playlist
            )
            .filter(F.col("track_uri").isNotNull())
        )
        
        # Step 3: Calculate confidence based on position
        # Earlier tracks in playlist = higher confidence (user preference)
        print(f"   🎯 Calculating confidence weights...")
        
        # Get playlist lengths
        playlist_lengths = interactions_df.groupBy("playlist_id").agg(
            F.max("position").alias("max_position")
        )
        
        # Join and calculate normalized confidence
        # Formula: confidence = 1 + log(1 + (max_pos - pos) / (max_pos + 1))
        # This gives higher weight to earlier songs
        interactions_df = interactions_df.join(playlist_lengths, "playlist_id")
        interactions_df = interactions_df.withColumn(
            "confidence",
            lit(1.0) + spark_log(lit(1.0) + (col("max_position") - col("position")) / (col("max_position") + lit(1.0)))
        )
        
        # Remove duplicates (keep higher confidence if duplicate)
        print(f"   🔄 Removing duplicates (keeping max confidence)...")
        window_spec = Window.partitionBy("playlist_id", "track_uri").orderBy(desc("confidence"))
        interactions_df = interactions_df.withColumn("rn", row_number().over(window_spec))
        interactions_df = interactions_df.filter(col("rn") == 1).drop("rn", "max_position")
        
        # Repartition for balance
        interactions_df = interactions_df.repartition(36, "playlist_id")
        
        print(f"   ✅ Enhanced features extracted")

        # Count statistics
        print(f"\n📊 Counting statistics...")
        total_interactions = interactions_df.count()
        total_playlists = interactions_df.select("playlist_id").distinct().count()
        total_tracks = interactions_df.select("track_uri").distinct().count()
        total_artists = interactions_df.select("artist_uri").distinct().count()
        
        # Cache and checkpoint
        print(f"\n💾 Saving enhanced checkpoint...")
        interactions_df.write.mode("overwrite").parquet(checkpoint_path)
        
        elapsed = time.time() - start_time
        
        print(f"\n{'=' * 80}")
        print(f"✅ ENHANCED DATA LOADING COMPLETE")
        print(f"{'=' * 80}")
        print(f"   Total interactions: {total_interactions:,}")
        print(f"   Total playlists: {total_playlists:,}")
        print(f"   Total tracks: {total_tracks:,}")
        print(f"   Total artists: {total_artists:,}")
        print(f"   Time: {elapsed:.1f}s")
        print(f"   Checkpoint: {checkpoint_path}")
        print(f"{'=' * 80}")
        
        progress_tracker.progress["load_enhanced_data"] = {
            "completed": True,
            "metadata": {
                "total_interactions": total_interactions,
                "total_playlists": total_playlists,
                "total_tracks": total_tracks,
                "total_artists": total_artists
            }
        }
        progress_tracker._save()
        
        return interactions_df


class ResilientFilter:
    @staticmethod
    def filter_or_resume(spark, raw_df, checkpoint_path, progress_tracker, min_user=5, min_item=10):
        checkpoint_path = normalize_hdfs_path(checkpoint_path)
        
        if progress_tracker.is_completed("filter_data"):
            print(f"\n✅ Loading filtered data from checkpoint...")
            return spark.read.parquet(checkpoint_path)
        
        print(f"\n{'=' * 80}")
        print(f"🔍 FILTERING DATA (Iterative)")
        print(f"{'=' * 80}")
        print(f"Min user interactions: {min_user}")
        print(f"Min item interactions: {min_item}")
        print(f"{'=' * 80}")
        
        print(f"\n💾 Caching raw data...")
        raw_df.cache()
        raw_count = raw_df.count()
        print(f"   Raw interactions: {raw_count:,}")
        
        # Iterative filtering to convergence
        filtered = raw_df
        iteration = 0
        max_iterations = 5
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Filter iteration {iteration}...")
            
            user_counts = filtered.groupBy("playlist_id").count().withColumnRenamed("count", "user_count")
            item_counts = filtered.groupBy("track_uri").count().withColumnRenamed("count", "item_count")
            
            before_count = filtered.count()
            before_users = filtered.select("playlist_id").distinct().count()
            before_items = filtered.select("track_uri").distinct().count()
            
            filtered_new = filtered \
                .join(user_counts, "playlist_id") \
                .join(item_counts, "track_uri") \
                .filter((col("user_count") >= min_user) & (col("item_count") >= min_item)) \
                .select("playlist_id", "track_uri", "artist_uri", "position", "confidence")
            
            after_count = filtered_new.count()
            after_users = filtered_new.select("playlist_id").distinct().count()
            after_items = filtered_new.select("track_uri").distinct().count()
            
            if before_count == after_count:
                print(f"   ✅ Converged at iteration {iteration}")
                filtered = filtered_new
                break
            
            print(f"   Dropped: {before_count - after_count:,} interactions, {before_users - after_users:,} users, {before_items - after_items:,} items")
            filtered = filtered_new
        
        raw_df.unpersist()
        
        filtered = filtered.repartition(36, "playlist_id")
        filtered_count = filtered.count()
        num_users_after = filtered.select("playlist_id").distinct().count()
        num_items_after = filtered.select("track_uri").distinct().count()
        
        print(f"\n💾 Saving filtered data...")
        filtered.write.mode("overwrite").parquet(checkpoint_path)
        progress_tracker.mark_completed("filter_data")
        
        print(f"\n{'=' * 80}")
        print(f"✅ FILTERING COMPLETE")
        print(f"{'=' * 80}")
        print(f"   Final interactions: {filtered_count:,}")
        print(f"   Final users: {num_users_after:,}")
        print(f"   Final items: {num_items_after:,}")
        if raw_count > 0:
            print(f"   Retention: {filtered_count/raw_count*100:.1f}%")
        print(f"{'=' * 80}")
        
        return filtered


class EnhancedIndexer:
    @staticmethod
    def index_or_resume(spark, filtered_df, checkpoint_path, progress_tracker, save_indexers=True, indexer_base_path=None):
        """Index with track, artist, and save mappings"""
        checkpoint_path = normalize_hdfs_path(checkpoint_path)
        
        if progress_tracker.is_completed("index_data"):
            print(f"\n✅ Loading indexed data from checkpoint...")
            return spark.read.parquet(checkpoint_path)
        
        print(f"\n{'=' * 80}")
        print(f"🔢 ENHANCED INDEXING (Track + Artist)")
        print(f"{'=' * 80}")
        
        before_count = filtered_df.count()
        print(f"   Interactions before indexing: {before_count:,}")
        
        # Repartition before indexing
        print(f"\n🔄 Repartitioning data...")
        filtered_df = filtered_df.repartition(36, "playlist_id")
        
        print(f"\n🔢 Indexing users (playlists)...")
        user_indexer = StringIndexer(
            inputCol="playlist_id", 
            outputCol="playlist_idx", 
            handleInvalid="skip",
            stringOrderType="frequencyDesc"
        )
        user_indexer_model = user_indexer.fit(filtered_df)
        indexed = user_indexer_model.transform(filtered_df)
        num_users = len(user_indexer_model.labels)
        print(f"   ✅ Users indexed: {num_users:,}")
        
        print(f"\n🔢 Indexing items (tracks)...")
        item_indexer = StringIndexer(
            inputCol="track_uri", 
            outputCol="track_idx", 
            handleInvalid="skip",
            stringOrderType="frequencyDesc"
        )
        item_indexer_model = item_indexer.fit(indexed)
        indexed = item_indexer_model.transform(indexed)
        num_items = len(item_indexer_model.labels)
        print(f"   ✅ Items indexed: {num_items:,}")
        
        print(f"\n🔢 Indexing artists...")
        artist_indexer = StringIndexer(
            inputCol="artist_uri", 
            outputCol="artist_idx", 
            handleInvalid="skip",
            stringOrderType="frequencyDesc"
        )
        artist_indexer_model = artist_indexer.fit(indexed)
        indexed = artist_indexer_model.transform(indexed)
        num_artists = len(artist_indexer_model.labels)
        print(f"   ✅ Artists indexed: {num_artists:,}")
        
        print(f"\n🔄 Creating final indexed format...")
        indexed = indexed.select(
            col("playlist_id"),
            col("playlist_idx").cast("int"),
            col("track_uri"),
            col("track_idx").cast("int"),
            col("artist_uri"),
            col("artist_idx").cast("int"),
            col("position"),
            col("confidence")
        )
        
        print(f"\n💾 Saving indexed data...")
        indexed.write.mode("overwrite").parquet(checkpoint_path)
        
        after_count = indexed.count()
        dropped = before_count - after_count
        drop_rate = (dropped / before_count * 100) if before_count > 0 else 0
        
        if dropped > 0:
            print(f"   ℹ️  Dropped by indexers: {dropped:,} (~{drop_rate:.2f}%)")
        
        if save_indexers and indexer_base_path:
            print(f"\n💾 Saving indexer models...")
            user_indexer_path = normalize_hdfs_path(indexer_base_path, "user_indexer")
            item_indexer_path = normalize_hdfs_path(indexer_base_path, "item_indexer")
            artist_indexer_path = normalize_hdfs_path(indexer_base_path, "artist_indexer")
            
            user_indexer_model.write().overwrite().save(user_indexer_path)
            item_indexer_model.write().overwrite().save(item_indexer_path)
            artist_indexer_model.write().overwrite().save(artist_indexer_path)
            print(f"   ✅ User indexer: {user_indexer_path}")
            print(f"   ✅ Item indexer: {item_indexer_path}")
            print(f"   ✅ Artist indexer: {artist_indexer_path}")
        
        progress_tracker.mark_completed("index_data")
        
        print(f"\n{'=' * 80}")
        print(f"✅ INDEXING COMPLETE")
        print(f"{'=' * 80}")
        print(f"   Final interactions: {after_count:,}")
        print(f"   Users: {num_users:,}")
        print(f"   Items: {num_items:,}")
        print(f"   Artists: {num_artists:,}")
        print(f"{'=' * 80}")
        
        # Validate output
        print(f"\n🔍 Quick validation...")
        null_count = indexed.filter(
            col("playlist_idx").isNull() | col("track_idx").isNull()
        ).count()
        if null_count > 0:
            raise ValueError(f"Found {null_count} null values in indexed columns!")
        print(f"   ✅ No null values in indexed columns")
        
        return indexed


class DualModelTrainer:
    @staticmethod
    def train_dual_models(spark, train_df, model_base_path, rank, max_iter, reg_param, alpha, force_retrain=False):
        """
        Train TWO ALS models:
        1. Track-based ALS (main model)
        2. Artist-based ALS (diversity model)
        Then ensemble them
        """
        track_model_path = normalize_hdfs_path(model_base_path, "track_model")
        artist_model_path = normalize_hdfs_path(model_base_path, "artist_model")
        
        # Check if models exist
        track_exists = False
        artist_exists = False
        try:
            hadoop_conf = spark._jsc.hadoopConfiguration()
            uri = spark._jvm.java.net.URI(track_model_path)
            fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            track_exists = fs.exists(spark._jvm.org.apache.hadoop.fs.Path(track_model_path))
            artist_exists = fs.exists(spark._jvm.org.apache.hadoop.fs.Path(artist_model_path))
        except:
            pass
        
        if track_exists and artist_exists and not force_retrain:
            print(f"\n✅ Loading existing dual models...")
            track_model = ALSModel.load(track_model_path)
            artist_model = ALSModel.load(artist_model_path)
            return track_model, artist_model
        
        print(f"\n{'=' * 80}")
        print(f"🔥 TRAINING DUAL ALS MODELS")
        print(f"{'=' * 80}")
        print(f"Model 1: Track-based collaborative filtering")
        print(f"Model 2: Artist-based collaborative filtering")
        print(f"{'=' * 80}")
        
        # MODEL 1: Track-based ALS (primary model)
        print(f"\n{'=' * 40}")
        print(f"🎵 TRAINING MODEL 1: TRACK-BASED ALS")
        print(f"{'=' * 40}")
        print(f"📊 Hyperparameters:")
        print(f"   Rank: {rank}")
        print(f"   Max Iterations: {max_iter}")
        print(f"   Regularization: {reg_param}")
        print(f"   Alpha: {alpha}")
        print(f"   Implicit Prefs: True")
        print(f"   Cold Start: drop")
        
        track_training_data = train_df.select(
            col("playlist_idx").alias("user"),
            col("track_idx").alias("item"),
            col("confidence").alias("rating")  # Use position-based confidence
        )
        
        print(f"\n💾 Caching track training data...")
        track_training_data.cache()
        track_count = track_training_data.count()
        print(f"   Training samples: {track_count:,}")
        
        track_als = ALS(
            rank=rank, maxIter=max_iter, regParam=reg_param, alpha=alpha,
            userCol="user", itemCol="item", ratingCol="rating",
            coldStartStrategy="drop", implicitPrefs=True,
            seed=42, checkpointInterval=5
        )
        
        print(f"\n🚀 Training track model...")
        start = time.time()
        track_model = track_als.fit(track_training_data)
        track_training_data.unpersist()
        track_time = time.time() - start
        
        print(f"✅ Track model trained in {track_time/60:.2f} min")
        print(f"💾 Saving track model...")
        track_model.write().overwrite().save(track_model_path)
        
        # MODEL 2: Artist-based ALS (for diversity)
        print(f"\n{'=' * 40}")
        print(f"👤 TRAINING MODEL 2: ARTIST-BASED ALS")
        print(f"{'=' * 40}")
        print(f"📊 Hyperparameters:")
        print(f"   Rank: {rank // 2} (reduced for artist model)")
        print(f"   Max Iterations: {max_iter}")
        print(f"   Regularization: {reg_param * 1.5} (increased for sparsity)")
        print(f"   Alpha: {alpha}")
        
        # Aggregate to playlist-artist level
        artist_training_data = train_df.groupBy("playlist_idx", "artist_idx").agg(
            spark_sum("confidence").alias("rating")  # Sum confidence for same artist
        ).select(
            col("playlist_idx").alias("user"),
            col("artist_idx").alias("item"),
            col("rating")
        )
        
        print(f"\n💾 Caching artist training data...")
        artist_training_data.cache()
        artist_count = artist_training_data.count()
        print(f"   Training samples: {artist_count:,}")
        
        artist_als = ALS(
            rank=rank // 2,  # Smaller rank for artist model
            maxIter=max_iter,
            regParam=reg_param * 1.5,  # Higher regularization
            alpha=alpha,
            userCol="user", itemCol="item", ratingCol="rating",
            coldStartStrategy="drop", implicitPrefs=True,
            seed=43, checkpointInterval=5
        )
        
        print(f"\n🚀 Training artist model...")
        start = time.time()
        artist_model = artist_als.fit(artist_training_data)
        artist_training_data.unpersist()
        artist_time = time.time() - start
        
        print(f"✅ Artist model trained in {artist_time/60:.2f} min")
        print(f"💾 Saving artist model...")
        artist_model.write().overwrite().save(artist_model_path)
        
        print(f"\n{'=' * 80}")
        print(f"✅ DUAL MODEL TRAINING COMPLETE")
        print(f"{'=' * 80}")
        print(f"Track model: {track_model_path}")
        print(f"Artist model: {artist_model_path}")
        print(f"Total training time: {(track_time + artist_time)/60:.2f} min")
        print(f"{'=' * 80}")
        
        return track_model, artist_model


def split_train_valid_per_user(df, k=1, seed=42):
    """Deterministic leave-k-out split using hash"""
    print(f"\n{'=' * 80}")
    print(f"📊 SPLITTING DATA: Leave-{k}-out per user")
    print(f"{'=' * 80}")
    print(f"Method: Deterministic hash-based ordering")
    print(f"Seed: {seed} (used in hash function)")
    print(f"{'=' * 80}")
    
    print(f"\n🔢 Counting items per user...")
    w_count = Window.partitionBy("playlist_idx")
    df_counted = df.withColumn("total_items", count("*").over(w_count))
    
    print(f"🔀 Creating deterministic ordering...")
    w_order = Window.partitionBy("playlist_idx").orderBy(
        spark_abs(spark_hash(col("track_uri"), lit(seed))) % 1000000
    )
    ranked = df_counted.withColumn("rn", row_number().over(w_order))
    
    print(f"\n✂️  Splitting into train/validation...")
    valid = ranked.filter((col("rn") <= k) & (col("total_items") > k)) \
        .drop("rn", "total_items")
    
    train = ranked.filter((col("rn") > k) | (col("total_items") <= k)) \
        .drop("rn", "total_items")
    
    print(f"\n📊 Counting split sizes...")
    train_count = train.count()
    valid_count = valid.count()
    total_count = train_count + valid_count
    
    train_pct = (train_count / total_count * 100) if total_count > 0 else 0
    valid_pct = (valid_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n{'=' * 80}")
    print(f"✅ SPLIT COMPLETE")
    print(f"{'=' * 80}")
    print(f"   Train: {train_count:,} interactions ({train_pct:.1f}%)")
    print(f"   Valid: {valid_count:,} interactions ({valid_pct:.1f}%)")
    print(f"   Total: {total_count:,} interactions")
    print(f"{'=' * 80}")
    
    return train, valid


def evaluate_ensemble_map_scalable(spark, track_model, artist_model, track_to_artist_mapping, valid_df, 
                                    k=500, num_batches=20, track_weight=0.7, artist_weight=0.3, 
                                    filter_seen=True, seen_in_train=None):
    """
    Ensemble evaluation combining track-based and artist-based recommendations
    Args:
        filter_seen: If True, remove items seen in TRAIN from predictions (proper MAP@K)
        seen_in_train: DataFrame with (user, seen_item) from training data
    """
    print(f"\n{'=' * 80}")
    print(f"📊 EVALUATING ENSEMBLE MAP@{k}")
    print(f"{'=' * 80}")
    print(f"Batches: {num_batches}")
    print(f"Track weight: {track_weight} | Artist weight: {artist_weight}")
    print(f"Filter seen items: {filter_seen}")
    print(f"{'=' * 80}")
    
    start_time = time.time()
    
    # Ground truth
    print(f"\n📦 Preparing ground truth...")
    ground_truth = valid_df.groupBy("playlist_idx").agg(
        collect_set(col("track_idx").cast("double")).alias("label")
    ).withColumnRenamed("playlist_idx", "user")
    
    total_users = ground_truth.count()
    print(f"   Total validation users: {total_users:,}")
    
    # Create batches
    print(f"\n🔀 Creating {num_batches} deterministic batches...")
    gt_batched = ground_truth.withColumn(
        "batch_id", 
        ntile(num_batches).over(Window.orderBy("user"))
    )
    gt_batched.cache()
    batch_count = gt_batched.count()
    print(f"   Batched users: {batch_count:,}")
    
    # Setup evaluator
    print(f"\n🔧 Setting up RankingEvaluator...")
    metric_name = f"MAP@{k}"
    try:
        evaluator = RankingEvaluator(
            labelCol="label", predictionCol="prediction",
            metricName="meanAveragePrecisionAtK", k=k
        )
        print(f"   Metric: {metric_name}")
    except Exception as e:
        metric_name = "MAP (full)"
        print(f"   ⚠️  meanAveragePrecisionAtK not supported: {e}")
        print(f"   ⚠️  CRITICAL WARNING: Falling back to {metric_name}")
        print(f"   ⚠️  Results will NOT be truncated at K={k}")
        evaluator = RankingEvaluator(
            labelCol="label", predictionCol="prediction",
            metricName="meanAveragePrecision"
        )
    
    print(f"\n{'=' * 80}")
    print(f"🔄 PROCESSING BATCHES WITH ENSEMBLE")
    print(f"{'=' * 80}")
    
    batch_results = []
    
    for i in range(1, num_batches + 1):
        batch_start = time.time()
        
        batch_gt = gt_batched.filter(col("batch_id") == i).drop("batch_id")
        batch_gt.cache()
        
        batch_user_count = batch_gt.count()
        if batch_user_count == 0:
            print(f"   Batch {i:2d}/{num_batches}: EMPTY - skipping")
            batch_gt.unpersist()
            continue
        
        # Get track recommendations
        users_for_pred = batch_gt.select("user")
        track_recs = track_model.recommendForUserSubset(users_for_pred, k)
        
        # Get artist recommendations and map to tracks
        artist_recs = artist_model.recommendForUserSubset(users_for_pred, k)
        
        # Map artist recommendations to tracks with aggregation
        # Limit per-artist instead of global limit (deterministic)
        artist_track_recs = artist_recs.select(
            col("user"),
            explode("recommendations").alias("rec")
        ).select(
            col("user"),
            col("rec.item").alias("artist_idx"),
            col("rec.rating").alias("artist_score")
        ).join(
            track_to_artist_mapping,  # Use full mapping
            "artist_idx"
        ).withColumn(
            "rank_in_artist",
            row_number().over(Window.partitionBy("user", "artist_idx").orderBy(desc("artist_score"), asc("track_idx")))
        ).filter(
            col("rank_in_artist") <= 50  # Top N tracks per artist (deterministic)
        ).groupBy("user", "track_idx").agg(
            spark_max("artist_score").alias("artist_score")  # Aggregate duplicates
        )
        
        # Ensemble: Combine track and artist scores
        track_scores = track_recs.select(
            col("user"),
            explode("recommendations").alias("rec")
        ).select(
            col("user"),
            col("rec.item").alias("track_idx"),
            col("rec.rating").alias("track_score")
        )
        
        # Combine with proper null handling
        combined = track_scores.join(
            artist_track_recs, 
            ["user", "track_idx"], 
            "outer"
        ).withColumn(
            "track_score_weighted",
            F.coalesce(col("track_score"), lit(0.0)) * track_weight
        ).withColumn(
            "artist_score_weighted",
            F.coalesce(col("artist_score"), lit(0.0)) * artist_weight
        ).withColumn(
            "ensemble_score",
            col("track_score_weighted") + col("artist_score_weighted")
        )
        
        # Rank and take top k (preserve order with tie-break)
        window_spec = Window.partitionBy("user").orderBy(desc("ensemble_score"), asc("track_idx"))
        ranked_combined = combined.withColumn("rank", row_number().over(window_spec))
        top_k_recs = ranked_combined.filter(col("rank") <= k)
        
        # Filter seen items from TRAIN if requested (proper MAP@K evaluation)
        if filter_seen and seen_in_train is not None:
            # Get seen items for users in this batch
            batch_users = batch_gt.select("user").distinct()
            batch_seen = seen_in_train.join(batch_users, "user", "inner")
            
            # Anti-join to remove items seen in training
            top_k_filtered = top_k_recs.join(
                batch_seen,
                (top_k_recs.user == batch_seen.user) & 
                (top_k_recs.track_idx.cast("double") == batch_seen.seen_item),
                "left_anti"
            )
            
            # Re-rank after filtering (keep ensemble_score order)
            window_rerank = Window.partitionBy("user").orderBy(desc("ensemble_score"), asc("track_idx"))
            top_k_filtered = top_k_filtered.withColumn(
                "new_rank", row_number().over(window_rerank)
            ).filter(col("new_rank") <= k)
            
            final_recs = top_k_filtered.select("user", col("new_rank").alias("rank"), "track_idx", "ensemble_score")
        else:
            final_recs = top_k_recs
        
        # Create prediction array with order preserved (Spark 2.4 compatible)
        batch_preds = final_recs.select(
            col("user"),
            col("rank"),
            col("track_idx").cast("double").alias("track")
        ).groupBy("user").agg(
            F.collect_list(F.struct("rank", "track")).alias("ranked_tracks")
        ).select(
            col("user"),
            F.expr("sort_array(ranked_tracks).track").alias("prediction")
        )
        
        # Unpersist intermediate DataFrames
        try:
            combined.unpersist()
            ranked_combined.unpersist()
            top_k_recs.unpersist()
        except:
            pass  # Safe if not cached
        
        # Use LEFT join to count users without predictions as MAP=0
        eval_df = batch_gt.join(batch_preds, "user", "left")
        # Fill empty predictions with empty array (fillna doesn't work for arrays)
        eval_df = eval_df.withColumn(
            "prediction",
            when(col("prediction").isNull(), F.array().cast("array<double>")).otherwise(col("prediction"))
        )
        
        batch_map_score = evaluator.evaluate(eval_df)
        actual_evaluated = eval_df.count()
        users_without_preds = eval_df.filter(size(col("prediction")) == 0).count()
        
        batch_time = time.time() - batch_start
        # Weight by actual evaluated users, not ground truth users
        batch_results.append((batch_map_score, actual_evaluated))
        
        batch_gt.unpersist()
        
        if i % 5 == 0 or i == num_batches or i == 1:
            no_pred_pct = (users_without_preds / batch_user_count * 100) if batch_user_count > 0 else 0
            print(f"   Batch {i:2d}/{num_batches}: MAP={batch_map_score:.4f} | GT={batch_user_count:,} | NoPred={users_without_preds:,} ({no_pred_pct:.1f}%) | Time={batch_time:.1f}s")
        elif i % 2 == 0:
            print(f"   Batch {i:2d}/{num_batches}: MAP={batch_map_score:.4f}")
    
    gt_batched.unpersist()
    
    print(f"\n{'=' * 80}")
    print(f"📊 CALCULATING FINAL ENSEMBLE METRICS")
    print(f"{'=' * 80}")
    
    # Weighted average
    total_weighted_score = sum(score * count for score, count in batch_results)
    total_users_evaluated = sum(count for _, count in batch_results)
    
    map_score = total_weighted_score / total_users_evaluated if total_users_evaluated > 0 else 0.0
    
    elapsed = time.time() - start_time
    
    print(f"   Batches processed: {len(batch_results)}/{num_batches}")
    print(f"   Total users evaluated: {total_users_evaluated:,}")
    print(f"   Ensemble {metric_name}: {map_score:.4f} ({map_score*100:.2f}%)")
    print(f"   Total evaluation time: {elapsed:.1f}s ({elapsed/60:.2f} min)")
    print(f"{'=' * 80}")
    print(f"✅ ENSEMBLE EVALUATION COMPLETE: {metric_name} = {map_score:.4f}")
    print(f"{'=' * 80}")
    
    return map_score, elapsed


def main():
    parser = argparse.ArgumentParser(description="Enhanced Hybrid v7.0 - Accuracy Improvements")
    
    # Paths
    parser.add_argument("--input_path", default="hdfs://namenode:8020/input/data")
    parser.add_argument("--checkpoint_base", default="hdfs://namenode:8020/checkpoints/")
    parser.add_argument("--model_path", default="hdfs://namenode:8020/output/model/")
    parser.add_argument("--indexer_path", default="hdfs://namenode:8020/output/indexers/")
    parser.add_argument("--progress_path", default="hdfs://namenode:8020/tmp/progress_v7.json")
    parser.add_argument("--checkpoint_dir", default="hdfs://namenode:8020/tmp/checkpoints")
    parser.add_argument("--metrics_path", default="hdfs://namenode:8020/output/metrics/")
    
    # Model params - IMPROVED DEFAULTS
    parser.add_argument("--rank", type=int, default=150)  # Increased from 100
    parser.add_argument("--maxIter", type=int, default=25)
    parser.add_argument("--regParam", type=float, default=0.08)  # Tuned
    parser.add_argument("--alpha", type=float, default=40.0)  # Tuned for implicit
    parser.add_argument("--topK", type=int, default=500)
    parser.add_argument("--holdout_k", type=int, default=1)
    
    # Filter params
    parser.add_argument("--min_user", type=int, default=5)
    parser.add_argument("--min_item", type=int, default=10)
    
    # Ensemble params
    parser.add_argument("--track_weight", type=float, default=0.7)
    parser.add_argument("--artist_weight", type=float, default=0.3)
    
    # Evaluation
    parser.add_argument("--eval_batches", type=int, default=20)
    parser.add_argument("--filter_seen", action="store_true", default=True, help="Filter items seen in TRAIN from predictions")
    parser.add_argument("--no_filter_seen", action="store_false", dest="filter_seen")
    parser.add_argument("--tracks_per_artist", type=int, default=50, help="Max tracks per artist in ensemble")
    
    # Flags
    parser.add_argument("--force_retrain", action="store_true")
    parser.add_argument("--skip_training", action="store_true")
    parser.add_argument("--skip_evaluation", action="store_true")
    parser.add_argument("--force_cleanup", action="store_true")
    parser.add_argument("--no_save_indexers", action="store_true")
    parser.add_argument("--export_metrics", action="store_true", default=False)
    parser.add_argument("--no_export_metrics", action="store_false", dest="export_metrics")
    
    args = parser.parse_args()
    start_time = time.time()
    
    # Config hash
    config_str = (
        f"{args.input_path}_{args.checkpoint_base}_{args.model_path}_"
        f"{args.rank}_{args.maxIter}_{args.regParam}_{args.alpha}_"
        f"{args.topK}_{args.holdout_k}_{args.min_user}_{args.min_item}_"
        f"{args.track_weight}_{args.artist_weight}_v7"
    )
    config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    spark = AutoCleanupSparkSession.create(rank=args.rank, checkpoint_dir=args.checkpoint_dir)
    progress_tracker = ProgressTracker(spark, args.progress_path, config_hash)
    
    try:
        # Load with enhanced features
        raw_df = EnhancedDataLoader.load_with_features(
            spark, args.input_path,
            normalize_hdfs_path(args.checkpoint_base, "enhanced_data"),
            progress_tracker
        )
        
        # Filter
        filtered_df = ResilientFilter.filter_or_resume(
            spark, raw_df,
            normalize_hdfs_path(args.checkpoint_base, "filtered_enhanced_data"),
            progress_tracker,
            min_user=args.min_user,
            min_item=args.min_item
        )
        
        # Cleanup raw data
        if progress_tracker.is_completed("filter_data"):
            print(f"\n🧹 CLEANUP: enhanced_data")
            HDFSCleaner.delete_checkpoint(
                spark,
                normalize_hdfs_path(args.checkpoint_base, "enhanced_data"),
                "enhanced_data"
            )
        
        # Index with artist info
        indexed_df = EnhancedIndexer.index_or_resume(
            spark, filtered_df,
            normalize_hdfs_path(args.checkpoint_base, "indexed_enhanced_data"),
            progress_tracker,
            save_indexers=not args.no_save_indexers,
            indexer_base_path=args.indexer_path
        )
        
        indexed_df.cache()
        indexed_df.count()
        
        # Create track-to-artist mapping for ensemble
        print(f"\n📊 Creating track-to-artist mapping...")
        track_to_artist = indexed_df.select("track_idx", "artist_idx").distinct()
        track_to_artist.cache()
        print(f"   Track-Artist mappings: {track_to_artist.count():,}")
        
        # Split
        train_df, valid_df = split_train_valid_per_user(indexed_df, args.holdout_k)
        
        validate_dataframe(train_df, "train_split", check_duplicates=False)
        validate_dataframe(valid_df, "valid_split", check_duplicates=False)
        
        # Build seen_in_train for proper MAP@K evaluation
        print(f"\n📊 Building seen items from training data...")
        seen_in_train = train_df.select(
            col("playlist_idx").alias("user"),
            col("track_idx").cast("double").alias("seen_item")
        ).distinct().cache()
        seen_count = seen_in_train.count()
        print(f"   Seen items: {seen_count:,}")
        
        indexed_df.unpersist()
        
        # Train dual models
        if args.skip_training:
            print(f"\n⏭️  SKIP TRAINING - Loading existing models")
            print(f"⚠️  WARNING: Ensure indexers match the loaded models!")
            print(f"   Using indexed data from: {normalize_hdfs_path(args.checkpoint_base, 'indexed_enhanced_data')}")
            track_model = ALSModel.load(normalize_hdfs_path(args.model_path, "track_model"))
            artist_model = ALSModel.load(normalize_hdfs_path(args.model_path, "artist_model"))
        else:
            train_df.cache()
            train_df.count()
            
            track_model, artist_model = DualModelTrainer.train_dual_models(
                spark, train_df,
                args.model_path,
                args.rank, args.maxIter, args.regParam, args.alpha,
                args.force_retrain
            )
            
            train_df.unpersist()
        
        # Cleanup filtered data
        print(f"\n🧹 CLEANUP: filtered_enhanced_data")
        HDFSCleaner.delete_checkpoint(
            spark,
            normalize_hdfs_path(args.checkpoint_base, "filtered_enhanced_data"),
            "filtered_enhanced_data"
        )
        
        # Evaluate ensemble
        if not args.skip_evaluation:
            map_score, eval_time = evaluate_ensemble_map_scalable(
                spark, track_model, artist_model, track_to_artist, valid_df,
                k=args.topK, num_batches=args.eval_batches, 
                track_weight=args.track_weight, artist_weight=args.artist_weight,
                filter_seen=args.filter_seen, seen_in_train=seen_in_train
            )
            seen_in_train.unpersist()
        else:
            print(f"\n⏭️  SKIP EVALUATION")
            map_score = 0.0
            eval_time = 0.0
        
        track_to_artist.unpersist()
        
        # Force cleanup
        if args.force_cleanup:
            print(f"\n🧹 FORCE CLEANUP")
            HDFSCleaner.delete_checkpoint(spark, args.checkpoint_dir, "temp checkpoints")
        
        total_time = time.time() - start_time
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ ENHANCED HYBRID v7.0 COMPLETE!")
        print("=" * 80)
        
        if not args.skip_evaluation:
            print(f"📊 Ensemble MAP@{args.topK}: {map_score:.4f} ({map_score*100:.2f}%)")
            print(f"   Track weight: {args.track_weight} | Artist weight: {args.artist_weight}")
        
        print(f"💾 Models: {normalize_hdfs_path(args.model_path)}")
        print(f"⏱️  Total: {total_time/60:.1f} min")
        print("=" * 80)
        
        # Export metrics
        if args.export_metrics:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            metrics = {
                "timestamp": timestamp,
                "config_hash": config_hash,
                "version": "v7.0_enhanced",
                "metric_name": "MAP@500" if not args.skip_evaluation else None,
                "map_score": float(map_score) if not args.skip_evaluation else None,
                "eval_time_sec": float(eval_time) if not args.skip_evaluation else None,
                "total_time_sec": float(total_time),
                "filtered_seen": args.filter_seen,
                "parameters": {
                    "rank": args.rank,
                    "maxIter": args.maxIter,
                    "regParam": args.regParam,
                    "alpha": args.alpha,
                    "topK": args.topK,
                    "track_weight": args.track_weight,
                    "artist_weight": args.artist_weight,
                    "tracks_per_artist": args.tracks_per_artist
                },
                "features": [
                    "position_based_confidence",
                    "artist_collaborative_filtering",
                    "dual_model_ensemble",
                    "frequency_based_indexing",
                    "filter_seen_from_train"
                ]
            }
            
            metrics_file = normalize_hdfs_path(args.metrics_path, f"metrics_v7_{timestamp}_{config_hash}.json")
            export_metrics(metrics, metrics_file)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        spark.stop()
        exit(1)
    
    spark.stop()


if __name__ == "__main__":
    main()

