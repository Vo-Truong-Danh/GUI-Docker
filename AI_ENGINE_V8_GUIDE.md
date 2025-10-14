# 🚀 Advanced AI Engine V8.0 - Complete Guide

**Version:** 8.0.0  
**Date:** October 14, 2025  
**Status:** ✅ Production Ready

---

## 🎯 Điểm Mới Trong V8.0

### ✨ Tính năng mới

1. **Multi-Model Support**
   - OpenAI GPT-4, GPT-4-Turbo, GPT-4o, GPT-3.5
   - Anthropic Claude 3 (Opus, Sonnet, Haiku)
   - Google Gemini 2.5 (Flash, Pro), Gemini 1.5 (Flash, Pro)
   - Hỗ trợ local models (Ollama)

2. **Smart Fallback System**
   - Tự động chuyển sang model khác khi lỗi
   - Configurable fallback chain
   - Zero downtime

3. **Cost Tracking & Budgets**
   - Track chi phí theo ngày
   - Daily budget limits
   - Cost per request
   - Detailed cost analytics

4. **Quality Scoring**
   - Tự động đánh giá chất lượng câu trả lời
   - Minimum quality threshold
   - Multiple scoring criteria

5. **Rate Limiting**
   - Per-provider rate limits
   - Sliding window algorithm
   - Auto-throttling

6. **Enhanced Caching**
   - Smart TTL (Time To Live)
   - LRU eviction
   - Cache hit statistics

---

## 📦 Installation

### 1. Cài đặt dependencies

```bash
# Core requirements
pip install asyncio

# Optional - AI Providers (install theo nhu cầu)
pip install openai>=1.0.0                    # OpenAI
pip install anthropic>=0.7.0                 # Claude
pip install google-generativeai>=0.3.0      # Gemini
```

### 2. Set API Keys

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-openai-key"
$env:ANTHROPIC_API_KEY="your-anthropic-key"
$env:GOOGLE_API_KEY="your-google-key"

# Linux/Mac
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
```

---

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from advanced_ai_engine_v8 import (
    AdvancedAIEngine, AIConfig, AIProvider
)

async def basic_example():
    # 1. Tạo config
    config = AIConfig(
        provider=AIProvider.GOOGLE_GEMINI_25_FLASH,  # Free & fast
        cache_enabled=True,
        daily_budget=5.0
    )
    
    # 2. Khởi tạo engine
    engine = AdvancedAIEngine(config)
    
    # 3. Analyze data
    data = """id,name,age,salary
1,John,30,50000
2,Jane,25,45000"""
    
    result = await engine.analyze_data(
        data=data,
        question="Tính lương trung bình và tạo code PySpark"
    )
    
    if result.success:
        print(f"✅ Response:\n{result.response}")
        print(f"💰 Cost: ${result.cost:.4f}")
        print(f"🎯 Quality: {result.quality_score:.2%}")
    else:
        print(f"❌ Error: {result.error}")

# Run
asyncio.run(basic_example())
```

### With Fallback

```python
async def fallback_example():
    config = AIConfig(
        provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
        fallback_providers=[
            AIProvider.GOOGLE_GEMINI_25_FLASH,
            AIProvider.ANTHROPIC_CLAUDE_3_HAIKU,
            AIProvider.OPENAI_GPT35
        ]
    )
    
    engine = AdvancedAIEngine(config)
    
    # Nếu Gemini lỗi → tự động chuyển Claude → GPT-3.5
    result = await engine.analyze_data(data, question)
    
    print(f"Provider used: {result.provider_used}")
    print(f"Fallbacks: {engine.stats['fallback_count']}")

asyncio.run(fallback_example())
```

---

## 🔧 Configuration

### AIConfig Options

```python
config = AIConfig(
    # Primary model
    provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
    api_key="your-key",  # Optional, auto-load từ env
    
    # Fallback chain
    fallback_providers=[
        AIProvider.GOOGLE_GEMINI_25_FLASH,
        AIProvider.ANTHROPIC_CLAUDE_3_HAIKU
    ],
    
    # Performance
    max_tokens=4096,
    temperature=0.7,
    top_p=0.9,
    timeout=60,
    retry_count=3,
    retry_delay=1.0,
    
    # Caching
    cache_enabled=True,
    cache_ttl=3600,  # 1 hour
    cache_max_size=1000,
    
    # Rate limiting
    rate_limit_enabled=True,
    max_requests_per_minute=60,
    
    # Cost control
    max_cost_per_request=1.0,  # USD
    daily_budget=10.0,         # USD
    
    # Quality control
    min_quality_score=0.7,
    enable_quality_check=True,
    
    # Advanced
    parallel_requests=5,
    chunk_size=1000,
    overlap_size=200
)
```

---

## 📊 AI Providers

### Comparison Table

| Provider | Model | Speed | Cost (per 1M tokens) | Context | Free Tier |
|----------|-------|-------|---------------------|---------|-----------|
| **Gemini 2.5 Flash** | Fast | ⚡⚡⚡ | Free | 32K | ✅ Yes |
| **Gemini 2.5 Pro** | Advanced | ⚡⚡ | $1-2 | 128K | Limited |
| **Claude 3 Haiku** | Fast | ⚡⚡⚡ | $0.25-1.25 | 200K | ❌ No |
| **Claude 3 Sonnet** | Balanced | ⚡⚡ | $3-15 | 200K | ❌ No |
| **Claude 3 Opus** | Best | ⚡ | $15-75 | 200K | ❌ No |
| **GPT-4o** | Fast | ⚡⚡⚡ | $5-15 | 128K | Limited |
| **GPT-4 Turbo** | Balanced | ⚡⚡ | $10-30 | 128K | Limited |
| **GPT-4** | Best | ⚡ | $30-60 | 8K | Limited |
| **GPT-3.5 Turbo** | Fast | ⚡⚡⚡ | $0.5-1.5 | 16K | Limited |

### Recommendations

**For Development (Free):**
```python
provider=AIProvider.GOOGLE_GEMINI_25_FLASH
```

**For Production (Best Quality):**
```python
provider=AIProvider.ANTHROPIC_CLAUDE_3_OPUS
fallback_providers=[
    AIProvider.GOOGLE_GEMINI_25_PRO,
    AIProvider.OPENAI_GPT4_TURBO
]
```

**For Production (Cost-Effective):**
```python
provider=AIProvider.GOOGLE_GEMINI_25_FLASH
fallback_providers=[
    AIProvider.ANTHROPIC_CLAUDE_3_HAIKU,
    AIProvider.OPENAI_GPT35
]
```

---

## 💡 Advanced Features

### 1. Generate PySpark Code

```python
async def generate_code():
    engine = AdvancedAIEngine()
    
    result = await engine.generate_pyspark_code(
        data_description="""
        CSV file with columns:
        - id: integer
        - name: string
        - age: integer
        - salary: float
        - department: string
        """,
        operations=[
            "Đọc dữ liệu từ HDFS",
            "Filter employees có salary > 50000",
            "Group by department",
            "Tính average salary và count",
            "Sort theo avg salary giảm dần",
            "Lưu kết quả ra Parquet"
        ],
        optimization_level="advanced"  # basic, standard, advanced
    )
    
    if result.success:
        print(result.response)  # Complete PySpark code

asyncio.run(generate_code())
```

### 2. Streaming (Coming Soon)

```python
async def streaming_example():
    def callback(chunk: str):
        print(chunk, end='', flush=True)
    
    result = await engine.analyze_data(
        data=data,
        question=question,
        streaming=True,
        callback=callback
    )
```

### 3. Quality Scoring

Engine tự động đánh giá chất lượng dựa trên:

- **Length** (20%): Độ dài hợp lý
- **Code presence** (30%): Có code khi cần
- **Structure** (20%): Format, headers, lists
- **Relevance** (15%): Liên quan đến câu hỏi
- **Completeness** (15%): Đầy đủ, có kết luận

```python
result = await engine.analyze_data(data, question)
print(f"Quality Score: {result.quality_score:.2%}")

# Set minimum quality
config = AIConfig(
    min_quality_score=0.7,
    enable_quality_check=True
)
```

### 4. Cost Tracking

```python
# Check daily budget
cost_stats = engine.cost_tracker.get_stats()
print(f"Today's cost: ${cost_stats['today_cost']:.2f}")
print(f"Remaining: ${cost_stats['remaining_budget']:.2f}")

# Set budget limit
config = AIConfig(
    daily_budget=10.0,
    max_cost_per_request=1.0
)
```

### 5. Statistics

```python
stats = engine.get_statistics()
print(stats)

# Output:
{
    "requests": {
        "total": 50,
        "successful": 48,
        "failed": 2,
        "success_rate": "96.00%"
    },
    "cache": {
        "hits": 15,
        "hit_rate": "30.00%"
    },
    "cost": {
        "today_cost": 2.45,
        "daily_budget": 10.0,
        "remaining_budget": 7.55,
        "total_cost": 15.23
    },
    "tokens": 125000,
    "providers": {
        "google_gemini_25_flash": 45,
        "anthropic_claude3_haiku": 3
    },
    "fallbacks": 3
}
```

---

## 🎓 Examples

### Example 1: Data Analysis

```python
data = """date,product,sales,region
2024-01-01,A,1000,North
2024-01-01,B,1500,South
2024-01-02,A,1200,North"""

result = await engine.analyze_data(
    data=data,
    question="""
    Phân tích dữ liệu sales này:
    1. Tổng sales theo product
    2. Tổng sales theo region
    3. Trend theo thời gian
    4. Tạo code PySpark hoàn chỉnh
    """
)

print(result.response)
```

### Example 2: Schema Analysis

```python
result = await engine.analyze_data(
    data=large_dataset,
    question="""
    Phân tích schema của dataset này:
    1. Xác định các cột và kiểu dữ liệu
    2. Phát hiện missing values
    3. Đề xuất data quality checks
    4. Tạo PySpark code để validate
    """
)
```

### Example 3: Performance Optimization

```python
result = await engine.analyze_data(
    data=slow_code,
    question="""
    Code PySpark này chạy chậm:
    ```python
    df.groupBy("col").count().show()
    ```
    
    Hãy:
    1. Phân tích bottlenecks
    2. Đề xuất optimizations
    3. Tạo code tối ưu với:
       - Partitioning
       - Caching
       - Broadcast joins
    """
)
```

---

## ⚙️ Troubleshooting

### 1. API Key Not Found

```python
# Error: API key not set
# Solution: Set environment variable or pass directly
config = AIConfig(
    provider=AIProvider.OPENAI_GPT4,
    api_key="your-key-here"
)
```

### 2. Rate Limit Exceeded

```python
# Error: Rate limit exceeded
# Solution: Enable rate limiting
config = AIConfig(
    rate_limit_enabled=True,
    max_requests_per_minute=30  # Reduce if needed
)
```

### 3. Budget Exceeded

```python
# Error: Daily budget exceeded
# Solution: Increase budget or wait until tomorrow
config = AIConfig(
    daily_budget=20.0  # Increase limit
)

# Or reset costs manually
engine.cost_tracker.costs.clear()
```

### 4. Low Quality Responses

```python
# Solution 1: Use better model
config = AIConfig(
    provider=AIProvider.ANTHROPIC_CLAUDE_3_OPUS
)

# Solution 2: Adjust quality threshold
config = AIConfig(
    min_quality_score=0.5  # Lower threshold
)

# Solution 3: Provide more context
result = await engine.analyze_data(
    data=data,
    question="<more detailed question with examples>"
)
```

### 5. All Providers Failed

```python
# Check API keys
print(os.getenv("GOOGLE_API_KEY"))
print(os.getenv("ANTHROPIC_API_KEY"))

# Check fallback chain
config = AIConfig(
    provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
    fallback_providers=[
        AIProvider.GOOGLE_GEMINI_25_FLASH,
        AIProvider.ANTHROPIC_CLAUDE_3_HAIKU,
        AIProvider.OPENAI_GPT35
    ]
)
```

---

## 📈 Best Practices

### 1. Choose Right Provider

```python
# Development: Use free Gemini
config_dev = AIConfig(provider=AIProvider.GOOGLE_GEMINI_25_FLASH)

# Production: Use Claude/GPT-4 với fallback
config_prod = AIConfig(
    provider=AIProvider.ANTHROPIC_CLAUDE_3_SONNET,
    fallback_providers=[
        AIProvider.GOOGLE_GEMINI_25_PRO,
        AIProvider.OPENAI_GPT4O
    ]
)
```

### 2. Enable Caching

```python
# Cache lâu cho queries tĩnh
config = AIConfig(
    cache_enabled=True,
    cache_ttl=7200  # 2 hours
)

# Cache ngắn cho data động
config = AIConfig(
    cache_enabled=True,
    cache_ttl=300  # 5 minutes
)
```

### 3. Set Appropriate Budgets

```python
# Generous budget cho production
config = AIConfig(daily_budget=50.0)

# Strict budget cho development
config = AIConfig(daily_budget=5.0)
```

### 4. Use Quality Checks

```python
config = AIConfig(
    enable_quality_check=True,
    min_quality_score=0.8  # High threshold
)

result = await engine.analyze_data(data, question)
if result.quality_score < 0.8:
    # Retry với detailed prompt
    result = await engine.analyze_data(data, better_question)
```

### 5. Monitor Statistics

```python
# Định kỳ check stats
stats = engine.get_statistics()

if stats['cache']['hit_rate'] < 20:
    print("⚠️ Low cache hit rate - consider increasing TTL")

if stats['requests']['success_rate'] < 90:
    print("⚠️ High failure rate - check API keys and fallbacks")

if stats['cost']['remaining_budget'] < 2.0:
    print("⚠️ Budget running low")
```

---

## 🔄 Migration from V7.0

### Changes

1. **Import path changed:**
   ```python
   # OLD
   from advanced_ai_engine import AdvancedAIEngine
   
   # NEW
   from advanced_ai_engine_v8 import AdvancedAIEngine
   ```

2. **New providers:**
   ```python
   # NEW models available
   AIProvider.OPENAI_GPT4O
   AIProvider.GOOGLE_GEMINI_25_FLASH
   AIProvider.GOOGLE_GEMINI_25_PRO
   AIProvider.ANTHROPIC_CLAUDE_3_HAIKU
   ```

3. **Enhanced config:**
   ```python
   # NEW options
   config = AIConfig(
       fallback_providers=[...],  # NEW
       rate_limit_enabled=True,   # NEW
       daily_budget=10.0,         # NEW
       min_quality_score=0.7      # NEW
   )
   ```

4. **Enhanced results:**
   ```python
   result = await engine.analyze_data(...)
   
   # NEW fields
   print(result.quality_score)   # NEW
   print(result.cost)           # NEW
   print(result.provider_used)  # NEW
   print(result.retry_count)    # NEW
   ```

---

## 📚 API Reference

### Classes

#### `AdvancedAIEngine`

```python
class AdvancedAIEngine:
    def __init__(self, config: Optional[AIConfig] = None)
    
    async def analyze_data(
        self,
        data: str,
        question: str,
        streaming: bool = False,
        callback: Optional[Callable] = None
    ) -> AnalysisResult
    
    async def generate_pyspark_code(
        self,
        data_description: str,
        operations: List[str],
        optimization_level: str = "standard"
    ) -> AnalysisResult
    
    def get_statistics(self) -> Dict[str, Any]
    
    def clear_cache(self)
```

#### `AIConfig`

```python
@dataclass
class AIConfig:
    provider: AIProvider
    api_key: Optional[str]
    fallback_providers: List[AIProvider]
    max_tokens: int
    temperature: float
    cache_enabled: bool
    daily_budget: float
    # ... (see Configuration section)
```

#### `AnalysisResult`

```python
@dataclass
class AnalysisResult:
    success: bool
    response: str
    metadata: Dict[str, Any]
    tokens_used: int
    processing_time: float
    confidence_score: float
    quality_score: float
    cost: float
    error: Optional[str]
    cached: bool
    provider_used: Optional[str]
    retry_count: int
```

---

## 🎯 Performance Tips

1. **Use Gemini for free tier:** `GOOGLE_GEMINI_25_FLASH`
2. **Enable caching:** Reduce costs and latency
3. **Set appropriate budgets:** Prevent overspending
4. **Use fallback chains:** Ensure high availability
5. **Monitor quality scores:** Maintain output quality
6. **Chunk large data:** Better for deep analysis
7. **Use parallel requests:** Speed up multi-chunk analysis

---

## 📞 Support

- **Documentation:** This file
- **Issues:** Check error logs
- **Updates:** Check CHANGELOG.md

---

## 🏆 Comparison: V7 vs V8

| Feature | V7.0 | V8.0 |
|---------|------|------|
| Models | 3 | 9 |
| Fallback | ❌ | ✅ |
| Cost Tracking | ❌ | ✅ |
| Quality Scoring | ❌ | ✅ |
| Rate Limiting | Basic | Advanced |
| Caching | Basic | Smart LRU+TTL |
| Free Tier | Gemini 1.5 | Gemini 2.5 Flash |
| Statistics | Basic | Comprehensive |

---

**Version:** 8.0.0  
**Last Updated:** October 14, 2025  
**Status:** ✅ Production Ready
