#!/bin/bash
# Quick run script with optimized presets for different RAM configurations

SCRIPT_PATH="/tmp/v1_ultimate.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    print_error "Script not found at $SCRIPT_PATH"
    print_warning "Please copy v1_ultimate.py to container first:"
    echo "docker cp v1_ultimate.py gui-docker-spark-worker-1:/tmp/"
    exit 1
fi

# Function to run spark-submit
run_spark() {
    local preset_name=$1
    shift
    
    print_header "Running preset: $preset_name"
    
    docker exec gui-docker-spark-worker-1 \
        /spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        $SCRIPT_PATH \
        "$@"
    
    if [ $? -eq 0 ]; then
        print_success "Preset '$preset_name' completed successfully!"
    else
        print_error "Preset '$preset_name' failed!"
        exit 1
    fi
}

# Main menu
echo ""
print_header "SPOTIFY ALS RECOMMENDATION PRESETS"
echo ""
echo "Choose a preset based on your available RAM:"
echo ""
echo "  1) ULTRA-SAFE (4-8GB RAM)"
echo "     - Smallest data, fastest, lowest accuracy"
echo "     - Expected MAP@500: 0.10-0.12"
echo "     - Time: ~20-30 min"
echo ""
echo "  2) CONSERVATIVE (8-16GB RAM) ⭐ RECOMMENDED"
echo "     - Balanced data/accuracy"
echo "     - Expected MAP@500: 0.14-0.16"
echo "     - Time: ~30-45 min"
echo ""
echo "  3) BALANCED (16-24GB RAM)"
echo "     - Good data coverage"
echo "     - Expected MAP@500: 0.16-0.18"
echo "     - Time: ~45-60 min"
echo ""
echo "  4) AGGRESSIVE (24GB+ RAM)"
echo "     - Maximum data"
echo "     - Expected MAP@500: 0.18-0.20"
echo "     - Time: ~60-90 min"
echo ""
echo "  5) CUSTOM (enter your own parameters)"
echo ""
echo "  6) DRY RUN (test filtering only, no training)"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        print_header "ULTRA-SAFE PRESET (4-8GB RAM)"
        run_spark "ULTRA-SAFE" \
            --min_playlist_len 25 \
            --max_playlist_len 100 \
            --min_track_freq 200 \
            --sample_playlists 0.4 \
            --rank 10 \
            --regParam 0.2 \
            --alpha 8.0 \
            --maxIter 4 \
            --numUserBlocks 200 \
            --numItemBlocks 200 \
            --evalSample 500 \
            --batchSize 20000
        ;;
    
    2)
        print_header "CONSERVATIVE PRESET (8-16GB RAM) ⭐"
        run_spark "CONSERVATIVE" \
            --min_playlist_len 20 \
            --max_playlist_len 150 \
            --min_track_freq 150 \
            --rank 15 \
            --regParam 0.15 \
            --alpha 10.0 \
            --maxIter 5 \
            --numUserBlocks 300 \
            --numItemBlocks 300 \
            --evalSample 1000 \
            --batchSize 30000
        ;;
    
    3)
        print_header "BALANCED PRESET (16-24GB RAM)"
        run_spark "BALANCED" \
            --min_playlist_len 15 \
            --max_playlist_len 200 \
            --min_track_freq 100 \
            --rank 20 \
            --regParam 0.12 \
            --alpha 12.0 \
            --maxIter 6 \
            --numUserBlocks 350 \
            --numItemBlocks 350 \
            --evalSample 1500 \
            --batchSize 40000
        ;;
    
    4)
        print_header "AGGRESSIVE PRESET (24GB+ RAM)"
        run_spark "AGGRESSIVE" \
            --min_playlist_len 10 \
            --max_playlist_len 250 \
            --min_track_freq 80 \
            --rank 25 \
            --regParam 0.1 \
            --alpha 15.0 \
            --maxIter 8 \
            --numUserBlocks 400 \
            --numItemBlocks 400 \
            --evalSample 2000 \
            --batchSize 50000
        ;;
    
    5)
        print_header "CUSTOM PARAMETERS"
        echo ""
        read -p "Min playlist length [15]: " min_pl
        min_pl=${min_pl:-15}
        
        read -p "Max playlist length [200]: " max_pl
        max_pl=${max_pl:-200}
        
        read -p "Min track frequency [100]: " min_tr
        min_tr=${min_tr:-100}
        
        read -p "Sample playlists (0.1-1.0, empty=no sample): " sample
        sample_arg=""
        if [ ! -z "$sample" ]; then
            sample_arg="--sample_playlists $sample"
        fi
        
        read -p "Rank (latent factors) [15]: " rank
        rank=${rank:-15}
        
        read -p "Max iterations [6]: " maxiter
        maxiter=${maxiter:-6}
        
        read -p "Alpha [10.0]: " alpha
        alpha=${alpha:-10.0}
        
        run_spark "CUSTOM" \
            --min_playlist_len $min_pl \
            --max_playlist_len $max_pl \
            --min_track_freq $min_tr \
            $sample_arg \
            --rank $rank \
            --alpha $alpha \
            --maxIter $maxiter
        ;;
    
    6)
        print_header "DRY RUN (Filtering Test)"
        print_warning "This will only run filtering and indexing (no training)"
        echo ""
        read -p "Min playlist length [15]: " min_pl
        min_pl=${min_pl:-15}
        
        read -p "Max playlist length [200]: " max_pl
        max_pl=${max_pl:-200}
        
        read -p "Min track frequency [100]: " min_tr
        min_tr=${min_tr:-100}
        
        # Create a simple test script that exits after filtering
        docker exec gui-docker-spark-worker-1 bash -c "cat > /tmp/dry_run.py << 'EOF'
import sys
sys.path.insert(0, '/tmp')
from v1_ultimate import *

spark = MemoryOptimizedSparkSession.create()
interactions_df = DataLoader.load_playlists(spark, 'hdfs://namenode:8020/input/data/')
filtered_df = IntelligentFilter.filter_intelligently(
    interactions_df,
    min_playlist_len=$min_pl,
    max_playlist_len=$max_pl,
    min_track_freq=$min_tr,
    max_track_freq=None,
    sample_playlists=None,
    remove_popular_bias=False
)
print('\\n✅ Dry run completed - data would be processable!')
spark.stop()
EOF"
        
        docker exec gui-docker-spark-worker-1 \
            /spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            /tmp/dry_run.py
        ;;
    
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
print_success "Script completed!"
echo ""
echo "📊 Check results at:"
echo "   - Submission: hdfs://namenode:8020/output/submission_ultimate/"
echo "   - Model: hdfs://namenode:8020/output/model/als_model_ultimate/"
echo ""
