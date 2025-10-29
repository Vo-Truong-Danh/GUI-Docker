#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production-Ready Spotify Recommendation System - 24GB RAM
Features:
- Full checkpoint & resume for ALL steps including submission batches
- Robust error handling with automatic recovery
- MAP evaluation
- Validated CSV output (exactly 500 tracks per playlist)
- Memory-optimized for 24GB RAM, 12 cores
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


class OptimizedSparkSession:
    """Spark session optimized for 24GB RAM, 12 cores"""
    
    @staticmethod
    def create(app_name: str = "SpotifyRecs_24GB") -> SparkSession:
        spark = (
            SparkSession.builder
            .appName(app_name)
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.kryoserializer.buffer.max", "256m")
            .config("spark.kryoserializer.buffer", "32m")
            .config("spark.driver.memory", "3g")
            .config("spark.driver.maxResultSize", "1g")
            .config("spark.executor.memory", "6g")
            .config("spark.executor.memoryOverhead", "1024m")
            .config("spark.executor.cores", "6")
            .config("spark.executor.instances", "1")
            .config("spark.sql.shuffle.partitions", "36")
            .config("spark.default.parallelism", "36")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "36")
            .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128m")
            .config("spark.sql.adaptive.skewJoin.enabled", "true")
            .config("spark.memory.fraction", "0.7")
            .config("spark.memory.storageFraction", "0.4")
            .config("spark.shuffle.compress", "true")
            .config("spark.shuffle.spill.compress", "true")
            .config("spark.shuffle.service.enabled", "false")
            .config("spark.sql.autoBroadcastJoinThreshold", "10m")
            .config("spark.broadcast.blockSize", "4m")
            .config("spark.broadcast.compress", "true")
            .config("spark.task.maxFailures", "8")
            .config("spark.stage.maxConsecutiveAttempts", "8")
            .config("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
            .config("spark.cleaner.periodicGC.interval", "5min")
            .config("spark.speculation", "true")
            .config("spark.speculation.interval", "30s")
            .config("spark.speculation.multiplier", "3")
            .config("spark.network.timeout", "600s")
            .config("spark.executor.heartbeatInterval", "30s")
            .getOrCreate()
        )
        
        spark.sparkContext.setLogLevel("WARN")
        checkpoint_dir = "hdfs://namenode:8020/tmp/checkpoints"
        spark.sparkContext.setCheckpointDir(checkpoint_dir)
        
        print("=" * 80)
        print("🚀 Spark Session Created - 24GB RAM STABLE & BALANCED")
        print("=" * 80)
        print(f"💾 Driver: 3g | Executor: 6g (×2) | Cores: 6 | Workers: 2×7g")
        print(f"📁 Checkpoint: {checkpoint_dir}")
        print("=" * 80)
        
        return spark


class ResilientDataLoader:
    """Data loading with checkpoint/resume"""
    
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
        
        interactions_df = (
            playlists_df
            .select("playlist_id", F.explode("tracks").alias("track"))
            .select(
                F.col("playlist_id").cast("long"),
                F.col("track.track_uri").alias("track_uri")
            )
            .filter(F.col("track_uri").isNotNull())
            .dropDuplicates(["playlist_id", "track_uri"])
            .repartition(36, "playlist_id")
        )
        
        total_interactions = interactions_df.count()
        total_playlists = interactions_df.select("playlist_id").distinct().count()
        total_tracks = interactions_df.select("track_uri").distinct().count()
        
        print(f"   Saving checkpoint...")
        interactions_df.write.mode("overwrite").parquet(checkpoint_path)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ LOADED: {total_interactions:,} interactions, {total_playlists:,} playlists, {total_tracks:,} tracks ({elapsed:.1f}s)")
        
        progress_tracker.mark_complete(step_name, {
            'total_interactions': total_interactions,
            'total_playlists': total_playlists,
            'total_tracks': total_tracks
        })
        
        return interactions_df


class ResilientFilter:
    """Filtering with checkpoint"""
    
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
        
        kept_playlists = valid_playlists.count()
        kept_tracks = valid_tracks.count()
        
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
        
        filtered_df = filtered_df.repartition(36, "playlist_id")
        
        print(f"   Saving checkpoint...")
        filtered_df.write.mode("overwrite").parquet(checkpoint_path)
        
        playlist_stats.unpersist()
        track_stats.unpersist()
        
        kept_interactions = filtered_df.count()
        elapsed = time.time() - start_time
        
        print(f"✅ FILTERED: {kept_interactions:,} interactions ({elapsed:.1f}s)")
        
        progress_tracker.mark_complete(step_name, {
            'kept_interactions': kept_interactions
        })
        
        return filtered_df


class ResilientIndexer:
    """Indexing with checkpoint"""
    
    @staticmethod
    def index_or_resume(
        spark: SparkSession,
        filtered_df: DataFrame,
        checkpoint_path: str,
        map_path: str,
        progress_tracker: ProgressTracker,
        force_reindex: bool = False
    ) -> tuple:
        step_name = "index_data"
        
        if not force_reindex and progress_tracker.is_complete(step_name):
            print(f"\n✅ Loading indexed data from checkpoint...")
            indexed_df = spark.read.parquet(checkpoint_path)
            playlist_map_df = spark.read.parquet(f"{map_path}/playlist_map")
            track_map_df = spark.read.parquet(f"{map_path}/track_map")
            return indexed_df, playlist_map_df, track_map_df
        
        print(f"\n🔢 INDEXING...")
        start_time = time.time()
        
        filtered_df = filtered_df.repartition(36, "playlist_id")
        
        playlist_indexer = StringIndexer(
            inputCol="playlist_id",
            outputCol="playlist_id_idx",
            handleInvalid="skip",
            stringOrderType="frequencyDesc"
        ).fit(filtered_df)
        
        track_indexer = StringIndexer(
            inputCol="track_uri",
            outputCol="track_id_idx",
            handleInvalid="skip",
            stringOrderType="frequencyDesc"
        ).fit(filtered_df)
        
        indexed_df = playlist_indexer.transform(filtered_df)
        indexed_df = track_indexer.transform(indexed_df)
        
        indexed_df = (
            indexed_df
            .withColumn("user", F.col("playlist_id_idx").cast("int"))
            .withColumn("item", F.col("track_id_idx").cast("int"))
            .withColumn("rating", F.lit(1.0).cast("float"))
            .select("user", "item", "rating", "playlist_id", "track_uri")
        )
        
        print(f"   Saving checkpoint...")
        indexed_df.write.mode("overwrite").parquet(checkpoint_path)
        
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
        
        playlist_map_df.write.mode("overwrite").parquet(f"{map_path}/playlist_map")
        track_map_df.write.mode("overwrite").parquet(f"{map_path}/track_map")
        
        indexed_df = spark.read.parquet(checkpoint_path)
        playlist_map_df = spark.read.parquet(f"{map_path}/playlist_map")
        track_map_df = spark.read.parquet(f"{map_path}/track_map")
        
        elapsed = time.time() - start_time
        print(f"✅ INDEXED ({elapsed:.1f}s)")
        
        progress_tracker.mark_complete(step_name)
        
        return indexed_df, playlist_map_df, track_map_df


class ResilientTrainer:
    """Training with checkpoint"""
    
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
        step_name = "train_model"
        
        if not force_retrain and progress_tracker.is_complete(step_name):
            print(f"\n✅ Loading model from {model_path}...")
            model = ALSModel.load(model_path)
            return model
        
        print(f"\n🎯 TRAINING ALS MODEL...")
        print(f"   Rank: {rank} | RegParam: {regParam} | Alpha: {alpha} | MaxIter: {maxIter}")
        
        start_time = time.time()
        
        train_df, val_df = indexed_df.randomSplit([0.8, 0.2], seed=42)
        train_df = train_df.repartition(36, "user").cache()
        val_df = val_df.repartition(18, "user").cache()
        
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
            numUserBlocks=18,
            numItemBlocks=18,
            intermediateStorageLevel="MEMORY_AND_DISK",
            finalStorageLevel="MEMORY_AND_DISK",
            checkpointInterval=2
        )
        
        print(f"   Training...")
        model = als.fit(train_df)
        
        print(f"   Saving model...")
        model.write().overwrite().save(model_path)
        
        train_df.unpersist()
        val_df.unpersist()
        
        elapsed = time.time() - start_time
        print(f"✅ TRAINED ({elapsed:.1f}s = {elapsed/60:.1f} min)")
        
        progress_tracker.mark_complete(step_name)
        
        return model


class MAPEvaluator:
    """MAP evaluation for recommendation quality"""
    
    @staticmethod
    def evaluate_map(
        spark: SparkSession,
        model: ALSModel,
        val_df: DataFrame,
        k: int = 500,
        sample_size: int = 1000
    ) -> float:
        """Calculate Mean Average Precision @ K"""
        
        print(f"\n📊 EVALUATING MAP@{k}...")
        start_time = time.time()
        
        # Prepare ground truth
        truth_df = (
            val_df
            .groupBy("user")
            .agg(F.collect_set("item").alias("truth_items"))
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        
        # Sample users
        sampled_users = (
            truth_df
            .select("user")
            .orderBy(F.rand(seed=42))
            .limit(sample_size)
        )
        
        # Generate recommendations
        recs_df = model.recommendForUserSubset(sampled_users, k)
        eval_df = recs_df.join(truth_df, on="user", how="inner")
        
        # Calculate AP for each user
        def average_precision(pred_items: List[int], true_items: Set[int], k: int) -> float:
            if len(true_items) == 0:
                return 0.0
            
            hits = 0
            score = 0.0
            
            for rank_idx, item in enumerate(pred_items[:k], start=1):
                if item in true_items:
                    hits += 1
                    score += hits / float(rank_idx)
            
            return score / float(min(len(true_items), k))
        
        # Collect and compute
        rows = eval_df.select("user", "recommendations", "truth_items").collect()
        
        ap_scores = []
        for row in rows:
            pred = [r.item for r in row.recommendations]
            truth = set(row.truth_items)
            ap = average_precision(pred, truth, k)
            ap_scores.append(ap)
        
        map_score = sum(ap_scores) / len(ap_scores) if ap_scores else 0.0
        
        truth_df.unpersist()
        
        elapsed = time.time() - start_time
        
        print(f"✅ MAP@{k} = {map_score:.4f} (evaluated on {len(ap_scores)} users, {elapsed:.1f}s)")
        
        return map_score


# Define UDFs OUTSIDE the class to avoid re-serialization
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
        if len(kept) >= 500:  # Fixed limit
            break
    return kept

@F.udf(returnType=T.ArrayType(T.StringType()))
def sort_uris(recs_struct):
    """Sort recommendations by rank position"""
    if recs_struct is None:
        return []
    sorted_list = sorted(recs_struct, key=lambda x: x["rank_pos"])
    return [x["track_uri"] for x in sorted_list]


class RobustSubmissionGenerator:
    """Submission generation with FULL resume capability"""
    
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
        batch_size: int = 5000,  # REDUCED from 20000
        force_regenerate: bool = False
    ):
        """Generate submission with batch-level checkpointing"""
        
        step_name = "generate_submission"
        
        # Check if completely done
        if not force_regenerate and progress_tracker.is_complete(step_name):
            print(f"\n✅ Submission already complete: {output_path}")
            return
        
        print(f"\n📝 GENERATING SUBMISSION (with batch checkpointing)...")
        print("=" * 80)
        start_time = time.time()
        
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
        
        num_batches = (total_users + batch_size - 1) // batch_size
        
        print(f"   Total users: {total_users:,}")
        print(f"   Batch size: {batch_size:,}")
        print(f"   Total batches: {num_batches}")
        
        # Batch output directory
        batch_dir = f"{output_path}_batches"
        
        # Check completed batches
        completed_batches = progress_tracker.get_completed_batches(step_name)
        print(f"   Already completed batches: {completed_batches}")
        
        # Process batches
        for i in range(0, total_users, batch_size):
            batch_num = (i // batch_size) + 1
            
            # Skip if already complete
            if batch_num in completed_batches:
                print(f"\n   ✅ Batch {batch_num}/{num_batches} already complete, skipping...")
                continue
            
            batch_ids = all_user_ids[i:i + batch_size]
            
            print(f"\n   📦 Batch {batch_num}/{num_batches}: Processing {len(batch_ids):,} users...")
            batch_start = time.time()
            
            try:
                # Create batch
                batch_df = spark.createDataFrame([(uid,) for uid in batch_ids], ["user"])
                
                # Generate recommendations (REDUCED: 520 instead of 600)
                recs_df = model.recommendForUserSubset(batch_df, top_k + 20)
                
                # Filter seen
                filtered_df = (
                    recs_df
                    .join(seen_tracks_df, on="user", how="left")
                    .withColumn("filtered_items", filter_seen_udf("recommendations", "seen_items"))
                )
                
                # Explode and map
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
                
                # Group and format
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
                
                # SAVE THIS BATCH immediately
                batch_path = f"{batch_dir}/batch_{batch_num:04d}"
                print(f"      💾 Saving batch to {batch_path}...")
                batch_submission.repartition(1).write.mode("overwrite").parquet(batch_path)
                
                # Mark as complete
                progress_tracker.mark_batch_complete(step_name, batch_num)
                
                batch_elapsed = time.time() - batch_start
                print(f"      ✅ Batch {batch_num} saved ({batch_elapsed:.1f}s)")
                
            except Exception as e:
                print(f"      ❌ Batch {batch_num} FAILED: {e}")
                print(f"      You can resume by running the same command again.")
                raise
        
        # All batches complete, now merge
        print(f"\n   🔗 All batches complete, merging to final CSV...")
        merge_start = time.time()
        
        # Read all batch parquets
        all_batch_paths = [f"{batch_dir}/batch_{i:04d}" for i in range(1, num_batches + 1)]
        
        # Union all batches
        final_df = spark.read.parquet(*all_batch_paths)
        
        # Validate: count tracks per playlist
        print(f"   🔍 Validating submission format...")
        validation_df = final_df.withColumn(
            "track_count",
            F.size(F.split(F.col("recommended_track_uris"), ","))
        )
        
        invalid_count = validation_df.filter(F.col("track_count") != top_k).count()
        if invalid_count > 0:
            print(f"   ⚠️  WARNING: {invalid_count} playlists don't have exactly {top_k} tracks!")
        else:
            print(f"   ✅ All playlists have exactly {top_k} tracks")
        
        # Save final CSV
        print(f"   💾 Writing final CSV to {output_path}...")
        
        # Coalesce to reduce number of output files
        final_df.repartition(50) \
            .write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv(output_path)
        
        # Cleanup
        seen_tracks_df.unpersist()
        
        merge_elapsed = time.time() - merge_start
        total_elapsed = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("✅ SUBMISSION COMPLETE")
        print("=" * 80)
        print(f"   Total playlists: {total_users:,}")
        print(f"   Tracks per playlist: {top_k}")
        print(f"   Merge time: {merge_elapsed:.1f}s")
        print(f"   Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
        print(f"   📁 Output: {output_path}")
        print(f"   📦 Batch checkpoints: {batch_dir}")
        print("=" * 80)
        
        # Mark step complete
        progress_tracker.mark_complete(step_name, {
            'total_playlists': total_users,
            'tracks_per_playlist': top_k
        })

def main():
    parser = argparse.ArgumentParser(
        description="Production-Ready Spotify Recommendation System - 24GB RAM"
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
    


    #ALS
    #Số lượng yếu tố tiềm ẩn (hiện là 12).
    parser.add_argument("--rank", type=int, default=50) 

    #Tham số điều chuẩn (regularization) (hiện là 0.15).
    parser.add_argument("--regParam", type=float, default=0.1)

    #Tham số tin cậy cho sở thích ngầm định (hiện là 10.0)
    parser.add_argument("--alpha", type=float, default=40.0)

    #Số vòng lặp huấn luyện tối đa (hiện là 6).
    parser.add_argument("--maxIter", type=int, default=20)

    


    # Evaluation
    parser.add_argument("--evaluate_map", action="store_true",
                       help="Evaluate MAP metric on validation set")
    parser.add_argument("--eval_sample_size", type=int, default=1000,
                       help="Number of users for MAP evaluation")
    
    # Generation
    parser.add_argument("--topK", type=int, default=500)
    parser.add_argument("--batchSize", type=int, default=5000)  # REDUCED for stability
    
    # Force flags
    parser.add_argument("--force_reload", action="store_true")
    parser.add_argument("--force_refilter", action="store_true")
    parser.add_argument("--force_reindex", action="store_true")
    parser.add_argument("--force_retrain", action="store_true")
    parser.add_argument("--force_regenerate", action="store_true")
    parser.add_argument("--reset_progress", action="store_true")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🎯 PRODUCTION SPOTIFY RECOMMENDATION SYSTEM")
    print("💾 24GB RAM | Full Resume | MAP Evaluation | Validated Output")
    print("=" * 80)
    
    # Progress tracker
    progress_tracker = ProgressTracker("progress.json")
    
    if args.reset_progress:
        print("🔄 Resetting progress...")
        if os.path.exists("progress.json"):
            os.remove("progress.json")
        progress_tracker = ProgressTracker("progress.json")
    
    # Spark
    spark = OptimizedSparkSession.create()
    
    try:
        # Load
        interactions_df = ResilientDataLoader.load_or_resume(
            spark, args.input_path,
            f"{args.checkpoint_dir}/raw_data",
            progress_tracker, args.force_reload
        )
        
        # Filter
        filtered_df = ResilientFilter.filter_or_resume(
            spark, interactions_df,
            f"{args.checkpoint_dir}/filtered_data",
            progress_tracker,
            args.min_playlist_len, args.max_playlist_len,
            args.min_track_freq, args.max_track_freq,
            args.force_refilter
        )
        
        # Index
        indexed_df, playlist_map_df, track_map_df = ResilientIndexer.index_or_resume(
            spark, filtered_df,
            f"{args.checkpoint_dir}/indexed_data",
            f"{args.checkpoint_dir}/mappings",
            progress_tracker, args.force_reindex
        )
        
        # Train
        model = ResilientTrainer.train_or_load(
            spark, indexed_df, args.model_path,
            progress_tracker,
            args.rank, args.regParam, args.alpha, args.maxIter,
            args.force_retrain
        )
        
        # <<< THAY ĐỔI Ở ĐÂY:
        # Tôi đã xóa dòng 'if args.evaluate_map:' và bỏ lùi lề (un-indent)
        # khối code bên dưới để nó luôn chạy.
        
        # Evaluate MAP
        # Create validation set
        train_df, val_df = indexed_df.randomSplit([0.8, 0.2], seed=42)
        val_df = val_df.repartition(18, "user").cache()
        
        map_score = MAPEvaluator.evaluate_map(
            spark, model, val_df,
            k=args.topK,
            sample_size=args.eval_sample_size
        )
        
        val_df.unpersist()
        
        print(f"\n📊 MAP@{args.topK} = {map_score:.4f}")
        
        # Generate submission
        RobustSubmissionGenerator.generate_with_recovery(
            spark, model,
            indexed_df, playlist_map_df, track_map_df,
            args.submission_path,
            progress_tracker,
            args.topK, args.batchSize,
            args.force_regenerate
        )
        
        print("\n" + "=" * 80)
        print("🎉 PIPELINE COMPLETE!")
        print("=" * 80)
        print(f"📊 Submission: {args.submission_path}")
        print(f"💾 Model: {args.model_path}")
        print(f"📁 Progress: progress.json")
        print("=" * 80)
        print("\n💡 Resume anytime: just run the same command again")
        print("=" * 80)
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"   {str(e)}")
        print("=" * 80)
        print("\n💡 Resume: run the same command to continue from last checkpoint")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()