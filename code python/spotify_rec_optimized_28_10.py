#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Spotify Recommendation System - 24GB RAM Edition
Features:
- Checkpointing & Resume capability
- Error handling & auto-retry
- Memory-optimized for 24GB RAM
- Progress tracking & recovery
"""

import argparse
import time
import os
import json
from typing import List, Set, Optional, Dict, Any
from functools import reduce
from pathlib import Path

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window
from pyspark.storagelevel import StorageLevel
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.feature import StringIndexer


class ProgressTracker:
    """Track and save progress for resume capability"""
    
    def __init__(self, progress_file: str = "progress.json"):
        self.progress_file = progress_file
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict[str, Any]:
        """Load existing progress"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_progress(self):
        """Save current progress"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save progress: {e}")
    
    def mark_complete(self, step: str, metadata: Dict[str, Any] = None):
        """Mark a step as complete"""
        self.progress[step] = {
            'completed': True,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        self._save_progress()
        print(f"✅ Step '{step}' marked complete and saved to {self.progress_file}")
    
    def is_complete(self, step: str) -> bool:
        """Check if step is complete"""
        return self.progress.get(step, {}).get('completed', False)
    
    def get_metadata(self, step: str) -> Dict[str, Any]:
        """Get metadata for a step"""
        return self.progress.get(step, {}).get('metadata', {})
    
    def reset_step(self, step: str):
        """Reset a specific step"""
        if step in self.progress:
            del self.progress[step]
            self._save_progress()
            print(f"🔄 Step '{step}' reset")


class OptimizedSparkSession:
    """Spark session optimized for 24GB RAM, 12 cores"""
    
    @staticmethod
    def create(app_name: str = "SpotifyRecs_24GB") -> SparkSession:
        """Create Spark session optimized for 24GB RAM environment"""
        
        # Calculate optimal memory distribution for 24GB
        # Leave 4GB for OS, 20GB for Spark
        # Driver: 8GB, Executor: 10GB, with overheads
        
        spark = (
            SparkSession.builder
            .appName(app_name)
            
            # Serialization
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.kryoserializer.buffer.max", "256m")
            .config("spark.kryoserializer.buffer", "32m")
            
            # Memory - OPTIMIZED FOR 24GB RAM
            .config("spark.driver.memory", "8g")  # Reduced from 6g (but more efficient)
            .config("spark.driver.maxResultSize", "2g")
            .config("spark.executor.memory", "10g")  # Reduced from 8g
            .config("spark.executor.memoryOverhead", "1536m")  # Reduced from 2048m
            .config("spark.executor.cores", "6")  # Half of 12 cores for stability
            .config("spark.executor.instances", "1")  # Single executor for local mode
            
            # Shuffle - OPTIMIZED FOR 12 CORES
            # Rule: 2-3x number of cores
            .config("spark.sql.shuffle.partitions", "36")  # Changed from 600
            .config("spark.default.parallelism", "36")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "36")
            .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128m")
            .config("spark.sql.adaptive.skewJoin.enabled", "true")
            
            # Memory management
            .config("spark.memory.fraction", "0.8")  # Increased from 0.75
            .config("spark.memory.storageFraction", "0.3")  # Increased from 0.2
            .config("spark.shuffle.compress", "true")
            .config("spark.shuffle.spill.compress", "true")
            .config("spark.shuffle.service.enabled", "false")
            
            # Broadcast - Conservative
            .config("spark.sql.autoBroadcastJoinThreshold", "10m")  # Small broadcasts only
            .config("spark.broadcast.blockSize", "4m")
            .config("spark.broadcast.compress", "true")
            
            # Task optimization
            .config("spark.task.maxFailures", "8")  # Increased for resilience
            .config("spark.stage.maxConsecutiveAttempts", "8")
            
            # Checkpointing - CRITICAL FOR RESUME
            .config("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
            .config("spark.cleaner.periodicGC.interval", "5min")
            
            # Speculation - Enable for long tasks
            .config("spark.speculation", "true")
            .config("spark.speculation.interval", "30s")
            .config("spark.speculation.multiplier", "3")
            
            # Network timeout - Increase for large shuffles
            .config("spark.network.timeout", "600s")
            .config("spark.executor.heartbeatInterval", "30s")
            
            .getOrCreate()
        )
        
        spark.sparkContext.setLogLevel("WARN")
        
        # Set checkpoint directory
        checkpoint_dir = "hdfs://namenode:8020/tmp/checkpoints"
        spark.sparkContext.setCheckpointDir(checkpoint_dir)
        
        print("=" * 80)
        print("🚀 Spark Session Created - 24GB RAM Optimized")
        print("=" * 80)
        print(f"📊 Spark Version: {spark.version}")
        print(f"💾 Driver Memory: 8g (optimized for 24GB system)")
        print(f"⚡ Executor Memory: 10g")
        print(f"🔧 Cores: 6 (50% of 12 cores for stability)")
        print(f"📦 Shuffle Partitions: 36 (3x cores)")
        print(f"📁 Checkpoint Dir: {checkpoint_dir}")
        print(f"🔄 Adaptive Execution: Enabled")
        print(f"⏱️  Network Timeout: 600s")
        print("=" * 80)
        
        return spark


class ResilientDataLoader:
    """Data loading with error handling and resume capability"""
    
    @staticmethod
    def load_or_resume(
        spark: SparkSession,
        input_path: str,
        checkpoint_path: str,
        progress_tracker: ProgressTracker,
        force_reload: bool = False
    ) -> DataFrame:
        """Load data with checkpoint/resume support"""
        
        step_name = "load_data"
        
        # Check if already loaded
        if not force_reload and progress_tracker.is_complete(step_name):
            print(f"\n✅ Data already loaded, loading from checkpoint...")
            try:
                df = spark.read.parquet(checkpoint_path)
                metadata = progress_tracker.get_metadata(step_name)
                print(f"   Loaded checkpoint with {metadata.get('total_interactions', 'N/A')} interactions")
                return df
            except Exception as e:
                print(f"⚠️  Could not load checkpoint: {e}")
                print("   Re-loading from source...")
        
        print(f"\n📥 LOADING DATA FROM SOURCE...")
        start_time = time.time()
        
        try:
            # Load with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    df = spark.read.option("multiLine", "true").json(f"{input_path}/*.json")
                    
                    playlists_df = (
                        df.select(F.explode("playlists").alias("pl"))
                        .select(
                            F.col("pl.pid").alias("playlist_id"),
                            F.col("pl.tracks").alias("tracks")
                        )
                    )
                    
                    interactions_df = (
                        playlists_df
                        .select("playlist_id", F.explode("tracks").alias("track"))
                        .select(
                            F.col("playlist_id").cast("long"),
                            F.col("track.track_uri").alias("track_uri")
                        )
                        .filter(F.col("track_uri").isNotNull())
                        .dropDuplicates(["playlist_id", "track_uri"])
                        .repartition(36, "playlist_id")  # Match shuffle partitions
                    )
                    
                    # Compute statistics
                    print("   Computing statistics...")
                    total_interactions = interactions_df.count()
                    total_playlists = interactions_df.select("playlist_id").distinct().count()
                    total_tracks = interactions_df.select("track_uri").distinct().count()
                    
                    # Save checkpoint
                    print(f"   Saving checkpoint to {checkpoint_path}...")
                    interactions_df.write.mode("overwrite").parquet(checkpoint_path)
                    
                    elapsed = time.time() - start_time
                    
                    print("\n" + "=" * 80)
                    print("📈 DATA LOADED SUCCESSFULLY")
                    print("=" * 80)
                    print(f"   Total interactions: {total_interactions:,}")
                    print(f"   Unique playlists: {total_playlists:,}")
                    print(f"   Unique tracks: {total_tracks:,}")
                    print(f"   Avg tracks/playlist: {total_interactions/total_playlists:.1f}")
                    print(f"   ⏱️  Time: {elapsed:.1f}s")
                    print("=" * 80)
                    
                    # Mark complete
                    progress_tracker.mark_complete(step_name, {
                        'total_interactions': total_interactions,
                        'total_playlists': total_playlists,
                        'total_tracks': total_tracks
                    })
                    
                    return interactions_df
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️  Attempt {attempt+1} failed: {e}")
                        print(f"   Retrying in 10s...")
                        time.sleep(10)
                    else:
                        raise
        
        except Exception as e:
            print(f"\n❌ ERROR loading data: {e}")
            raise


class ResilientFilter:
    """Filtering with checkpoint support"""
    
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
        """Filter with resume support"""
        
        step_name = "filter_data"
        
        if not force_refilter and progress_tracker.is_complete(step_name):
            print(f"\n✅ Data already filtered, loading from checkpoint...")
            try:
                df = spark.read.parquet(checkpoint_path)
                metadata = progress_tracker.get_metadata(step_name)
                print(f"   Loaded filtered data: {metadata.get('kept_interactions', 'N/A')} interactions")
                return df
            except Exception as e:
                print(f"⚠️  Could not load checkpoint: {e}")
                print("   Re-filtering...")
        
        print(f"\n🔍 FILTERING DATA...")
        start_time = time.time()
        
        try:
            # Playlist filtering
            print("   Filtering playlists by length...")
            playlist_stats = (
                interactions_df
                .groupBy("playlist_id")
                .agg(F.count("*").alias("pl_len"))
                .persist(StorageLevel.MEMORY_AND_DISK)
            )
            
            valid_playlists = (
                playlist_stats
                .filter(
                    (F.col("pl_len") >= min_playlist_len) &
                    (F.col("pl_len") <= max_playlist_len)
                )
                .select("playlist_id")
            )
            
            kept_playlists = valid_playlists.count()
            print(f"   ✅ Kept playlists: {kept_playlists:,}")
            
            # Track filtering
            print("   Filtering tracks by frequency...")
            track_stats = (
                interactions_df
                .groupBy("track_uri")
                .agg(F.count("*").alias("trk_freq"))
                .persist(StorageLevel.MEMORY_AND_DISK)
            )
            
            if max_track_freq:
                valid_tracks = (
                    track_stats
                    .filter(
                        (F.col("trk_freq") >= min_track_freq) &
                        (F.col("trk_freq") <= max_track_freq)
                    )
                    .select("track_uri")
                )
            else:
                valid_tracks = (
                    track_stats
                    .filter(F.col("trk_freq") >= min_track_freq)
                    .select("track_uri")
                )
            
            kept_tracks = valid_tracks.count()
            print(f"   ✅ Kept tracks: {kept_tracks:,}")
            
            # Join and filter
            print("   Applying filters...")
            if kept_playlists < kept_tracks:
                filtered_df = (
                    interactions_df
                    .join(F.broadcast(valid_playlists), on="playlist_id", how="inner")
                    .join(valid_tracks, on="track_uri", how="inner")
                )
            else:
                filtered_df = (
                    interactions_df
                    .join(valid_playlists, on="playlist_id", how="inner")
                    .join(F.broadcast(valid_tracks), on="track_uri", how="inner")
                )
            
            # Repartition and checkpoint
            filtered_df = filtered_df.repartition(36, "playlist_id")
            
            # Save checkpoint
            print(f"   Saving checkpoint to {checkpoint_path}...")
            filtered_df.write.mode("overwrite").parquet(checkpoint_path)
            
            # Cleanup
            playlist_stats.unpersist()
            track_stats.unpersist()
            
            # Statistics
            kept_interactions = filtered_df.count()
            final_playlists = filtered_df.select("playlist_id").distinct().count()
            final_tracks = filtered_df.select("track_uri").distinct().count()
            
            elapsed = time.time() - start_time
            
            print("\n" + "=" * 80)
            print("✅ FILTERING COMPLETE")
            print("=" * 80)
            print(f"   Interactions: {kept_interactions:,}")
            print(f"   Playlists: {final_playlists:,}")
            print(f"   Tracks: {final_tracks:,}")
            print(f"   Sparsity: {100 - (kept_interactions/(final_playlists*final_tracks)*100):.4f}%")
            print(f"   ⏱️  Time: {elapsed:.1f}s")
            print("=" * 80)
            
            # Mark complete
            progress_tracker.mark_complete(step_name, {
                'kept_interactions': kept_interactions,
                'final_playlists': final_playlists,
                'final_tracks': final_tracks
            })
            
            return filtered_df
            
        except Exception as e:
            print(f"\n❌ ERROR filtering: {e}")
            raise


class ResilientIndexer:
    """Indexing with checkpoint support"""
    
    @staticmethod
    def index_or_resume(
        spark: SparkSession,
        filtered_df: DataFrame,
        checkpoint_path: str,
        map_path: str,
        progress_tracker: ProgressTracker,
        force_reindex: bool = False
    ) -> tuple:
        """Index with resume support"""
        
        step_name = "index_data"
        
        if not force_reindex and progress_tracker.is_complete(step_name):
            print(f"\n✅ Data already indexed, loading from checkpoint...")
            try:
                indexed_df = spark.read.parquet(checkpoint_path)
                playlist_map_df = spark.read.parquet(f"{map_path}/playlist_map")
                track_map_df = spark.read.parquet(f"{map_path}/track_map")
                print(f"   Loaded indexed data successfully")
                return indexed_df, playlist_map_df, track_map_df
            except Exception as e:
                print(f"⚠️  Could not load checkpoint: {e}")
                print("   Re-indexing...")
        
        print(f"\n🔢 INDEXING IDs...")
        start_time = time.time()
        
        try:
            # Repartition
            filtered_df = filtered_df.repartition(36, "playlist_id")
            
            # Build indexers
            print("   Building playlist index...")
            playlist_indexer = StringIndexer(
                inputCol="playlist_id",
                outputCol="playlist_id_idx",
                handleInvalid="skip",
                stringOrderType="frequencyDesc"
            ).fit(filtered_df)
            
            print("   Building track index...")
            track_indexer = StringIndexer(
                inputCol="track_uri",
                outputCol="track_id_idx",
                handleInvalid="skip",
                stringOrderType="frequencyDesc"
            ).fit(filtered_df)
            
            # Apply transformations
            print("   Applying transformations...")
            indexed_df = playlist_indexer.transform(filtered_df)
            indexed_df = track_indexer.transform(indexed_df)
            
            indexed_df = (
                indexed_df
                .withColumn("user", F.col("playlist_id_idx").cast("int"))
                .withColumn("item", F.col("track_id_idx").cast("int"))
                .withColumn("rating", F.lit(1.0).cast("float"))
                .select("user", "item", "rating", "playlist_id", "track_uri")
            )
            
            # Save indexed data checkpoint
            print(f"   Saving indexed data to {checkpoint_path}...")
            indexed_df.write.mode("overwrite").parquet(checkpoint_path)
            
            # Create mapping tables
            print("   Creating mapping tables...")
            playlist_map_df = (
                indexed_df
                .select("user", "playlist_id")
                .dropDuplicates(["user"])
                .withColumnRenamed("user", "user_int")
            )
            
            track_map_df = (
                indexed_df
                .select("item", "track_uri")
                .dropDuplicates(["item"])
                .withColumnRenamed("item", "item_int")
            )
            
            # Save mapping tables
            print(f"   Saving mapping tables to {map_path}...")
            playlist_map_df.write.mode("overwrite").parquet(f"{map_path}/playlist_map")
            track_map_df.write.mode("overwrite").parquet(f"{map_path}/track_map")
            
            # Reload from checkpoint
            indexed_df = spark.read.parquet(checkpoint_path)
            playlist_map_df = spark.read.parquet(f"{map_path}/playlist_map")
            track_map_df = spark.read.parquet(f"{map_path}/track_map")
            
            elapsed = time.time() - start_time
            
            print("\n" + "=" * 80)
            print("✅ INDEXING COMPLETE")
            print("=" * 80)
            print(f"   ⏱️  Time: {elapsed:.1f}s")
            print("=" * 80)
            
            # Mark complete
            progress_tracker.mark_complete(step_name)
            
            return indexed_df, playlist_map_df, track_map_df
            
        except Exception as e:
            print(f"\n❌ ERROR indexing: {e}")
            raise


class ResilientTrainer:
    """Training with checkpoint and resume"""
    
    @staticmethod
    def train_or_load(
        spark: SparkSession,
        indexed_df: DataFrame,
        model_path: str,
        progress_tracker: ProgressTracker,
        rank: int = 12,
        regParam: float = 0.15,
        alpha: float = 10.0,
        maxIter: int = 6,
        force_retrain: bool = False
    ) -> ALSModel:
        """Train with checkpoint support"""
        
        step_name = "train_model"
        
        if not force_retrain and progress_tracker.is_complete(step_name):
            print(f"\n✅ Model already trained, loading...")
            try:
                model = ALSModel.load(model_path)
                print(f"   Model loaded successfully")
                return model
            except Exception as e:
                print(f"⚠️  Could not load model: {e}")
                print("   Re-training...")
        
        print(f"\n🎯 TRAINING ALS MODEL...")
        print("=" * 80)
        print("📋 Hyperparameters (optimized for 24GB):")
        print(f"   Rank: {rank}")
        print(f"   RegParam: {regParam}")
        print(f"   Alpha: {alpha}")
        print(f"   MaxIter: {maxIter}")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # Split data
            train_df, val_df = indexed_df.randomSplit([0.8, 0.2], seed=42)
            train_df = train_df.repartition(36, "user").cache()
            val_df = val_df.repartition(18, "user").cache()
            
            # Configure ALS (adjusted for 24GB RAM)
            als = ALS(
                userCol="user",
                itemCol="item",
                ratingCol="rating",
                implicitPrefs=True,
                rank=rank,
                regParam=regParam,
                alpha=alpha,
                maxIter=maxIter,
                coldStartStrategy="drop",
                nonnegative=False,
                numUserBlocks=18,  # Reduced from 300
                numItemBlocks=18,  # Reduced from 300
                intermediateStorageLevel="MEMORY_AND_DISK",
                finalStorageLevel="MEMORY_AND_DISK",
                checkpointInterval=2
            )
            
            print("\n⏳ Training in progress...")
            model = als.fit(train_df)
            
            # Save model
            print(f"\n💾 Saving model to {model_path}...")
            model.write().overwrite().save(model_path)
            
            elapsed = time.time() - start_time
            
            print("\n" + "=" * 80)
            print("✅ TRAINING COMPLETE")
            print("=" * 80)
            print(f"   ⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
            print("=" * 80)
            
            # Cleanup
            train_df.unpersist()
            val_df.unpersist()
            
            # Mark complete
            progress_tracker.mark_complete(step_name)
            
            return model
            
        except Exception as e:
            print(f"\n❌ ERROR training: {e}")
            raise


class SafeSubmissionGenerator:
    """Memory-safe submission generation"""
    
    @staticmethod
    def generate_with_checkpoints(
        spark: SparkSession,
        model: ALSModel,
        indexed_df: DataFrame,
        playlist_map_df: DataFrame,
        track_map_df: DataFrame,
        output_path: str,
        progress_tracker: ProgressTracker,
        top_k: int = 500,
        batch_size: int = 20000,  # Reduced for 24GB RAM
        force_regenerate: bool = False
    ) -> DataFrame:
        """Generate submission safely"""
        
        step_name = "generate_submission"
        
        if not force_regenerate and progress_tracker.is_complete(step_name):
            print(f"\n✅ Submission already generated")
            print(f"   Output location: {output_path}")
            return None
        
        print(f"\n📝 GENERATING SUBMISSION...")
        print("=" * 80)
        start_time = time.time()
        
        try:
            # Prepare seen items
            print("   Computing seen items...")
            seen_tracks_df = (
                indexed_df
                .groupBy("user")
                .agg(F.collect_set("item").alias("seen_items"))
                .persist(StorageLevel.MEMORY_AND_DISK)
            )
            
            # Get all users
            all_users = indexed_df.select("user").distinct().collect()
            all_user_ids = [row.user for row in all_users]
            total_users = len(all_user_ids)
            
            print(f"   Total users: {total_users:,}")
            print(f"   Batch size: {batch_size:,} (optimized for 24GB)")
            
            # UDFs
            @F.udf(returnType=T.ArrayType(T.IntegerType()))
            def filter_seen_udf(recs, seen_items):
                if recs is None:
                    return []
                seen = set(seen_items) if seen_items else set()
                kept = []
                for r in recs:
                    if r["item"] not in seen:
                        kept.append(r["item"])
                    if len(kept) >= top_k:
                        break
                return kept
            
            @F.udf(returnType=T.ArrayType(T.StringType()))
            def sort_uris(recs_struct):
                if recs_struct is None:
                    return []
                sorted_list = sorted(recs_struct, key=lambda x: x["rank_pos"])
                return [x["track_uri"] for x in sorted_list]
            
            # Process in batches
            submission_parts = []
            num_batches = (total_users + batch_size - 1) // batch_size
            
            for i in range(0, total_users, batch_size):
                batch_num = (i // batch_size) + 1
                batch_ids = all_user_ids[i:i + batch_size]
                
                print(f"\n   📦 Batch {batch_num}/{num_batches}: Processing {len(batch_ids):,} users...")
                batch_start = time.time()
                
                # Create batch
                batch_df = spark.createDataFrame([(uid,) for uid in batch_ids], ["user"])
                
                # Generate recommendations
                recs_df = model.recommendForUserSubset(batch_df, top_k + 100)
                
                # Filter and process
                filtered_df = (
                    recs_df
                    .join(seen_tracks_df, on="user", how="left")
                    .withColumn("filtered_items", filter_seen_udf("recommendations", "seen_items"))
                )
                
                exploded_df = (
                    filtered_df
                    .select(
                        F.col("user").alias("user_int"),
                        F.posexplode("filtered_items").alias("rank_pos", "item_int")
                    )
                    .join(track_map_df, on="item_int", how="left")
                    .join(playlist_map_df, on="user_int", how="left")
                    .select("playlist_id", "rank_pos", "track_uri")
                )
                
                batch_submission = (
                    exploded_df
                    .groupBy("playlist_id")
                    .agg(F.collect_list(F.struct("rank_pos", "track_uri")).alias("recs_struct"))
                    .withColumn("track_uri_list", sort_uris("recs_struct"))
                    .select(
                        F.col("playlist_id").cast("long"),
                        F.concat_ws(",", F.col("track_uri_list")).alias("recommended_track_uris")
                    )
                )
                
                submission_parts.append(batch_submission)
                
                batch_elapsed = time.time() - batch_start
                print(f"      ✅ Completed in {batch_elapsed:.1f}s")
                
                # Periodic checkpoint
                if batch_num % 5 == 0:
                    print(f"   💾 Intermediate save at batch {batch_num}...")
                    temp_submission = reduce(lambda df1, df2: df1.union(df2), submission_parts)
                    temp_submission.repartition(50).write.mode("overwrite") \
                        .parquet(f"{output_path}_temp")
            
            # Final union
            print("\n   🔗 Combining all batches...")
            final_submission = reduce(lambda df1, df2: df1.union(df2), submission_parts)
            
            # Save final submission
            print(f"\n   💾 Saving to {output_path}...")
            final_submission.repartition(50).write.mode("overwrite") \
                .option("header", "true").csv(output_path)
            
            # Cleanup
            seen_tracks_df.unpersist()
            
            elapsed = time.time() - start_time
            
            print("\n" + "=" * 80)
            print("✅ SUBMISSION COMPLETE")
            print("=" * 80)
            print(f"   Expected playlists: {total_users:,}")
            print(f"   Recommendations per playlist: {top_k}")
            print(f"   ⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
            print(f"   📁 Output: {output_path}")
            print("=" * 80)
            
            # Mark complete
            progress_tracker.mark_complete(step_name)
            
            return final_submission
            
        except Exception as e:
            print(f"\n❌ ERROR generating submission: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Optimized Spotify Recommendation System - 24GB RAM Edition"
    )
    
    # Paths
    parser.add_argument("--input_path", type=str,
                       default="hdfs://namenode:8020/input/data/")
    parser.add_argument("--checkpoint_dir", type=str,
                       default="hdfs://namenode:8020/checkpoints/")
    parser.add_argument("--model_path", type=str,
                       default="hdfs://namenode:8020/output/model/als_model")
    parser.add_argument("--submission_path", type=str,
                       default="hdfs://namenode:8020/output/submission")
    
    # Filtering
    parser.add_argument("--min_playlist_len", type=int, default=15)
    parser.add_argument("--max_playlist_len", type=int, default=200)
    parser.add_argument("--min_track_freq", type=int, default=100)
    parser.add_argument("--max_track_freq", type=int, default=None)
    
    # ALS hyperparameters (optimized for 24GB)
    parser.add_argument("--rank", type=int, default=12,  # Reduced from 15
                       help="Latent factors (reduced for 24GB)")
    parser.add_argument("--regParam", type=float, default=0.15)
    parser.add_argument("--alpha", type=float, default=10.0)
    parser.add_argument("--maxIter", type=int, default=6)
    
    # Generation
    parser.add_argument("--topK", type=int, default=500)
    parser.add_argument("--batchSize", type=int, default=20000,  # Reduced
                       help="Batch size (reduced for 24GB)")
    
    # Force flags
    parser.add_argument("--force_reload", action="store_true")
    parser.add_argument("--force_refilter", action="store_true")
    parser.add_argument("--force_reindex", action="store_true")
    parser.add_argument("--force_retrain", action="store_true")
    parser.add_argument("--force_regenerate", action="store_true")
    parser.add_argument("--reset_progress", action="store_true",
                       help="Reset all progress and start from scratch")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🎯 OPTIMIZED SPOTIFY RECOMMENDATION SYSTEM")
    print("💾 24GB RAM Edition with Resume Capability")
    print("=" * 80)
    
    # Initialize progress tracker
    progress_tracker = ProgressTracker("progress.json")
    
    if args.reset_progress:
        print("🔄 Resetting all progress...")
        os.remove("progress.json") if os.path.exists("progress.json") else None
        progress_tracker = ProgressTracker("progress.json")
    
    # Initialize Spark
    spark = OptimizedSparkSession.create()
    
    try:
        # Step 1: Load data
        interactions_df = ResilientDataLoader.load_or_resume(
            spark,
            args.input_path,
            f"{args.checkpoint_dir}/raw_data",
            progress_tracker,
            args.force_reload
        )
        
        # Step 2: Filter data
        filtered_df = ResilientFilter.filter_or_resume(
            spark,
            interactions_df,
            f"{args.checkpoint_dir}/filtered_data",
            progress_tracker,
            args.min_playlist_len,
            args.max_playlist_len,
            args.min_track_freq,
            args.max_track_freq,
            args.force_refilter
        )
        
        # Step 3: Index data
        indexed_df, playlist_map_df, track_map_df = ResilientIndexer.index_or_resume(
            spark,
            filtered_df,
            f"{args.checkpoint_dir}/indexed_data",
            f"{args.checkpoint_dir}/mappings",
            progress_tracker,
            args.force_reindex
        )
        
        # Step 4: Train model
        model = ResilientTrainer.train_or_load(
            spark,
            indexed_df,
            args.model_path,
            progress_tracker,
            args.rank,
            args.regParam,
            args.alpha,
            args.maxIter,
            args.force_retrain
        )
        
        # Step 5: Generate submission
        SafeSubmissionGenerator.generate_with_checkpoints(
            spark,
            model,
            indexed_df,
            playlist_map_df,
            track_map_df,
            args.submission_path,
            progress_tracker,
            args.topK,
            args.batchSize,
            args.force_regenerate
        )
        
        print("\n" + "=" * 80)
        print("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"📊 Submission: {args.submission_path}")
        print(f"💾 Model: {args.model_path}")
        print(f"📁 Progress file: progress.json")
        print("=" * 80)
        print("\n💡 TIP: If interrupted, simply re-run the same command.")
        print("   The system will resume from the last completed step.")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR OCCURRED")
        print("=" * 80)
        print(f"   {str(e)}")
        print("=" * 80)
        print("\n💡 You can resume by running the same command again.")
        print("   Completed steps will be skipped automatically.")
        raise
    finally:
        print("\n🧹 Cleaning up...")
        spark.stop()
        print("✅ Done")


if __name__ == "__main__":
    main()
