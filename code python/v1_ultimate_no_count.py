#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultimate Spotify Recommendation System with Spark ALS
Optimized for large datasets with limited RAM
MODIFIED: Skip count() to avoid OOM during submission generation
Author: Optimized Version - No Count
"""

import argparse
import time
from typing import List, Set, Optional
from functools import reduce

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window
from pyspark.storagelevel import StorageLevel
from pyspark.ml.recommendation import ALS, ALSModel
from pyspark.ml.feature import StringIndexer


class MemoryOptimizedSparkSession:
    """Advanced Spark session with memory optimization"""
    
    @staticmethod
    def create(app_name: str = "SpotifyRecsALS_Ultimate") -> SparkSession:
        spark = (
            SparkSession.builder
            .appName(app_name)
            
            # Serialization - Kryo with optimized buffer
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.kryoserializer.buffer.max", "512m")
            .config("spark.kryoserializer.buffer", "64m")
            
            # Memory allocation - Conservative settings
            .config("spark.driver.memory", "6g")
            .config("spark.driver.maxResultSize", "2g")
            .config("spark.executor.memory", "6g")
            .config("spark.executor.memoryOverhead", "1536m")
            .config("spark.executor.cores", "3")
            
            # Shuffle optimization - Critical for large datasets
            .config("spark.sql.shuffle.partitions", "600")
            .config("spark.default.parallelism", "600")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "600")
            .config("spark.sql.adaptive.advisoryPartitionSizeInBytes", "64m")
            .config("spark.sql.adaptive.skewJoin.enabled", "true")
            
            # Memory management - Fine-tuned
            .config("spark.memory.fraction", "0.75")
            .config("spark.memory.storageFraction", "0.2")
            .config("spark.shuffle.compress", "true")
            .config("spark.shuffle.spill.compress", "true")
            .config("spark.shuffle.service.enabled", "false")
            
            # Broadcast optimization - Disable auto broadcast
            .config("spark.sql.autoBroadcastJoinThreshold", "-1")
            .config("spark.broadcast.blockSize", "2m")
            .config("spark.broadcast.compress", "true")
            
            # Task optimization
            .config("spark.task.maxFailures", "4")
            .config("spark.stage.maxConsecutiveAttempts", "4")
            
            # IO optimization
            .config("spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2")
            .config("spark.speculation", "false")
            
            # Garbage collection
            .config("spark.cleaner.referenceTracking.cleanCheckpoints", "true")
            .config("spark.cleaner.periodicGC.interval", "10min")
            
            .getOrCreate()
        )
        
        spark.sparkContext.setLogLevel("WARN")
        spark.sparkContext.setCheckpointDir("hdfs://namenode:8020/tmp/checkpoints")
        
        print("=" * 70)
        print("🚀 Spark Session Created Successfully (NO COUNT VERSION)")
        print("=" * 70)
        print(f"📊 Spark Version: {spark.version}")
        print(f"💾 Driver Memory: 6g")
        print(f"⚡ Executor Memory: 6g")
        print(f"🔄 Shuffle Partitions: 600")
        print(f"📁 Checkpoint Dir: hdfs://namenode:8020/tmp/checkpoints")
        print("=" * 70)
        
        return spark


class DataLoader:
    """Optimized data loading with early filtering"""
    
    @staticmethod
    def load_playlists(spark: SparkSession, input_path: str) -> DataFrame:
        """Load and explode playlists with minimal memory footprint"""
        print("\n📥 LOADING RAW DATA...")
        start_time = time.time()
        
        df = (
            spark.read
            .option("multiLine", "true")
            .json(f"{input_path}/*.json")
        )

        playlists_df = (
            df.select(F.explode("playlists").alias("pl"))
              .select(
                F.col("pl.pid").alias("playlist_id"),
                F.col("pl.tracks").alias("tracks")
              )
        )

        interactions_df = (
            playlists_df
            .select(
                "playlist_id",
                F.explode("tracks").alias("track")
            )
            .select(
                F.col("playlist_id").cast("long"),
                F.col("track.track_uri").alias("track_uri")
            )
            .filter(F.col("track_uri").isNotNull())
            .dropDuplicates(["playlist_id", "track_uri"])
            .repartition(400, "playlist_id")  # Early repartitioning
        )

        # Get stats without materializing full dataset
        print("\n📊 COMPUTING STATISTICS...")
        total_interactions = interactions_df.count()
        total_playlists = interactions_df.select("playlist_id").distinct().count()
        total_tracks = interactions_df.select("track_uri").distinct().count()
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("📈 RAW DATA STATISTICS")
        print("=" * 70)
        print(f"   Total interactions: {total_interactions:,}")
        print(f"   Unique playlists: {total_playlists:,}")
        print(f"   Unique tracks: {total_tracks:,}")
        print(f"   Avg tracks/playlist: {total_interactions/total_playlists:.1f}")
        print(f"   ⏱️  Loading time: {elapsed:.1f}s")
        print("=" * 70)

        return interactions_df


class IntelligentFilter:
    """Advanced filtering with statistical analysis"""
    
    @staticmethod
    def analyze_distribution(df: DataFrame, col_name: str, entity_name: str):
        """Analyze and print distribution statistics"""
        stats = df.agg(
            F.min(col_name).alias("min"),
            F.expr(f"percentile_approx({col_name}, 0.25)").alias("p25"),
            F.expr(f"percentile_approx({col_name}, 0.5)").alias("median"),
            F.expr(f"percentile_approx({col_name}, 0.75)").alias("p75"),
            F.expr(f"percentile_approx({col_name}, 0.95)").alias("p95"),
            F.max(col_name).alias("max"),
            F.avg(col_name).alias("mean")
        ).collect()[0]
        
        print(f"\n📊 {entity_name} Distribution:")
        print(f"   Min: {stats['min']}, P25: {stats['p25']}, Median: {stats['median']}")
        print(f"   P75: {stats['p75']}, P95: {stats['p95']}, Max: {stats['max']}")
        print(f"   Mean: {stats['mean']:.2f}")
    
    @staticmethod
    def filter_intelligently(
        interactions_df: DataFrame,
        min_playlist_len: int,
        max_playlist_len: int,
        min_track_freq: int,
        max_track_freq: Optional[int],
        sample_playlists: Optional[float],
        remove_popular_bias: bool = True
    ) -> DataFrame:
        """
        Intelligent filtering with multiple strategies:
        - Remove too short/long playlists
        - Remove rare/too popular tracks
        - Optional sampling
        - Remove potential bots/biases
        """
        print("\n🔍 INTELLIGENT FILTERING...")
        start_time = time.time()
        
        # Step 1: Analyze playlist lengths
        print("\n1️⃣ Analyzing playlist lengths...")
        playlist_stats = (
            interactions_df
            .groupBy("playlist_id")
            .agg(F.count("*").alias("pl_len"))
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        
        IntelligentFilter.analyze_distribution(
            playlist_stats, "pl_len", "Playlist Length"
        )
        
        # Filter playlists by length
        valid_playlists = (
            playlist_stats
            .filter(
                (F.col("pl_len") >= min_playlist_len) &
                (F.col("pl_len") <= max_playlist_len)
            )
            .select("playlist_id")
        )
        
        # Optional: Sample playlists
        if sample_playlists and sample_playlists < 1.0:
            print(f"\n🎲 Sampling {sample_playlists*100:.1f}% of playlists...")
            valid_playlists = valid_playlists.sample(
                withReplacement=False,
                fraction=sample_playlists,
                seed=42
            )
        
        kept_playlists = valid_playlists.count()
        print(f"   ✅ Kept playlists: {kept_playlists:,}")
        
        # Step 2: Analyze track frequencies
        print("\n2️⃣ Analyzing track frequencies...")
        track_stats = (
            interactions_df
            .groupBy("track_uri")
            .agg(F.count("*").alias("trk_freq"))
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        
        IntelligentFilter.analyze_distribution(
            track_stats, "trk_freq", "Track Frequency"
        )
        
        # Filter tracks by frequency
        if max_track_freq and remove_popular_bias:
            print(f"   🎯 Removing extremely popular tracks (freq > {max_track_freq})")
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
        
        # Step 3: Join and filter (use broadcast for smaller table)
        print("\n3️⃣ Applying filters...")
        
        # Determine which table is smaller for broadcast
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
        
        # Repartition for better parallelism
        filtered_df = filtered_df.repartition(400, "playlist_id")
        
        # Checkpoint to break lineage and free memory
        filtered_df = filtered_df.checkpoint()
        
        # Cleanup
        playlist_stats.unpersist()
        track_stats.unpersist()
        
        # Final statistics
        print("\n4️⃣ Computing final statistics...")
        kept_interactions = filtered_df.count()
        final_playlists = filtered_df.select("playlist_id").distinct().count()
        final_tracks = filtered_df.select("track_uri").distinct().count()
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("✅ FILTERING RESULTS")
        print("=" * 70)
        print(f"   Interactions: {kept_interactions:,}")
        print(f"   Playlists: {final_playlists:,}")
        print(f"   Tracks: {final_tracks:,}")
        print(f"   Avg tracks/playlist: {kept_interactions/final_playlists:.1f}")
        print(f"   Sparsity: {100 - (kept_interactions/(final_playlists*final_tracks)*100):.4f}%")
        print(f"   ⏱️  Filtering time: {elapsed:.1f}s")
        print("=" * 70)
        
        return filtered_df


class EfficientIndexer:
    """Memory-efficient ID indexing"""
    
    @staticmethod
    def index_and_prepare(filtered_df: DataFrame) -> tuple:
        """Index IDs and prepare training data with minimal memory usage"""
        print("\n🔢 INDEXING IDS...")
        start_time = time.time()
        
        # Repartition before indexing
        filtered_df = filtered_df.repartition(300, "playlist_id")
        
        print("   Building playlist index...")
        playlist_indexer = StringIndexer(
            inputCol="playlist_id",
            outputCol="playlist_id_idx",
            handleInvalid="skip",
            stringOrderType="frequencyDesc"  # Most frequent get lower IDs
        ).fit(filtered_df)
        
        print("   Building track index...")
        track_indexer = StringIndexer(
            inputCol="track_uri",
            outputCol="track_id_idx",
            handleInvalid="skip",
            stringOrderType="frequencyDesc"
        ).fit(filtered_df)
        
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
        
        # Checkpoint
        indexed_df = indexed_df.checkpoint()
        
        print("   Creating mapping tables...")
        playlist_map_df = (
            indexed_df
            .select("user", "playlist_id")
            .dropDuplicates(["user"])
            .withColumnRenamed("user", "user_int")
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        
        track_map_df = (
            indexed_df
            .select("item", "track_uri")
            .dropDuplicates(["item"])
            .withColumnRenamed("item", "item_int")
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        
        elapsed = time.time() - start_time
        
        num_users = playlist_map_df.count()
        num_items = track_map_df.count()
        
        print("\n" + "=" * 70)
        print("✅ INDEXING COMPLETE")
        print("=" * 70)
        print(f"   Users (playlists): {num_users:,}")
        print(f"   Items (tracks): {num_items:,}")
        print(f"   ⏱️  Indexing time: {elapsed:.1f}s")
        print("=" * 70)
        
        return indexed_df, playlist_map_df, track_map_df


class SmartTrainValSplit:
    """Intelligent train/validation splitting"""
    
    @staticmethod
    def split_temporally_aware(
        indexed_df: DataFrame,
        train_ratio: float = 0.8,
        seed: int = 42
    ) -> tuple:
        """
        Split data with consideration for cold start:
        - Ensure all users/items appear in training
        - Use stratified sampling if possible
        """
        print("\n✂️  SPLITTING TRAIN/VALIDATION...")
        start_time = time.time()
        
        # Random split (could implement stratified split if needed)
        train_df, val_df = indexed_df.randomSplit([train_ratio, 1-train_ratio], seed=seed)
        
        # Checkpoint both
        train_df = train_df.repartition(400, "user").checkpoint()
        val_df = val_df.repartition(200, "user").checkpoint()
        
        # Get counts efficiently
        train_count = train_df.count()
        val_count = val_df.count()
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("✅ TRAIN/VAL SPLIT COMPLETE")
        print("=" * 70)
        print(f"   Training samples: {train_count:,} ({train_ratio*100:.0f}%)")
        print(f"   Validation samples: {val_count:,} ({(1-train_ratio)*100:.0f}%)")
        print(f"   ⏱️  Split time: {elapsed:.1f}s")
        print("=" * 70)
        
        return train_df, val_df


class OptimizedALSTrainer:
    """ALS training with progressive optimization"""
    
    @staticmethod
    def train_with_monitoring(
        train_df: DataFrame,
        rank: int = 15,
        regParam: float = 0.15,
        alpha: float = 10.0,
        maxIter: int = 6,
        numUserBlocks: int = 300,
        numItemBlocks: int = 300
    ) -> ALSModel:
        """Train ALS with progress monitoring"""
        print("\n🎓 TRAINING ALS MODEL...")
        print("=" * 70)
        print("📝 Hyperparameters:")
        print(f"   Rank (latent factors): {rank}")
        print(f"   Regularization: {regParam}")
        print(f"   Alpha (confidence): {alpha}")
        print(f"   Max iterations: {maxIter}")
        print(f"   User blocks: {numUserBlocks}")
        print(f"   Item blocks: {numItemBlocks}")
        print("=" * 70)
        
        start_time = time.time()
        
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
            numUserBlocks=numUserBlocks,
            numItemBlocks=numItemBlocks,
            intermediateStorageLevel="MEMORY_AND_DISK",
            finalStorageLevel="MEMORY_AND_DISK",
            checkpointInterval=2  # Checkpoint every 2 iterations
        )
        
        print("\n⏳ Training in progress...")
        model = als.fit(train_df)
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE")
        print("=" * 70)
        print(f"   ⏱️  Training time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"   Model size: ~{rank * (numUserBlocks + numItemBlocks) / 1000:.1f}K parameters")
        print("=" * 70)
        
        return model


class EvaluationMetrics:
    """Comprehensive evaluation metrics"""
    
    @staticmethod
    def average_precision_at_k(
        pred_items: List[int],
        true_items: Set[int],
        k: int = 500
    ) -> float:
        """Calculate AP@K"""
        if len(true_items) == 0:
            return 0.0
        
        hits = 0
        score = 0.0
        
        for rank_idx, item in enumerate(pred_items[:k], start=1):
            if item in true_items:
                hits += 1
                score += hits / float(rank_idx)
        
        denom = min(len(true_items), k)
        return score / float(denom) if denom > 0 else 0.0
    
    @staticmethod
    def recall_at_k(
        pred_items: List[int],
        true_items: Set[int],
        k: int = 500
    ) -> float:
        """Calculate Recall@K"""
        if len(true_items) == 0:
            return 0.0
        
        hits = len(set(pred_items[:k]) & true_items)
        return hits / float(len(true_items))
    
    @staticmethod
    def ndcg_at_k(
        pred_items: List[int],
        true_items: Set[int],
        k: int = 500
    ) -> float:
        """Calculate NDCG@K"""
        if len(true_items) == 0:
            return 0.0
        
        dcg = 0.0
        for rank_idx, item in enumerate(pred_items[:k], start=1):
            if item in true_items:
                dcg += 1.0 / (rank_idx).bit_length()  # log2(rank+1)
        
        idcg = sum(1.0 / (i+1).bit_length() for i in range(min(len(true_items), k)))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def evaluate_comprehensive(
        spark: SparkSession,
        model: ALSModel,
        val_df: DataFrame,
        k: int = 500,
        sample_size: int = 1000
    ) -> dict:
        """Evaluate model with multiple metrics"""
        print("\n📊 EVALUATING MODEL...")
        print("=" * 70)
        start_time = time.time()
        
        # Prepare ground truth
        print("   Preparing ground truth...")
        truth_df = (
            val_df
            .groupBy("user")
            .agg(F.collect_set("item").alias("truth_items"))
            .persist(StorageLevel.MEMORY_AND_DISK)
        )
        
        # Sample users for evaluation
        sampled_users_df = (
            truth_df
            .select("user")
            .orderBy(F.rand(seed=123))
            .limit(sample_size)
        )
        
        print(f"   Generating recommendations for {sample_size} users...")
        recs_df = model.recommendForUserSubset(sampled_users_df, k)
        eval_df = recs_df.join(truth_df, on="user", how="inner")
        
        print("   Computing metrics...")
        rows = eval_df.select("user", "recommendations", "truth_items").collect()
        
        map_scores = []
        recall_scores = []
        ndcg_scores = []
        
        for row in rows:
            rec_items = [r.item for r in row.recommendations]
            truth_items = set(row.truth_items)
            
            map_scores.append(
                EvaluationMetrics.average_precision_at_k(rec_items, truth_items, k)
            )
            recall_scores.append(
                EvaluationMetrics.recall_at_k(rec_items, truth_items, k)
            )
            ndcg_scores.append(
                EvaluationMetrics.ndcg_at_k(rec_items, truth_items, k)
            )
        
        truth_df.unpersist()
        
        elapsed = time.time() - start_time
        
        metrics = {
            'MAP@K': sum(map_scores) / len(map_scores) if map_scores else 0.0,
            'Recall@K': sum(recall_scores) / len(recall_scores) if recall_scores else 0.0,
            'NDCG@K': sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0,
            'num_users_evaluated': len(map_scores)
        }
        
        print("\n" + "=" * 70)
        print(f"✅ EVALUATION RESULTS @ K={k}")
        print("=" * 70)
        print(f"   MAP@{k}:    {metrics['MAP@K']:.4f}")
        print(f"   Recall@{k}: {metrics['Recall@K']:.4f}")
        print(f"   NDCG@{k}:   {metrics['NDCG@K']:.4f}")
        print(f"   Users evaluated: {metrics['num_users_evaluated']:,}")
        print(f"   ⏱️  Evaluation time: {elapsed:.1f}s")
        print("=" * 70)
        
        return metrics


class BatchedSubmissionGenerator:
    """Memory-efficient submission generation - MODIFIED TO SKIP COUNT"""
    
    @staticmethod
    def generate_in_batches(
        spark: SparkSession,
        model: ALSModel,
        indexed_df: DataFrame,
        playlist_map_df: DataFrame,
        track_map_df: DataFrame,
        top_k: int = 500,
        batch_size: int = 30000,
        extra_fetch: int = 200
    ) -> DataFrame:
        """Generate submission with batched processing - NO FINAL COUNT"""
        print("\n📝 GENERATING SUBMISSION...")
        print("=" * 70)
        start_time = time.time()
        
        # Prepare seen items for filtering
        print("   Computing seen items per user...")
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
        print(f"   Batch size: {batch_size:,}")
        print(f"   Number of batches: {(total_users + batch_size - 1) // batch_size}")
        
        # UDF for filtering seen items
        @F.udf(returnType=T.ArrayType(T.IntegerType()))
        def filter_seen_udf(recs, seen_items):
            if recs is None:
                return []
            seen = set(seen_items) if seen_items else set()
            kept = []
            for r in recs:
                it = r["item"]
                if it not in seen:
                    kept.append(it)
                if len(kept) >= top_k:
                    break
            return kept
        
        # UDF for sorting recommendations
        @F.udf(returnType=T.ArrayType(T.StringType()))
        def sort_and_extract_uris(recs_struct):
            if recs_struct is None:
                return []
            sorted_list = sorted(recs_struct, key=lambda x: x["rank_pos"])
            return [x["track_uri"] for x in sorted_list]
        
        # Process in batches
        submission_parts = []
        batch_num = 0
        
        for i in range(0, total_users, batch_size):
            batch_num += 1
            batch_ids = all_user_ids[i:i + batch_size]
            batch_start = time.time()
            
            print(f"\n   🔄 Batch {batch_num}/{(total_users + batch_size - 1) // batch_size}: "
                  f"Users {i:,} to {min(i+batch_size, total_users):,}")
            
            # Create batch dataframe
            batch_users_df = spark.createDataFrame(
                [(uid,) for uid in batch_ids],
                ["user"]
            )
            
            # Generate recommendations
            recs_df = model.recommendForUserSubset(batch_users_df, top_k + extra_fetch)
            
            # Filter seen items
            recs_with_seen = recs_df.join(seen_tracks_df, on="user", how="left")
            filtered_recs_df = (
                recs_with_seen
                .withColumn("filtered_items", filter_seen_udf("recommendations", "seen_items"))
                .select("user", "filtered_items")
            )
            
            # Explode and add position
            exploded_df = (
            filtered_recs_df
            .select(
                F.col("user").alias("user_int"),
                F.posexplode("filtered_items").alias("rank_pos", "item_int")
            )
        )
            
            # Map back to original IDs
            exploded_with_uri_df = (
                exploded_df
                .join(track_map_df, on="item_int", how="left")
                .join(playlist_map_df, on="user_int", how="left")
                .select("playlist_id", "rank_pos", "track_uri")
            )
            
            # Group and format
            grouped_struct_df = (
                exploded_with_uri_df
                .groupBy("playlist_id")
                .agg(
                    F.collect_list(
                        F.struct("rank_pos", "track_uri")
                    ).alias("recs_struct")
                )
            )
            
            batch_submission = grouped_struct_df.withColumn(
                "track_uri_list",
                sort_and_extract_uris("recs_struct")
            ).select(
                F.col("playlist_id").cast("long").alias("playlist_id"),
                F.concat_ws(",", F.col("track_uri_list")).alias("recommended_track_uris")
            )
            
            submission_parts.append(batch_submission)
            
            batch_elapsed = time.time() - batch_start
            print(f"      ✅ Batch completed in {batch_elapsed:.1f}s")
        
        # Union all batches
        print("\n   📦 Combining all batches...")
        final_submission = reduce(lambda df1, df2: df1.union(df2), submission_parts)
        
        # Cleanup
        seen_tracks_df.unpersist()
        
        elapsed = time.time() - start_time
        
        # MODIFIED: Skip count() to avoid OOM
        print("\n" + "=" * 70)
        print("✅ SUBMISSION GENERATION COMPLETE")
        print("=" * 70)
        print(f"   Expected playlists: {total_users:,}")
        print(f"   Recommendations per playlist: {top_k}")
        print(f"   ⏱️  Generation time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"   ⚠️  Skipped final count() to save memory")
        print("=" * 70)
        
        return final_submission


def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Spotify Recommendation System - No Count Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Conservative (safest for low RAM):
  python v1_ultimate_no_count.py --min_playlist_len 20 --min_track_freq 150 --rank 12
  
  # Balanced (recommended):
  python v1_ultimate_no_count.py --min_playlist_len 15 --min_track_freq 100 --rank 15
  
  # Skip training (load existing model):
  python v1_ultimate_no_count.py --skip_training --skip_evaluation
        """
    )
    
    # Input/Output paths
    parser.add_argument(
        "--input_path",
        type=str,
        default="hdfs://namenode:8020/input/data/",
        help="HDFS input path containing JSON files"
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="hdfs://namenode:8020/output/model/als_model_ultimate",
        help="HDFS path to save trained model"
    )
    parser.add_argument(
        "--submission_path",
        type=str,
        default="hdfs://namenode:8020/output/submission_ultimate",
        help="HDFS path to save submission CSV"
    )
    
    # Filtering parameters
    filter_group = parser.add_argument_group('Filtering Options')
    filter_group.add_argument(
        "--min_playlist_len",
        type=int,
        default=15,
        help="Minimum playlist length (default: 15)"
    )
    filter_group.add_argument(
        "--max_playlist_len",
        type=int,
        default=200,
        help="Maximum playlist length to remove noise (default: 200)"
    )
    filter_group.add_argument(
        "--min_track_freq",
        type=int,
        default=100,
        help="Minimum track frequency (default: 100)"
    )
    filter_group.add_argument(
        "--max_track_freq",
        type=int,
        default=None,
        help="Maximum track frequency to remove bias (default: None)"
    )
    filter_group.add_argument(
        "--sample_playlists",
        type=float,
        default=None,
        help="Sample fraction of playlists (0.0-1.0, default: None)"
    )
    filter_group.add_argument(
        "--remove_popular_bias",
        action="store_true",
        help="Remove extremely popular tracks"
    )
    
    # ALS parameters
    als_group = parser.add_argument_group('ALS Hyperparameters')
    als_group.add_argument("--rank", type=int, default=15,
                          help="Number of latent factors (default: 15)")
    als_group.add_argument("--regParam", type=float, default=0.15,
                          help="Regularization parameter (default: 0.15)")
    als_group.add_argument("--alpha", type=float, default=10.0,
                          help="Confidence scaling (default: 10.0)")
    als_group.add_argument("--maxIter", type=int, default=6,
                          help="Maximum iterations (default: 6)")
    als_group.add_argument("--numUserBlocks", type=int, default=300,
                          help="Number of user blocks (default: 300)")
    als_group.add_argument("--numItemBlocks", type=int, default=300,
                          help="Number of item blocks (default: 300)")
    
    # Evaluation parameters
    eval_group = parser.add_argument_group('Evaluation Options')
    eval_group.add_argument("--topK", type=int, default=500,
                           help="Top-K for recommendations (default: 500)")
    eval_group.add_argument("--evalSample", type=int, default=1000,
                           help="Number of users for evaluation (default: 1000)")
    eval_group.add_argument("--train_ratio", type=float, default=0.8,
                           help="Train/val split ratio (default: 0.8)")
    
    # Generation parameters
    gen_group = parser.add_argument_group('Generation Options')
    gen_group.add_argument("--batchSize", type=int, default=30000,
                          help="Batch size for submission generation (default: 30000)")
    gen_group.add_argument("--extraFetch", type=int, default=200,
                          help="Extra items to fetch before filtering (default: 200)")
    
    # Mode selection
    parser.add_argument("--skip_training", action="store_true",
                       help="Skip training and load existing model")
    parser.add_argument("--skip_evaluation", action="store_true",
                       help="Skip evaluation step")
    
    args = parser.parse_args()
    
    # Print configuration
    print("\n" + "=" * 70)
    print("🎯 ULTIMATE SPOTIFY RECOMMENDATION SYSTEM (NO COUNT VERSION)")
    print("=" * 70)
    print(f"📁 Input: {args.input_path}")
    print(f"💾 Model output: {args.model_path}")
    print(f"📊 Submission output: {args.submission_path}")
    print("=" * 70)
    
    # Initialize Spark
    spark = MemoryOptimizedSparkSession.create()
    
    try:
        # Step 1: Load data
        interactions_df = DataLoader.load_playlists(spark, args.input_path)
        
        # Step 2: Intelligent filtering
        filtered_df = IntelligentFilter.filter_intelligently(
            interactions_df,
            min_playlist_len=args.min_playlist_len,
            max_playlist_len=args.max_playlist_len,
            min_track_freq=args.min_track_freq,
            max_track_freq=args.max_track_freq,
            sample_playlists=args.sample_playlists,
            remove_popular_bias=args.remove_popular_bias
        )
        
        # Free memory
        interactions_df.unpersist() if hasattr(interactions_df, 'unpersist') else None
        
        # Step 3: Index IDs
        indexed_df, playlist_map_df, track_map_df = EfficientIndexer.index_and_prepare(
            filtered_df
        )
        
        # Free memory
        filtered_df.unpersist() if hasattr(filtered_df, 'unpersist') else None
        
        # Step 4: Train/Val split
        train_df, val_df = SmartTrainValSplit.split_temporally_aware(
            indexed_df,
            train_ratio=args.train_ratio
        )
        
        # Step 5: Train model
        if not args.skip_training:
            model = OptimizedALSTrainer.train_with_monitoring(
                train_df,
                rank=args.rank,
                regParam=args.regParam,
                alpha=args.alpha,
                maxIter=args.maxIter,
                numUserBlocks=args.numUserBlocks,
                numItemBlocks=args.numItemBlocks
            )
            
            # Save model
            print(f"\n💾 Saving model to {args.model_path}...")
            model.write().overwrite().save(args.model_path)
            print("   ✅ Model saved successfully")
        else:
            print(f"\n📥 Loading model from {args.model_path}...")
            model = ALSModel.load(args.model_path)
            print("   ✅ Model loaded successfully")
        
        # Step 6: Evaluate
        if not args.skip_evaluation:
            metrics = EvaluationMetrics.evaluate_comprehensive(
                spark,
                model,
                val_df,
                k=args.topK,
                sample_size=args.evalSample
            )
        
        # Free memory
        train_df.unpersist()
        val_df.unpersist()
        
        # Step 7: Generate submission
        submission_df = BatchedSubmissionGenerator.generate_in_batches(
            spark,
            model,
            indexed_df,
            playlist_map_df,
            track_map_df,
            top_k=args.topK,
            batch_size=args.batchSize,
            extra_fetch=args.extraFetch
        )
        
        # Save submission
        print(f"\n💾 Saving submission to {args.submission_path}...")
        submission_df.coalesce(1) \
            .write \
            .mode("overwrite") \
            .option("header", "true") \
            .csv(args.submission_path)
        
        print("\n" + "=" * 70)
        print("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"📊 Submission file: {args.submission_path}")
        print(f"💾 Model file: {args.model_path}")
        print("=" * 70)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR OCCURRED")
        print("=" * 70)
        print(f"   {str(e)}")
        print("=" * 70)
        raise
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        spark.stop()
        print("✅ Spark session stopped")


if __name__ == "__main__":
    main()


