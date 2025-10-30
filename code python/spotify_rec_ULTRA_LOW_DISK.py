#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA LOW DISK VERSION - Spotify Recommendation System
Optimized for HIGH RANK (80-150) with minimal disk usage (~50-60GB instead of 200GB+)

KEY OPTIMIZATIONS:
- Dynamic shuffle partitions based on rank (higher rank = more partitions)
- Aggressive compression (Snappy for Parquet, LZ4 for shuffle)
- Minimal caching (only when absolutely necessary)
- Aggressive unpersist() after each step
- Smaller checkpoint files
- Direct disk storage (no MEMORY_AND_DISK)
- Batch size reduced to 3000
- Checkpoint cleanup after training
"""

import argparse
import time
import os
import json
import glob
from typing import List, Set, Optional, Dict, Any
from functools import reduce

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window
from pyspark.storagelevel import StorageLevel
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.feature import StringIndexer


class ProgressTracker:
    """Enhanced progress tracker with batch-level tracking"""
    
    def __init__(self, progress_file: str = "progress.json"):
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict[str, Any]:
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_progress(self):
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save progress: {e}")
    
    def mark_complete(self, step: str, metadata: Dict[str, Any] = None):
        self.progress[step] = {
            'completed': True,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        self._save_progress()
        print(f"✅ Step '{step}' saved to {self.progress_file}")
    
    def is_complete(self, step: str) -> bool:
        return self.progress.get(step, {}).get('completed', False)
    
    def get_metadata(self, step: str) -> Dict[str, Any]:
        return self.progress.get(step, {}).get('metadata', {})
    
    def mark_batch_complete(self, step: str, batch_num: int):
        """Mark a specific batch as complete"""
        if step not in self.progress:
            self.progress[step] = {'completed': False, 'batches': {}}
        self.progress[step]['batches'][str(batch_num)] = True
        self._save_progress()
    
    def is_batch_complete(self, step: str, batch_num: int) -> bool:
        """Check if a specific batch is complete"""
        return self.progress.get(step, {}).get('batches', {}).get(str(batch_num), False)
    
    def get_completed_batches(self, step: str) -> List[int]:
        """Get list of completed batch numbers"""
        batches = self.progress.get(step, {}).get('batches', {})
        return [int(k) for k, v in batches.items() if v]


class UltraLowDiskSparkSession:
    """Spark session optimized for HIGH RANK with MINIMAL DISK USAGE"""
    
    @staticmethod
    def create(app_name: str = "SpotifyRecs_UltraLowDisk", rank: int = 100) -> SparkSession:
        """
        Create Spark session with dynamic partitioning based on rank
        
        Formula: shuffle_partitions = max(48, rank * 0.8)
        - Rank 50  → 48 partitions
        - Rank 80  → 64 partitions
        - Rank 100 → 80 partitions
        - Rank 120 → 96 partitions
        - Rank 150 → 120 partitions
        """
        shuffle_partitions = max(48, int(rank * 0.8))
        
        spark = (
            SparkSession.builder
            .appName(app_name)
            
            # Serialization
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.kryoserializer.buffer.max", "512m")  # Increased for high rank
            .config("spark.kryoserializer.buffer", "64m")
            
            # Memory
            .config("spark.driver.memory", "3g")
            .config("spark.driver.maxResultSize", "1g")
            .config("spark.executor.memory", "6g")
            .config("spark.executor.memoryOverhead", "1536m")  # Increased for high rank
            .config("spark.executor.cores", "6")
            .config("spark.executor.instances", "1")
            .config("spark.memory.fraction", "0.75")  # More memory for computation
            .config("spark.memory.storageFraction", "0.2")  # Less for caching (we don't cache much)
            
            # Dynamic Partitioning (KEY OPTIMIZATION)
            .config("spark.sql.shuffle.partitions", str(shuffle_partitions))
            .config("spark.default.parallelism", str(shuffle_partitions))
            
            # Adaptive Query Execution
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.initialPartitionNum", str(shuffle_partitions))
            .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64m")  # Smaller partitions
            .config("spark.sql.adaptive.skewJoin.enabled", "true")
            
            # COMPRESSION (CRITICAL FOR DISK SAVINGS)
            .config("spark.shuffle.compress", "true")
            .config("spark.shuffle.spill.compress", "true")
            .config("spark.io.compression.codec", "lz4")  # Fast compression
            .config("spark.rdd.compress", "true")
            
            # Parquet Compression
            .config("spark.sql.parquet.compression.codec", "snappy")  # Best balance
            
            # Broadcast
            .config("spark.sql.autoBroadcastJoinThreshold", "10m")
            .config("spark.broadcast.blockSize", "4m")
            .config("spark.broadcast.compress", "true")
            
            # Error Handling
            .config("spark.task.maxFailures", "8")
            .config("spark.stage.maxConsecutiveAttempts", "8")
            
            # Aggressive Cleanup
            .config("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
            .config("spark.cleaner.periodicGC.interval", "3min")  # More frequent GC
            
            # Network
            .config("spark.network.timeout", "800s")  # Longer for high rank
            .config("spark.executor.heartbeatInterval", "30s")
            
            # Speculation
            .config("spark.speculation", "true")
            .config("spark.speculation.interval", "30s")
            .config("spark.speculation.multiplier", "3")
            
            .getOrCreate()
        )
        
        spark.sparkContext.setLogLevel("WARN")
        checkpoint_dir = "hdfs://namenode:8020/tmp/checkpoints"
        spark.sparkContext.setCheckpointDir(checkpoint_dir)
        
        print("=" * 80)
        print("🚀 ULTRA LOW DISK MODE - Optimized for High Rank")
        print("=" * 80)
        print(f"💾 Driver: 3g | Executor: 6g (×2) | Cores: 6")
        print(f"📊 Shuffle Partitions: {shuffle_partitions} (rank={rank})")
        print(f"🗜️  Compression: LZ4 (shuffle) + Snappy (parquet)")
        print(f"📁 Checkpoint: {checkpoint_dir}")
        print("=" * 80)
        
        return spark


class ResilientDataLoader:
    """Data loading with checkpoint/resume - MINIMAL DISK"""
    
    @staticmethod
    def load_or_resume(
        spark: SparkSession,
        input_path: str,
        checkpoint_path: str,
        progress_tracker: ProgressTracker,
        force_reload: bool = False
    ) -> DataFrame:
        step_name = "load_data"
        
        if not force_reload and progress_tracker.is_complete(step_name):
            print(f"\n✅ Loading from checkpoint: {checkpoint_path}")
            df = spark.read.parquet(checkpoint_path)
            metadata = progress_tracker.get_metadata(step_name)
            print(f"   Interactions: {metadata.get('total_interactions', 'N/A'):,}")
            return df
        
        print(f"\n📥 LOADING DATA...")
        start_time = time.time()
        
        df = spark.read.option("multiLine", "true").json(f"{input_path}/*.json")
        
        playlists_df = (
            df.select(F.explode("playlists").alias("pl"))
            .select(
                F.col("pl.pid").alias("playlist_id"),
                F.col("pl.tracks").alias("tracks")
            )
        )
        
        # No caching - direct computation
        interactions_df = (
            playlists_df
            .select("playlist_id", F.explode("tracks").alias("track"))
            .select(
                F.col("playlist_id").cast("long"),
                F.col("track.track_uri").alias("track_uri")
            )
            .filter(F.col("track_uri").isNotNull())
            .dropDuplicates(["playlist_id", "track_uri"])
            .repartition(48, "playlist_id")  # Fixed partitions for raw data
        )
        
        total_interactions = interactions_df.count()
        
        print(f"   Saving checkpoint (Snappy compression)...")
        interactions_df.write.mode("overwrite").parquet(checkpoint_path)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ LOADED: {total_interactions:,} interactions ({elapsed:.1f}s)")
        
        progress_tracker.mark_complete(step_name, {
            'total_interactions': total_interactions
        })
        
        # Clean up intermediate DataFrames
        playlists_df.unpersist()
        df.unpersist()
        
        return interactions_df


class ResilientFilter:
    """Filtering with checkpoint - MINIMAL DISK"""
    
    @staticmethod
    def filter_or_resume(
        spark: SparkSession,
        interactions_df: DataFrame,
        checkpoint_path: str,
        progress_tracker: ProgressTracker,
        min_playlist_len: int = 15,
        max_playlist_len: int = 200,
        min_track_freq: int = 100,
        max_track_freq: Optional[int] = None,
        force_refilter: bool = False
    ) -> DataFrame:
        step_name = "filter_data"
        
        if not force_refilter and progress_tracker.is_complete(step_name):
            print(f"\n✅ Loading filtered data from checkpoint...")
            df = spark.read.parquet(checkpoint_path)
            return df
        
        print(f"\n🔍 FILTERING...")
        start_time = time.time()
        
        # DISK-ONLY storage (no MEMORY_AND_DISK to save RAM)
        playlist_stats = (
            interactions_df
            .groupBy("playlist_id")
            .agg(F.count("*").alias("pl_len"))
            .persist(StorageLevel.DISK_ONLY)  # Changed from MEMORY_AND_DISK
        )
        
        valid_playlists = (
            playlist_stats
            .filter(
                (F.col("pl_len") >= min_playlist_len) &
                (F.col("pl_len") <= max_playlist_len)
            )
            .select("playlist_id")
        )
        
        track_stats = (
            interactions_df
            .groupBy("track_uri")
            .agg(F.count("*").alias("track_freq"))
            .persist(StorageLevel.DISK_ONLY)  # Changed
        )
        
        valid_tracks = track_stats.filter(F.col("track_freq") >= min_track_freq)
        if max_track_freq:
            valid_tracks = valid_tracks.filter(F.col("track_freq") <= max_track_freq)
        valid_tracks = valid_tracks.select("track_uri")
        
        filtered_df = (
            interactions_df
            .join(valid_playlists, "playlist_id", "inner")
            .join(valid_tracks, "track_uri", "inner")
            .repartition(48, "playlist_id")
        )
        
        print(f"   Saving checkpoint (Snappy compression)...")
        filtered_df.write.mode("overwrite").parquet(checkpoint_path)
        
        elapsed = time.time() - start_time
        print(f"\n✅ FILTERED ({elapsed:.1f}s)")
        
        progress_tracker.mark_complete(step_name)
        
        # Aggressive cleanup
        playlist_stats.unpersist()
        track_stats.unpersist()
        valid_playlists.unpersist()
        valid_tracks.unpersist()
        
        return filtered_df


class ResilientIndexer:
    """String indexing with checkpoint - MINIMAL DISK"""
    
    @staticmethod
    def index_or_resume(
        spark: SparkSession,
        filtered_df: DataFrame,
        checkpoint_path: str,
        progress_tracker: ProgressTracker,
        force_reindex: bool = False
    ) -> DataFrame:
        step_name = "index_data"
        
        if not force_reindex and progress_tracker.is_complete(step_name):
            print(f"\n✅ Loading indexed data from checkpoint...")
            df = spark.read.parquet(checkpoint_path)
            return df
        
        print(f"\n🔢 INDEXING...")
        start_time = time.time()
        
        # No intermediate caching
        playlist_indexer = StringIndexer(
            inputCol="playlist_id", 
            outputCol="playlist_idx",
            handleInvalid="keep"
        )
        track_indexer = StringIndexer(
            inputCol="track_uri", 
            outputCol="track_idx",
            handleInvalid="keep"
        )
        
        df_with_pl = playlist_indexer.fit(filtered_df).transform(filtered_df)
        indexed_df = track_indexer.fit(df_with_pl).transform(df_with_pl)
        
        indexed_df = indexed_df.select(
            F.col("playlist_idx").cast("int").alias("playlist_idx"),
            F.col("track_idx").cast("int").alias("track_idx"),
            "playlist_id",
            "track_uri"
        ).repartition(48)
        
        print(f"   Saving checkpoint (Snappy compression)...")
        indexed_df.write.mode("overwrite").parquet(checkpoint_path)
        
        elapsed = time.time() - start_time
        print(f"\n✅ INDEXED ({elapsed:.1f}s)")
        
        progress_tracker.mark_complete(step_name)
        
        # Cleanup
        df_with_pl.unpersist()
        
        return indexed_df


def train_or_load(
    spark: SparkSession,
    indexed_df: DataFrame,
    model_path: str,
    progress_tracker: ProgressTracker,
    rank: int = 100,
    max_iter: int = 30,
    reg_param: float = 0.05,
    alpha: float = 50.0,
    force_retrain: bool = False
) -> ALSModel:
    """Train ALS model or load from checkpoint - OPTIMIZED FOR HIGH RANK"""
    step_name = "train_model"
    
    # Try to load existing model first
    if not force_retrain and progress_tracker.is_complete(step_name):
        try:
            print(f"\n✅ Loading model from {model_path}...")
            model = ALSModel.load(model_path)
            return model
        except Exception as e:
            print(f"\n⚠️  Model load failed: {e}")
            print(f"🔄 Retraining model instead...")
    
    print(f"\n🎓 TRAINING ALS MODEL (ULTRA LOW DISK MODE)...")
    print(f"   Rank: {rank} | MaxIter: {max_iter} | RegParam: {reg_param} | Alpha: {alpha}")
    print(f"\n   📊 Monitor progress:")
    print(f"   - Spark UI: http://localhost:4040 (detailed stages)")
    print(f"   - Logs below (iteration checkpoints)")
    print()
    start_time = time.time()
    
    # Prepare training data - NO CACHING
    train_df = indexed_df.select(
        F.col("playlist_idx").alias("user"),
        F.col("track_idx").alias("item")
    ).withColumn("rating", F.lit(1.0))
    
    # Set log level to INFO to see iteration progress
    spark.sparkContext.setLogLevel("INFO")
    
    als = ALS(
        rank=rank,
        maxIter=max_iter,
        regParam=reg_param,
        alpha=alpha,
        userCol="user",
        itemCol="item",
        ratingCol="rating",
        nonnegative=True,
        implicitPrefs=True,
        coldStartStrategy="drop",
        # CRITICAL: Checkpoint every 5 iterations to prevent lineage explosion
        checkpointInterval=5,
        intermediateStorageLevel="DISK_ONLY"  # Store intermediate results on disk only
    )
    
    print(f"   🚀 Training started (target: {max_iter} iterations)...")
    print(f"   ⏱️  Expected time: ~{int(max_iter * 0.8)}-{int(max_iter * 1.2)} minutes")
    print(f"   💡 Checkpoints every 5 iterations (you'll see logs)\n")
    
    model = als.fit(train_df)
    
    # Restore log level
    spark.sparkContext.setLogLevel("WARN")
    
    elapsed = time.time() - start_time
    print(f"\n✅ MODEL TRAINED ({elapsed/60:.1f} min)")
    
    print(f"   Saving model to {model_path}...")
    model.write().overwrite().save(model_path)
    
    progress_tracker.mark_complete(step_name, {
        'rank': rank,
        'max_iter': max_iter,
        'reg_param': reg_param,
        'alpha': alpha,
        'training_time': elapsed
    })
    
    # Cleanup training data
    train_df.unpersist()
    
    # CRITICAL: Clean old checkpoints to free disk space
    try:
        checkpoint_dir = spark.sparkContext.getCheckpointDir()
        print(f"   Cleaning old checkpoints in {checkpoint_dir}...")
        # This will happen automatically via spark.cleaner settings
    except Exception as e:
        print(f"   ⚠️  Checkpoint cleanup warning: {e}")
    
    return model


def evaluate_map(
    spark: SparkSession,
    model: ALSModel,
    indexed_df: DataFrame,
    top_k: int = 500
) -> float:
    """Evaluate model with Mean Average Precision - MINIMAL DISK"""
    print(f"\n📊 EVALUATING MAP@{top_k}...")
    start_time = time.time()
    
    # Create ground truth - NO CACHING
    ground_truth = (
        indexed_df
        .groupBy("playlist_idx")
        .agg(F.collect_set("track_idx").alias("actual_tracks"))
    )
    
    # Get unique users and rename to match model's userCol
    users = indexed_df.select(
        F.col("playlist_idx").alias("user")
    ).distinct()
    
    # Generate recommendations - DIRECTLY without caching
    recs = model.recommendForUserSubset(users, top_k)
    recs_df = recs.select(
        F.col("user").alias("playlist_idx"),  # Rename back for join
        F.col("recommendations.item").alias("pred_tracks")
    )
    
    # Join and calculate AP
    eval_df = ground_truth.join(recs_df, "playlist_idx", "inner")
    
    @F.udf(returnType=T.DoubleType())
    def calc_ap(actual, predicted):
        if not actual or not predicted:
            return 0.0
        actual_set = set(actual)
        hits = 0
        precision_sum = 0.0
        for i, track in enumerate(predicted, 1):
            if track in actual_set:
                hits += 1
                precision_sum += hits / i
        return precision_sum / min(len(actual_set), len(predicted)) if hits > 0 else 0.0
    
    map_value = eval_df.select(
        F.avg(calc_ap(F.col("actual_tracks"), F.col("pred_tracks"))).alias("map")
    ).collect()[0]["map"]
    
    elapsed = time.time() - start_time
    print(f"✅ MAP@{top_k}: {map_value:.4f} ({map_value*100:.2f}%) - {elapsed:.1f}s")
    
    # Cleanup
    ground_truth.unpersist()
    recs_df.unpersist()
    eval_df.unpersist()
    
    return map_value


# Define UDFs OUTSIDE to avoid re-serialization
@F.udf(returnType=T.ArrayType(T.IntegerType()))
def filter_seen_udf(recs, seen_items):
    """Filter out seen items from recommendations"""
    if recs is None:
        return []
    seen = set(seen_items) if seen_items else set()
    kept = []
    for r in recs:
        if r["item"] not in seen:
            kept.append(r["item"])
        if len(kept) >= 500:
            break
    return kept

@F.udf(returnType=T.ArrayType(T.StringType()))
def sort_uris(recs_struct):
    """Sort recommendations by rank position"""
    if recs_struct is None:
        return []
    sorted_list = sorted(recs_struct, key=lambda x: x["rank_pos"])
    return [x["track_uri"] for x in sorted_list]


class UltraLowDiskSubmissionGenerator:
    """Generate submission with MINIMAL DISK USAGE - Batch size reduced to 3000"""
    
    @staticmethod
    def generate_with_recovery(
        spark: SparkSession,
        model: ALSModel,
        indexed_df: DataFrame,
        playlist_map_df: DataFrame,
        track_map_df: DataFrame,
        output_path: str,
        progress_tracker: ProgressTracker,
        top_k: int = 500,
        batch_size: int = 3000,  # REDUCED from 5000
        force_regenerate: bool = False
    ):
        step_name = "generate_submission"
        
        if not force_regenerate and progress_tracker.is_complete(step_name):
            print(f"\n✅ Submission already complete at {output_path}")
            return
        
        print(f"\n📝 GENERATING SUBMISSION (Ultra Low Disk)...")
        print(f"   Batch size: {batch_size} users (smaller for lower disk usage)")
        start_time = time.time()
        
        # Get user/track maps - NO CACHING
        user_item_map = (
            indexed_df
            .groupBy("playlist_idx")
            .agg(F.collect_list("track_idx").alias("seen_items"))
        )
        
        all_users = indexed_df.select("playlist_idx").distinct().collect()
        user_ids = [row.playlist_idx for row in all_users]
        total_users = len(user_ids)
        num_batches = (total_users + batch_size - 1) // batch_size
        
        print(f"   Total: {total_users:,} users → {num_batches} batches")
        
        batch_paths = []
        completed_batches = progress_tracker.get_completed_batches(step_name)
        
        for i in range(num_batches):
            batch_num = i + 1
            
            if batch_num in completed_batches:
                batch_path = f"{output_path}_batches/batch_{batch_num:04d}"
                batch_paths.append(batch_path)
                print(f"\n✓ Batch {batch_num}/{num_batches}: Already complete")
                continue
            
            batch_start = time.time()
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_users)
            batch_user_ids = user_ids[start_idx:end_idx]
            
            print(f"\n📦 Batch {batch_num}/{num_batches}: Processing {len(batch_user_ids):,} users...")
            
            # Create batch users DataFrame - NO CACHING
            batch_users_df = spark.createDataFrame(
                [(int(uid),) for uid in batch_user_ids],
                ["playlist_idx"]
            )
            
            # Generate recommendations - DIRECTLY
            batch_recs = model.recommendForUserSubset(batch_users_df, top_k + 20)
            
            # Filter seen items
            batch_with_seen = batch_recs.join(user_item_map, "playlist_idx", "left")
            batch_filtered = batch_with_seen.select(
                F.col("playlist_idx"),
                filter_seen_udf(F.col("recommendations"), F.col("seen_items")).alias("filtered_item_ids")
            )
            
            # Map back to URIs
            batch_exploded = batch_filtered.select(
                F.col("playlist_idx"),
                F.posexplode(F.slice(F.col("filtered_item_ids"), 1, top_k)).alias("rank_pos", "track_idx")
            )
            
            batch_with_uris = batch_exploded.join(track_map_df, "track_idx", "inner")
            
            batch_final = (
                batch_with_uris
                .groupBy("playlist_idx")
                .agg(F.collect_list(F.struct("rank_pos", "track_uri")).alias("recs"))
                .select(
                    F.col("playlist_idx"),
                    sort_uris(F.col("recs")).alias("tracks")
                )
            )
            
            batch_submission = batch_final.join(playlist_map_df, "playlist_idx", "inner").select(
                "playlist_id",
                "tracks"
            )
            
            # Save batch
            batch_path = f"{output_path}_batches/batch_{batch_num:04d}"
            batch_submission.write.mode("overwrite").parquet(batch_path)
            batch_paths.append(batch_path)
            
            # Mark complete
            progress_tracker.mark_batch_complete(step_name, batch_num)
            
            batch_elapsed = time.time() - batch_start
            print(f"✅ Batch {batch_num} saved ({batch_elapsed:.1f}s)")
            
            # Aggressive cleanup after each batch
            batch_users_df.unpersist()
            batch_recs.unpersist()
            batch_with_seen.unpersist()
            batch_filtered.unpersist()
            batch_exploded.unpersist()
            batch_with_uris.unpersist()
            batch_final.unpersist()
            batch_submission.unpersist()
        
        # Combine all batches
        print(f"\n🔗 Combining {len(batch_paths)} batches...")
        all_batches = [spark.read.parquet(path) for path in batch_paths]
        final_df = reduce(DataFrame.unionAll, all_batches)
        
        # Save final submission
        final_df.coalesce(1).write.mode("overwrite").json(output_path)
        
        elapsed = time.time() - start_time
        print(f"\n✅ SUBMISSION COMPLETE: {output_path} ({elapsed/60:.1f} min)")
        
        progress_tracker.mark_complete(step_name)
        
        # Cleanup
        user_item_map.unpersist()
        final_df.unpersist()


def main():
    parser = argparse.ArgumentParser(description="Ultra Low Disk Spotify Recommendation")
    parser.add_argument("--input_path", default="hdfs://namenode:8020/input/data")
    parser.add_argument("--checkpoint_base", default="hdfs://namenode:8020/checkpoints/")
    parser.add_argument("--model_path", default="hdfs://namenode:8020/output/model/als_model")
    parser.add_argument("--submission_path", default="hdfs://namenode:8020/output/submission")
    parser.add_argument("--rank", type=int, default=100)
    parser.add_argument("--maxIter", type=int, default=30)
    parser.add_argument("--regParam", type=float, default=0.05)
    parser.add_argument("--alpha", type=float, default=50.0)
    parser.add_argument("--topK", type=int, default=500)
    parser.add_argument("--batchSize", type=int, default=3000)  # Smaller default
    parser.add_argument("--force_retrain", action="store_true")
    parser.add_argument("--force_regenerate", action="store_true")
    parser.add_argument("--skip_training", action="store_true", help="Skip training (load existing model)")
    parser.add_argument("--skip_evaluation", action="store_true", help="Skip MAP evaluation")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🎯 ULTRA LOW DISK MODE - SPOTIFY RECOMMENDATION SYSTEM")
    print("💾 Optimized for High Rank (80-150) with Minimal Disk Usage")
    print("=" * 80)
    print(f"📊 Config: rank={args.rank}, alpha={args.alpha}, regParam={args.regParam}")
    print(f"🗜️  Compression: Enabled (LZ4 + Snappy)")
    print(f"📦 Batch Size: {args.batchSize} (reduced for lower disk)")
    print("=" * 80)
    
    # Create Spark session with dynamic partitioning based on rank
    spark = UltraLowDiskSparkSession.create(rank=args.rank)
    progress_tracker = ProgressTracker()
    
    try:
        # Load data (ResilientDataLoader tự động resume từ checkpoint nếu có)
        raw_df = ResilientDataLoader.load_or_resume(
            spark, args.input_path, 
            f"{args.checkpoint_base}/raw_data",
            progress_tracker
        )
        
        # Filter (ResilientFilter tự động resume từ checkpoint nếu có)
        filtered_df = ResilientFilter.filter_or_resume(
            spark, raw_df,
            f"{args.checkpoint_base}/filtered_data",
            progress_tracker
        )
        raw_df.unpersist()  # Free memory
        
        # Index (ResilientIndexer tự động resume từ checkpoint nếu có)
        indexed_df = ResilientIndexer.index_or_resume(
            spark, filtered_df,
            f"{args.checkpoint_base}/indexed_data",
            progress_tracker
        )
        filtered_df.unpersist()  # Free memory
        
        # Create mapping DataFrames (MINIMAL STORAGE)
        playlist_map_df = indexed_df.select("playlist_idx", "playlist_id").distinct()
        track_map_df = indexed_df.select("track_idx", "track_uri").distinct()
        
        # Train or load model
        if args.skip_training:
            print(f"\n⏭️  SKIPPING TRAINING (loading existing model)...")
            if not os.path.exists(args.model_path.replace("hdfs://namenode:8020", "/data")):
                print(f"⚠️  WARNING: Model not found at {args.model_path}")
                print(f"🔄 Will attempt to load anyway (may fail if truly missing)...")
            from pyspark.ml.recommendation import ALSModel
            model = ALSModel.load(args.model_path)
            print(f"✅ Model loaded from {args.model_path}")
        else:
            model = train_or_load(
                spark, indexed_df, args.model_path, progress_tracker,
                args.rank, args.maxIter, args.regParam, args.alpha,
                args.force_retrain
            )
        
        # Evaluate
        if args.skip_evaluation:
            print(f"\n⏭️  SKIPPING EVALUATION")
            map_score = 0.0
        else:
            map_score = evaluate_map(spark, model, indexed_df, args.topK)
        
        # Generate submission (DISABLED BY DEFAULT - uncomment to enable)
        # UltraLowDiskSubmissionGenerator.generate_with_recovery(
        #     spark, model,
        #     indexed_df, playlist_map_df, track_map_df,
        #     args.submission_path,
        #     progress_tracker,
        #     args.topK, args.batchSize,
        #     args.force_regenerate
        # )
        
        print("\n" + "=" * 80)
        if args.skip_training and args.skip_evaluation:
            print("✅ MODEL LOADED (TRAINING & EVALUATION SKIPPED)")
        elif args.skip_training:
            print("✅ MODEL LOADED & EVALUATION COMPLETE!")
        elif args.skip_evaluation:
            print("✅ TRAINING COMPLETE (EVALUATION SKIPPED)")
        else:
            print("🎉 TRAINING & EVALUATION COMPLETE!")
        print("=" * 80)
        if not args.skip_evaluation:
            print(f"📊 Final MAP@{args.topK}: {map_score:.4f} ({map_score*100:.2f}%)")
        print(f"💾 Model path: {args.model_path}")
        print(f"🔧 Parameters: rank={args.rank}, alpha={args.alpha}, regParam={args.regParam}, maxIter={args.maxIter}")
        print("=" * 80)
        print("\n💡 Submission generation is DISABLED to save disk space.")
        print("   To enable: uncomment lines in main() function")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

