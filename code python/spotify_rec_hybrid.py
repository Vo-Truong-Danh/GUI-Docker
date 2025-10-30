#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HYBRID AUTO CLEANUP v2.4.0 - ENHANCED LOGGING (JSON INPUT)
=====================================================
Enhanced: Detailed progress tracking + JSON-only input
Optimized for Spotify Million Playlist Dataset (MPD)
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
    row_number, count, ntile, monotonically_increasing_id
)
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.feature import StringIndexer
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
        
        # Write to HDFS using Hadoop API
        spark = SparkSession.getActiveSession()
        hadoop_conf = spark._jsc.hadoopConfiguration()
        uri = spark._jvm.java.net.URI(output_path)
        fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
        path = spark._jvm.org.apache.hadoop.fs.Path(output_path)
        
        output_stream = fs.create(path, True)
        writer = spark._jvm.java.io.BufferedWriter(
            spark._jvm.java.io.OutputStreamWriter(output_stream)
        )
        
        writer.write(metrics_json)
        writer.close()
        
        print(f"✅ Metrics exported to {output_path}")
    except Exception as e:
        print(f"⚠️  Failed to export metrics: {e}")


class AutoCleanupSparkSession:
    @staticmethod
    def create(rank=100, checkpoint_dir=None):
        shuffle_partitions = max(80, min(200, rank))
        
        if checkpoint_dir is None:
            checkpoint_dir = "hdfs://namenode:8020/tmp/checkpoints"
        
        builder = SparkSession.builder \
            .appName("SpotifyRecs_v2.4.0_EnhancedLogging") \
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
        print("🎯 HYBRID AUTO CLEANUP v2.4.0 - ENHANCED LOGGING")
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
        except:
            pass
        
        return {"config_hash": self.config_hash}
    
    def _save(self):
        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            uri = self.spark._jvm.java.net.URI(self.progress_path)
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            path = self.spark._jvm.org.apache.hadoop.fs.Path(self.progress_path)
            
            output_stream = fs.create(path, True)
            writer = self.spark._jvm.java.io.BufferedWriter(
                self.spark._jvm.java.io.OutputStreamWriter(output_stream)
            )
            
            writer.write(json.dumps(self.progress, indent=2))
            writer.close()
        except:
            pass
    
    def is_completed(self, step):
        return self.progress.get(step, False)
    
    def mark_completed(self, step):
        self.progress[step] = True
        self._save()


class ResilientDataLoader:
    @staticmethod
    def load_or_resume(spark, input_path, checkpoint_path, progress_tracker):
        checkpoint_path = normalize_hdfs_path(checkpoint_path)
        
        # Check if checkpoint exists on HDFS (even without progress)
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
        
        if (checkpoint_exists and checkpoint_non_empty) or progress_tracker.is_completed("load_data"):
            print(f"\n✅ Loading from checkpoint...")
            try:
                df_cp = spark.read.parquet(checkpoint_path)
                # If checkpoint is raw MPD (columns: info, playlists), normalize to pid/track_uri
                if "playlists" in df_cp.columns and ("pid" not in df_cp.columns or "track_uri" not in df_cp.columns):
                    playlists_df = df_cp.select(F.explode(col("playlists")).alias("pl"))
                    df_cp = playlists_df.select(
                        col("pl.pid").alias("pid"),
                        F.explode(col("pl.tracks")).alias("trk")
                    ).select(
                        col("pid"),
                        col("trk.track_uri").alias("track_uri")
                    ).filter(col("track_uri").isNotNull())
                return df_cp
            except Exception as e:
                print(f"   ⚠️  Checkpoint unreadable ({e}); deleting and reloading raw input...")
                try:
                    hadoop_conf = spark._jsc.hadoopConfiguration()
                    uri = spark._jvm.java.net.URI(checkpoint_path)
                    fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
                    path = spark._jvm.org.apache.hadoop.fs.Path(checkpoint_path)
                    fs.delete(path, True)
                except Exception:
                    pass
                # fall through to raw load below
        
        print(f"\n{'=' * 80}")
        print(f"📥 LOADING DATA")
        print(f"{'=' * 80}")
        print(f"Input path: {input_path}")
        print(f"Format: JSON (MPD dataset)")
        
        # Load JSON directly - MPD format
        print(f"\n🔍 Loading JSON data...")
        try:
            df = spark.read.option("multiLine", True).option("mode", "PERMISSIVE").json(input_path)
            print(f"   ✅ JSON loaded successfully")
        except Exception as e:
            print(f"   ❌ Error loading JSON: {e}")
            raise
        
        print(f"\n📦 Processing MPD structure...")
        # MPD format: explode playlists and tracks
        if "playlists" in df.columns:
            print(f"   🔄 Exploding playlists...")
            playlists_df = df.select(F.explode(col("playlists")).alias("pl"))
            
            print(f"   🔄 Exploding tracks...")
            interactions = playlists_df.select(
                col("pl.pid").alias("pid"),
                F.explode(col("pl.tracks")).alias("trk")
            ).select(
                col("pid"),
                col("trk.track_uri").alias("track_uri")
            ).filter(col("track_uri").isNotNull())
            
            df = interactions
            print(f"   ✅ Converted to pid/track_uri format")
        else:
            # Already in pid/track_uri format
            print(f"   ✅ Already in pid/track_uri format")

        # Cache and checkpoint
        print(f"\n💾 Caching and checkpointing data...")
        df.cache()
        count = df.count()
        print(f"   Interactions loaded: {count:,}")
        
        print(f"\n💾 Saving checkpoint...")
        df.write.mode("overwrite").parquet(checkpoint_path)
        progress_tracker.mark_completed("load_data")
        
        print(f"\n{'=' * 80}")
        print(f"✅ DATA LOADING COMPLETE")
        print(f"{'=' * 80}")
        print(f"   Total interactions: {count:,}")
        print(f"   Checkpoint: {checkpoint_path}")
        print(f"{'=' * 80}")
        
        return df


class ResilientFilter:
    @staticmethod
    def filter_or_resume(spark, raw_df, checkpoint_path, progress_tracker, min_user=5, min_item=10):
        checkpoint_path = normalize_hdfs_path(checkpoint_path)
        
        if progress_tracker.is_completed("filter_data"):
            print(f"\n✅ Loading filtered data from checkpoint...")
            return spark.read.parquet(checkpoint_path)
        
        print(f"\n{'=' * 80}")
        print(f"🔍 FILTERING DATA")
        print(f"{'=' * 80}")
        print(f"Min user interactions: {min_user}")
        print(f"Min item interactions: {min_item}")
        print(f"{'=' * 80}")
        
        print(f"\n💾 Caching raw data...")
        raw_df.cache()
        raw_count = raw_df.count()
        print(f"   Raw interactions: {raw_count:,}")
        
        print(f"\n🔢 Counting user interactions...")
        user_counts = raw_df.groupBy("pid").count().withColumnRenamed("count", "user_count")
        num_users_before = user_counts.count()
        print(f"   Users: {num_users_before:,}")
        
        print(f"\n🔢 Counting item interactions...")
        item_counts = raw_df.groupBy("track_uri").count().withColumnRenamed("count", "item_count")
        num_items_before = item_counts.count()
        print(f"   Items: {num_items_before:,}")
        
        print(f"\n🔗 Applying filters...")
        filtered = raw_df \
            .join(user_counts, "pid") \
            .join(item_counts, "track_uri") \
            .filter((col("user_count") >= min_user) & (col("item_count") >= min_item)) \
            .select("pid", "track_uri")
        
        raw_df.unpersist()
        
        filtered_count = filtered.count()
        num_users_after = filtered.select("pid").distinct().count()
        num_items_after = filtered.select("track_uri").distinct().count()
        
        dropped_interactions = raw_count - filtered_count
        dropped_users = num_users_before - num_users_after
        dropped_items = num_items_before - num_items_after
        
        print(f"\n💾 Saving filtered data...")
        filtered.write.mode("overwrite").parquet(checkpoint_path)
        progress_tracker.mark_completed("filter_data")
        
        print(f"\n{'=' * 80}")
        print(f"✅ FILTERING COMPLETE")
        print(f"{'=' * 80}")
        print(f"   Interactions: {raw_count:,} → {filtered_count:,} (dropped {dropped_interactions:,})")
        print(f"   Users: {num_users_before:,} → {num_users_after:,} (dropped {dropped_users:,})")
        print(f"   Items: {num_items_before:,} → {num_items_after:,} (dropped {dropped_items:,})")
        print(f"   Retention: {filtered_count/raw_count*100:.1f}%")
        print(f"{'=' * 80}")
        
        return filtered


class ResilientIndexer:
    @staticmethod
    def index_or_resume(spark, filtered_df, checkpoint_path, progress_tracker, save_indexers=True, indexer_base_path=None):
        checkpoint_path = normalize_hdfs_path(checkpoint_path)
        
        if progress_tracker.is_completed("index_data"):
            print(f"\n✅ Loading indexed data from checkpoint...")
            return spark.read.parquet(checkpoint_path)
        
        print(f"\n{'=' * 80}")
        print(f"🔢 INDEXING DATA")
        print(f"{'=' * 80}")
        
        before_count = filtered_df.count()
        print(f"   Interactions before indexing: {before_count:,}")
        
        print(f"\n🔢 Indexing users (playlists)...")
        user_indexer = StringIndexer(inputCol="pid", outputCol="playlist_idx", handleInvalid="skip")
        user_indexer_model = user_indexer.fit(filtered_df)
        indexed = user_indexer_model.transform(filtered_df)
        num_users = len(user_indexer_model.labels)
        print(f"   ✅ Users indexed: {num_users:,}")
        
        print(f"\n🔢 Indexing items (tracks)...")
        item_indexer = StringIndexer(inputCol="track_uri", outputCol="track_idx", handleInvalid="skip")
        item_indexer_model = item_indexer.fit(indexed)
        indexed = item_indexer_model.transform(indexed)
        num_items = len(item_indexer_model.labels)
        print(f"   ✅ Items indexed: {num_items:,}")
        
        print(f"\n🔄 Selecting final columns...")
        indexed = indexed.select(
            col("pid").alias("playlist_id"),
            col("playlist_idx").cast("int"),
            col("track_uri"),
            col("track_idx").cast("int")
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
            
            user_indexer_model.write().overwrite().save(user_indexer_path)
            item_indexer_model.write().overwrite().save(item_indexer_path)
            print(f"   ✅ User indexer: {user_indexer_path}")
            print(f"   ✅ Item indexer: {item_indexer_path}")
        
        progress_tracker.mark_completed("index_data")
        
        print(f"\n{'=' * 80}")
        print(f"✅ INDEXING COMPLETE")
        print(f"{'=' * 80}")
        print(f"   Final interactions: {after_count:,}")
        print(f"   Users: {num_users:,}")
        print(f"   Items: {num_items:,}")
        print(f"{'=' * 80}")
        
        # Validate output
        validate_dataframe(indexed, "indexed_data", check_duplicates=False)
        
        return indexed


class HybridTrainer:
    @staticmethod
    def train_or_load(spark, train_df, model_path, rank, max_iter, reg_param, alpha, force_retrain=False):
        model_path = normalize_hdfs_path(model_path)
        
        model_exists = False
        try:
            hadoop_conf = spark._jsc.hadoopConfiguration()
            uri = spark._jvm.java.net.URI(model_path)
            fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            hadoop_path = spark._jvm.org.apache.hadoop.fs.Path(model_path)
            model_exists = fs.exists(hadoop_path)
        except:
            pass
        
        if model_exists and not force_retrain:
            print(f"\n✅ Loading existing model from {model_path}...")
            return ALSModel.load(model_path)
        
        print(f"\n{'=' * 80}")
        print(f"🔥 TRAINING ALS MODEL")
        print(f"{'=' * 80}")
        print(f"📊 Hyperparameters:")
        print(f"   Rank: {rank}")
        print(f"   Max Iterations: {max_iter}")
        print(f"   Regularization: {reg_param}")
        print(f"   Alpha: {alpha}")
        print(f"   Implicit Prefs: True")
        print(f"   Cold Start: drop")
        print(f"   Seed: 42")
        print(f"{'=' * 80}")
        
        training_data = train_df.select(
            col("playlist_idx").alias("user"),
            col("track_idx").alias("item")
        ).withColumn("rating", lit(1.0))
        
        print(f"\n💾 Caching training data...")
        training_data.cache()
        train_count = training_data.count()
        print(f"   Training samples: {train_count:,}")
        
        als = ALS(
            rank=rank, maxIter=max_iter, regParam=reg_param, alpha=alpha,
            userCol="user", itemCol="item", ratingCol="rating",
            coldStartStrategy="drop", implicitPrefs=True,
            seed=42, checkpointInterval=5
        )
        
        print(f"\n🚀 Starting training...")
        start = time.time()
        
        # Note: Spark ALS doesn't provide iteration callbacks
        # So we can only show progress at start/end
        print(f"   Training in progress (this may take several minutes)...")
        print(f"   Checkpoint interval: every 5 iterations")
        
        model = als.fit(training_data)
        
        training_data.unpersist()
        
        training_time = time.time() - start
        
        print(f"\n{'=' * 80}")
        print(f"✅ TRAINING COMPLETED")
        print(f"{'=' * 80}")
        print(f"⏱️  Training Time: {training_time/60:.2f} min ({training_time:.1f}s)")
        print(f"💾 Saving model to {model_path}...")
        
        model.write().overwrite().save(model_path)
        print(f"✅ Model saved successfully")
        print(f"{'=' * 80}")
        
        return model


def train_with_early_stopping(
    spark,
    als: ALS,
    train_df,
    valid_df,
    *,
    max_iter: int,
    step: int = 5,
    patience: int = 2,
    min_delta: float = 0.0,
    k: int = 500,
    eval_batches: int = 10,
    model_path: str = None
):
    """Train ALS with simple early stopping by increasing maxIter and
    evaluating MAP@k on the validation split.

    Note: Spark ALS does not support warm-start; this retrains from scratch
    at each checkpointed iteration count. We stop early if MAP does not
    improve for `patience` checkpoints.
    """
    # Build iteration checkpoints: e.g. [1, 5, 10, 15, ...]
    checkpoints = [1] + [i for i in range(step, max_iter + 1, step)]
    best_map = -1.0
    best_model = None
    best_iter = 0
    no_improve = 0

    print("\n" + "=" * 80)
    print("🧠 EARLY STOPPING TRAINING")
    print("=" * 80)
    print(f"Max Iterations: {max_iter} | Step: {step} | Patience: {patience}")
    print(f"Min Delta: {min_delta} | Eval K: {k} | Batches: {eval_batches}")
    print(f"Checkpoints: {checkpoints}")
    print("=" * 80)

    for idx, it in enumerate(checkpoints, 1):
        print(f"\n{'=' * 80}")
        print(f"🔄 CHECKPOINT {idx}/{len(checkpoints)} - Iteration {it}")
        print(f"{'=' * 80}")
        
        curr_als = als.setMaxIter(it)
        start = time.time()
        print(f"🔥 Training up to iteration {it}...")
        model = curr_als.fit(train_df)
        train_minutes = (time.time() - start) / 60.0
        print(f"✅ Training completed in {train_minutes:.2f} min")

        # Evaluate fast using existing scalable evaluator
        print(f"\n📊 Evaluating at iteration {it}...")
        map_score, eval_time = evaluate_map_ranking_scalable(
            spark, model, valid_df, k=k, num_batches=eval_batches
        )

        # Calculate improvement
        improvement = map_score - best_map
        improvement_pct = (improvement / best_map * 100) if best_map > 0 else float('inf')

        # Print detailed metrics
        print(f"\n📊 ITERATION {it} RESULTS:")
        print(f"   MAP@{k}: {map_score:.4f} ({map_score*100:.2f}%)")
        print(f"   Best MAP: {best_map:.4f} ({best_map*100:.2f}%)")
        print(f"   Improvement: {improvement:+.4f} ({improvement_pct:+.2f}%)")
        print(f"   Training Time: {train_minutes:.2f} min")
        print(f"   Eval Time: {eval_time:.1f}s")

        # Track best
        if map_score > best_map + max(min_delta, 0.0):
            print(f"   ✅ NEW BEST MODEL! (improved by {improvement:.4f})")
            best_map = map_score
            best_model = model
            best_iter = it
            no_improve = 0
            # Optionally save interim best
            if model_path:
                try:
                    print(f"   💾 Saving best model...")
                    model.write().overwrite().save(model_path)
                    print(f"   ✅ Model saved")
                except Exception as e:
                    print(f"   ⚠️  Failed to save: {e}")
        else:
            no_improve += 1
            print(f"   ⏭️  No improvement ({no_improve}/{patience})")

        if no_improve >= patience:
            print(f"\n{'=' * 80}")
            print(f"🛑 EARLY STOPPING at iteration {it}")
            print(f"   Best iteration: {best_iter}")
            print(f"   Best MAP@{k}: {best_map:.4f} ({best_map*100:.2f}%)")
            print(f"   Stopped after {no_improve} iterations without improvement")
            print(f"{'=' * 80}")
            break

    if best_model is None:
        print(f"\n⚠️  No best model found, using last model")
        best_model = model
        best_iter = it

    print(f"\n{'=' * 80}")
    print(f"✅ TRAINING COMPLETE")
    print(f"{'=' * 80}")
    print(f"Final Best MAP@{k}: {best_map:.4f} ({best_map*100:.2f}%)")
    print(f"Best Iteration: {best_iter}")
    print(f"{'=' * 80}")

    return best_model


def split_train_valid_per_user(df, k=1, seed=42):
    """Deterministic leave-k-out split using hash"""
    print(f"\n{'=' * 80}")
    print(f"📊 SPLITTING DATA: Leave-{k}-out per user")
    print(f"{'=' * 80}")
    print(f"Method: Deterministic hash-based ordering")
    print(f"Seed: {seed}")
    print(f"{'=' * 80}")
    
    print(f"\n🔢 Counting items per user...")
    # Window count (no join needed)
    w_count = Window.partitionBy("playlist_idx")
    df_counted = df.withColumn("total_items", count("*").over(w_count))
    
    print(f"🔀 Creating deterministic ordering...")
    # Deterministic ordering using hash
    w_order = Window.partitionBy("playlist_idx").orderBy(
        spark_abs(spark_hash(col("track_uri"))) % 1000000
    )
    ranked = df_counted.withColumn("rn", row_number().over(w_order))
    
    print(f"\n✂️  Splitting into train/validation...")
    # Hold-out k items (first k by hash order) only if user has > k items
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


def evaluate_map_ranking_scalable(spark, model, valid_df, k=500, num_batches=20):
    """
    FIX: Scalable batch evaluation using ntile (NO collect!)
    Compute MAP per batch, then weighted average on driver
    """
    print(f"\n{'=' * 80}")
    print(f"📊 EVALUATING MAP@{k} - SCALABLE BATCH METHOD")
    print(f"{'=' * 80}")
    print(f"Batches: {num_batches} | Method: ntile partitioning")
    print(f"{'=' * 80}")
    
    start_time = time.time()
    
    # Ground truth
    print(f"\n📦 Preparing ground truth...")
    # RankingEvaluator requires both label and prediction columns to be array<double>
    ground_truth = valid_df.groupBy("playlist_idx").agg(
        collect_set(col("track_idx").cast("double")).alias("label")
    ).withColumnRenamed("playlist_idx", "user")
    
    total_users = ground_truth.count()
    print(f"   Total validation users: {total_users:,}")
    
    # FIX v2.3.1: Deterministic batch assignment using user ordering
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
    try:
        evaluator = RankingEvaluator(
            labelCol="label", predictionCol="prediction",
            metricName="meanAveragePrecisionAtK", k=k
        )
        print(f"   Metric: meanAveragePrecisionAtK")
    except:
        evaluator = RankingEvaluator(
            labelCol="label", predictionCol="prediction",
            metricName="meanAveragePrecision"
        )
        print(f"   Metric: meanAveragePrecision (fallback)")
    
    print(f"\n{'=' * 80}")
    print(f"🔄 PROCESSING BATCHES")
    print(f"{'=' * 80}")
    
    # Process each batch
    batch_results = []  # [(map_score, user_count), ...]
    
    for i in range(1, num_batches + 1):
        batch_start = time.time()
        
        batch_gt = gt_batched.filter(col("batch_id") == i).drop("batch_id")
        batch_gt.cache()
        
        batch_user_count = batch_gt.count()
        if batch_user_count == 0:
            print(f"   Batch {i:2d}/{num_batches}: EMPTY - skipping")
            batch_gt.unpersist()
            continue
        
        # Generate recommendations for this batch
        users_for_pred = batch_gt.select("user")
        batch_recs = model.recommendForUserSubset(users_for_pred, k)
        # Cast prediction to array<double>
        batch_preds = batch_recs.select(
            col("user"),
            F.expr("transform(recommendations.item, x -> cast(x as double))").alias("prediction")
        )
        
        # Join and evaluate THIS BATCH
        eval_df = batch_gt.join(batch_preds, "user", "inner")
        batch_map_score = evaluator.evaluate(eval_df)
        
        batch_time = time.time() - batch_start
        
        # Store result
        batch_results.append((batch_map_score, batch_user_count))
        
        batch_gt.unpersist()
        
        # Print progress
        if i % 5 == 0 or i == num_batches or i == 1:
            print(f"   Batch {i:2d}/{num_batches}: MAP={batch_map_score:.4f} | Users={batch_user_count:,} | Time={batch_time:.1f}s")
        elif i % 2 == 0:
            # Print simpler progress every 2 batches
            print(f"   Batch {i:2d}/{num_batches}: MAP={batch_map_score:.4f}")
    
    gt_batched.unpersist()
    
    print(f"\n{'=' * 80}")
    print(f"📊 CALCULATING FINAL METRICS")
    print(f"{'=' * 80}")
    
    # FIX: Weighted average on driver (tiny data)
    total_weighted_score = sum(score * count for score, count in batch_results)
    total_users_evaluated = sum(count for _, count in batch_results)
    
    map_score = total_weighted_score / total_users_evaluated if total_users_evaluated > 0 else 0.0
    
    elapsed = time.time() - start_time
    
    print(f"   Batches processed: {len(batch_results)}/{num_batches}")
    print(f"   Total users evaluated: {total_users_evaluated:,}")
    print(f"   Weighted MAP@{k}: {map_score:.4f} ({map_score*100:.2f}%)")
    print(f"   Total evaluation time: {elapsed:.1f}s ({elapsed/60:.2f} min)")
    print(f"{'=' * 80}")
    print(f"✅ EVALUATION COMPLETE: MAP@{k} = {map_score:.4f}")
    print(f"{'=' * 80}")
    
    return map_score, elapsed


def main():
    parser = argparse.ArgumentParser(description="Hybrid Auto Cleanup v2.4.0 - Enhanced Logging")
    
    # Paths
    parser.add_argument("--input_path", default="hdfs://namenode:8020/input/data/*.json")
    parser.add_argument("--checkpoint_base", default="hdfs://namenode:8020/checkpoints/")
    parser.add_argument("--model_path", default="hdfs://namenode:8020/output/model/als_model")
    parser.add_argument("--indexer_path", default="hdfs://namenode:8020/output/indexers/")
    parser.add_argument("--progress_path", default="hdfs://namenode:8020/tmp/progress.json")
    parser.add_argument("--checkpoint_dir", default="hdfs://namenode:8020/tmp/checkpoints")
    parser.add_argument("--metrics_path", default="hdfs://namenode:8020/output/metrics/")
    
    # Model params
    parser.add_argument("--rank", type=int, default=100)
    parser.add_argument("--maxIter", type=int, default=30)
    parser.add_argument("--regParam", type=float, default=0.05)
    parser.add_argument("--alpha", type=float, default=50.0)
    parser.add_argument("--topK", type=int, default=500)
    parser.add_argument("--holdout_k", type=int, default=1)
    
    # Filter params
    parser.add_argument("--min_user", type=int, default=5)
    parser.add_argument("--min_item", type=int, default=10)
    
    # Evaluation
    parser.add_argument("--eval_batches", type=int, default=20)
    # Mặc định bật Early Stopping; dùng --no_early_stopping để tắt
    parser.add_argument("--early_stopping", action="store_true", default=True)
    parser.add_argument("--no_early_stopping", action="store_false", dest="early_stopping")
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--eval_step", type=int, default=5)
    parser.add_argument("--min_delta", type=float, default=0.0005)
    
    # Flags
    parser.add_argument("--force_retrain", action="store_true")
    parser.add_argument("--skip_training", action="store_true")
    parser.add_argument("--skip_evaluation", action="store_true")
    parser.add_argument("--force_cleanup", action="store_true")
    parser.add_argument("--no_save_indexers", action="store_true")
    parser.add_argument("--export_metrics", action="store_true", default=True)
    
    args = parser.parse_args()
    start_time = time.time()
    
    # Comprehensive config_hash
    config_str = (
        f"{args.input_path}_{args.checkpoint_base}_{args.model_path}_"
        f"{args.indexer_path}_{args.checkpoint_dir}_"
        f"{args.rank}_{args.maxIter}_{args.regParam}_{args.alpha}_"
        f"{args.topK}_{args.holdout_k}_{args.min_user}_{args.min_item}"
    )
    config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    spark = AutoCleanupSparkSession.create(rank=args.rank, checkpoint_dir=args.checkpoint_dir)
    progress_tracker = ProgressTracker(spark, args.progress_path, config_hash)
    
    try:
        # FIX: Check if indexed_data checkpoint exists (fast path for retraining)
        indexed_checkpoint = normalize_hdfs_path(args.checkpoint_base, "indexed_data")
        indexed_exists = False
        try:
            hadoop_conf = spark._jsc.hadoopConfiguration()
            uri = spark._jvm.java.net.URI(indexed_checkpoint)
            fs = spark._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)
            path = spark._jvm.org.apache.hadoop.fs.Path(indexed_checkpoint)
            indexed_exists = fs.exists(path)
        except:
            pass
        
        if indexed_exists and not args.force_retrain:
            print(f"\n✅ FAST PATH: indexed_data checkpoint found, skipping load/filter/index")
            indexed_df = spark.read.parquet(indexed_checkpoint)
            indexed_df.cache()
            indexed_df.count()
            
            # Skip directly to split/train
            train_df, valid_df = split_train_valid_per_user(indexed_df, args.holdout_k)
            validate_dataframe(train_df, "train_split", check_duplicates=False)
            validate_dataframe(valid_df, "valid_split", check_duplicates=False)
            indexed_df.unpersist()
            
        else:
            # Normal path: load/filter/index
            # Load
            raw_df = ResilientDataLoader.load_or_resume(
                spark, args.input_path,
                normalize_hdfs_path(args.checkpoint_base, "raw_data"),
                progress_tracker
            )
            
            # Filter
            filtered_df = ResilientFilter.filter_or_resume(
                spark, raw_df,
                normalize_hdfs_path(args.checkpoint_base, "filtered_data"),
                progress_tracker,
                min_user=args.min_user,
                min_item=args.min_item
            )
            
            # Cleanup #1
            if progress_tracker.is_completed("filter_data"):
                print(f"\n{'=' * 80}")
                print(f"🧹 CLEANUP #1: raw_data")
                print(f"{'=' * 80}")
                HDFSCleaner.delete_checkpoint(
                    spark,
                    normalize_hdfs_path(args.checkpoint_base, "raw_data"),
                    "raw_data"
                )
                print(f"{'=' * 80}")
            
            # Index
            indexed_df = ResilientIndexer.index_or_resume(
                spark, filtered_df,
                normalize_hdfs_path(args.checkpoint_base, "indexed_data"),
                progress_tracker,
                save_indexers=not args.no_save_indexers,
                indexer_base_path=args.indexer_path
            )
            
            indexed_df.cache()
            indexed_df.count()
            
            # Split
            train_df, valid_df = split_train_valid_per_user(indexed_df, args.holdout_k)
            
            # Validate splits
            validate_dataframe(train_df, "train_split", check_duplicates=False)
            validate_dataframe(valid_df, "valid_split", check_duplicates=False)
            
            # Unpersist indexed_df immediately
            indexed_df.unpersist()
        
        # Train or load
        if args.skip_training:
            print(f"\n⏭️  SKIP TRAINING")
            model = ALSModel.load(normalize_hdfs_path(args.model_path))
        else:
            # Cache train_df before fit
            train_df.cache()
            train_df.count()
            
            if args.early_stopping:
                als = ALS(
                    rank=args.rank,
                    maxIter=args.maxIter,
                    regParam=args.regParam,
                    alpha=args.alpha,
                    userCol="user",
                    itemCol="item",
                    ratingCol="rating",
                    coldStartStrategy="drop",
                    implicitPrefs=True,
                    seed=42,
                    checkpointInterval=5
                )

                # Reuse the same training projection as in HybridTrainer
                training_data = train_df.select(
                    col("playlist_idx").alias("user"),
                    col("track_idx").alias("item")
                ).withColumn("rating", lit(1.0))

                model = train_with_early_stopping(
                    spark,
                    als,
                    training_data,
                    valid_df,
                    max_iter=args.maxIter,
                    step=args.eval_step,
                    patience=args.patience,
                    min_delta=args.min_delta,
                    k=args.topK,
                    eval_batches=args.eval_batches,
                    model_path=normalize_hdfs_path(args.model_path)
                )
            else:
                model = HybridTrainer.train_or_load(
                    spark, train_df,
                    normalize_hdfs_path(args.model_path),
                    args.rank, args.maxIter, args.regParam, args.alpha,
                    args.force_retrain
                )
            
            # Unpersist immediately
            train_df.unpersist()
        
        # Cleanup #2
        print(f"\n{'=' * 80}")
        print(f"🧹 CLEANUP #2: filtered_data")
        print(f"{'=' * 80}")
        HDFSCleaner.delete_checkpoint(
            spark,
            normalize_hdfs_path(args.checkpoint_base, "filtered_data"),
            "filtered_data"
        )
        print(f"{'=' * 80}")
        
        # Evaluate
        if not args.skip_evaluation:
            map_score, eval_time = evaluate_map_ranking_scalable(
                spark, model, valid_df, args.topK, args.eval_batches
            )
        else:
            print(f"\n⏭️  SKIP EVALUATION")
            map_score = 0.0
            eval_time = 0.0
        
        # Force cleanup
        if args.force_cleanup:
            print(f"\n{'=' * 80}")
            print(f"🧹 FORCE CLEANUP")
            print(f"{'=' * 80}")
            HDFSCleaner.delete_checkpoint(spark, args.checkpoint_dir, "temp checkpoints")
            print(f"{'=' * 80}")
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ COMPLETE!")
        print("=" * 80)
        
        if not args.skip_evaluation:
            print(f"📊 Validation MAP@{args.topK}: {map_score:.4f} ({map_score*100:.2f}%)")
        
        print(f"💾 Model: {normalize_hdfs_path(args.model_path)}")
        print(f"💾 Data: indexed_data (kept)")
        print(f"🧹 Cleaned: raw_data, filtered_data")
        print(f"⏱️  Total: {total_time/60:.1f} min")
        print("=" * 80)
        
        # Export metrics
        if args.export_metrics:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Calculate dataset statistics
            print(f"\n📊 Calculating dataset statistics...")
            num_train_users = train_df.select("playlist_idx").distinct().count() if 'train_df' in locals() else 0
            num_train_items = train_df.select("track_idx").distinct().count() if 'train_df' in locals() else 0
            num_train_interactions = train_df.count() if 'train_df' in locals() else 0
            
            # Calculate sparsity: 1 - (actual_interactions / possible_interactions)
            if num_train_users > 0 and num_train_items > 0:
                sparsity = 1.0 - (num_train_interactions / (num_train_users * num_train_items))
            else:
                sparsity = 0.0
            
            metrics = {
                "timestamp": timestamp,
                "config_hash": config_hash,
                "map_score": float(map_score) if not args.skip_evaluation else None,
                "eval_time_sec": float(eval_time) if not args.skip_evaluation else None,
                "total_time_sec": float(total_time),
                "dataset_stats": {
                    "num_users": int(num_train_users),
                    "num_items": int(num_train_items),
                    "num_interactions": int(num_train_interactions),
                    "sparsity": float(sparsity),
                    "density": float(1.0 - sparsity)
                },
                "parameters": {
                    "rank": args.rank,
                    "maxIter": args.maxIter,
                    "regParam": args.regParam,
                    "alpha": args.alpha,
                    "topK": args.topK,
                    "holdout_k": args.holdout_k,
                    "min_user": args.min_user,
                    "min_item": args.min_item
                },
                "paths": {
                    "model": normalize_hdfs_path(args.model_path),
                    "indexed_data": normalize_hdfs_path(args.checkpoint_base, "indexed_data"),
                    "indexers": normalize_hdfs_path(args.indexer_path) if not args.no_save_indexers else None
                }
            }
            
            print(f"   Users: {num_train_users:,} | Items: {num_train_items:,}")
            print(f"   Interactions: {num_train_interactions:,} | Sparsity: {sparsity:.4f}")
            
            metrics_file = normalize_hdfs_path(args.metrics_path, f"metrics_{timestamp}_{config_hash}.json")
            export_metrics(metrics, metrics_file)
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: Input data not found")
        print(f"   {e}")
        spark.stop()
        exit(1)
    except MemoryError as e:
        print(f"\n❌ ERROR: Out of Memory")
        print(f"   Try: reduce batch size, increase executor memory, or reduce rank")
        print(f"   {e}")
        spark.stop()
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        spark.stop()
        exit(1)
    
    spark.stop()


if __name__ == "__main__":
    main()
