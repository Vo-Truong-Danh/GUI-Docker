# ⚡ AI Engine V8.0 - Quick Start

**Version:** 8.0.0  
**Date:** October 14, 2025

---

## 🎯 Tính năng nổi bật

✅ **Multi-model support** - 9 AI models  
✅ **Smart fallback** - Tự động chuyển model khi lỗi  
✅ **Cost tracking** - Theo dõi chi phí  
✅ **Quality scoring** - Đánh giá chất lượng tự động  
✅ **Free tier** - Gemini 2.5 Flash miễn phí  

---

## 📦 Cài đặt nhanh (30 giây)

```bash
# 1. Install dependencies
pip install google-generativeai

# 2. Set API key (optional - có thể dùng free tier)
$env:GOOGLE_API_KEY="your-key-here"

# 3. Run
python advanced_ai_tab_v8.py
```

---

## 🚀 Sử dụng cơ bản

### 1. Trong GUI

```
1. Mở "Advanced AI" tab
2. Chọn model: "Gemini 2.5 Flash (Free)"
3. Click "🚀 Initialize Engine"
4. Select data file (📁 button)
5. Nhập câu hỏi
6. Click "🔍 Analyze Data"
```

### 2. Trong Python Code

```python
import asyncio
from advanced_ai_engine_v8 import AdvancedAIEngine, AIConfig, AIProvider

async def main():
    # Init engine (free tier)
    config = AIConfig(
        provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
        daily_budget=5.0
    )
    engine = AdvancedAIEngine(config)
    
    # Analyze data
    data = """id,name,salary
1,John,50000
2,Jane,60000"""
    
    result = await engine.analyze_data(
        data=data,
        question="Tính lương trung bình và tạo code PySpark"
    )
    
    if result.success:
        print(result.response)
        print(f"\nQuality: {result.quality_score:.1%}")
        print(f"Cost: ${result.cost:.4f}")

asyncio.run(main())
```

---

## 🆓 Free Tier (Không cần API key)

**Model:** Gemini 2.5 Flash

```python
config = AIConfig(
    provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
    cache_enabled=True
)
```

**Giới hạn:**
- ✅ Unlimited requests
- ✅ Fast response (< 2s)
- ✅ 32K context window
- ✅ $0.00 cost

---

## 💰 Cost Comparison

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------|------------------------|----------|
| **Gemini 2.5 Flash** | $0.00 | $0.00 | Development |
| Claude 3 Haiku | $0.25 | $1.25 | Production (Fast) |
| GPT-3.5 Turbo | $0.50 | $1.50 | Production (Balanced) |
| Claude 3 Sonnet | $3.00 | $15.00 | Production (Quality) |
| GPT-4 Turbo | $10.00 | $30.00 | Production (Best) |
| Claude 3 Opus | $15.00 | $75.00 | Critical Tasks |

---

## 🎓 Use Cases

### 1. Data Analysis

```python
result = await engine.analyze_data(
    data=csv_data,
    question="""
    Phân tích dataset này:
    1. Statistics cơ bản
    2. Phát hiện outliers
    3. Correlations
    4. Tạo code PySpark để xử lý
    """
)
```

### 2. Code Generation

```python
result = await engine.generate_pyspark_code(
    data_description="CSV: id, name, age, salary, dept",
    operations=[
        "Load from HDFS",
        "Filter salary > 50000",
        "Group by department",
        "Calculate avg and sum",
        "Save to Parquet"
    ],
    optimization_level="advanced"
)
```

### 3. Code Review

```python
result = await engine.analyze_data(
    data=your_code,
    question="""
    Review code này:
    1. Tìm bugs
    2. Security issues
    3. Performance bottlenecks
    4. Đề xuất improvements
    5. Tạo optimized version
    """
)
```

---

## ⚙️ Configuration

### Basic

```python
config = AIConfig(
    provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
    temperature=0.7,
    cache_enabled=True
)
```

### Production

```python
config = AIConfig(
    provider=AIProvider.ANTHROPIC_CLAUDE_3_SONNET,
    fallback_providers=[
        AIProvider.GOOGLE_GEMINI_25_FLASH,
        AIProvider.OPENAI_GPT4O
    ],
    daily_budget=50.0,
    min_quality_score=0.8,
    rate_limit_enabled=True
)
```

---

## 📊 Monitoring

```python
# Get statistics
stats = engine.get_statistics()

print(f"Total requests: {stats['requests']['total']}")
print(f"Success rate: {stats['requests']['success_rate']}")
print(f"Cache hit rate: {stats['cache']['hit_rate']}")
print(f"Today cost: ${stats['cost']['today_cost']:.2f}")
print(f"Budget left: ${stats['cost']['remaining_budget']:.2f}")
```

---

## 🔧 Troubleshooting

### Engine không khởi tạo được

**Lỗi:** `ImportError: No module named 'google.generativeai'`

**Fix:**
```bash
pip install google-generativeai
```

### API key không hợp lệ

**Fix 1:** Dùng free tier (Gemini 2.5 Flash)
```python
provider=AIProvider.GOOGLE_GEMINI_25_FLASH
```

**Fix 2:** Get free API key tại https://makersuite.google.com/app/apikey

### Response chất lượng thấp

**Fix 1:** Tăng quality threshold
```python
config = AIConfig(min_quality_score=0.5)  # Lower threshold
```

**Fix 2:** Dùng model tốt hơn
```python
provider=AIProvider.ANTHROPIC_CLAUDE_3_OPUS
```

**Fix 3:** Cải thiện prompt
```python
question = """
<detailed question with examples and context>
"""
```

### Budget exceeded

**Fix:**
```python
config = AIConfig(daily_budget=20.0)  # Increase limit
```

Or wait until tomorrow (auto-reset).

---

## 🎯 Best Practices

### 1. Development
- ✅ Dùng Gemini 2.5 Flash (free)
- ✅ Enable cache
- ✅ Low budget limit

### 2. Production
- ✅ Dùng Claude/GPT-4 với fallback
- ✅ Set appropriate budget
- ✅ Enable quality checks
- ✅ Monitor statistics

### 3. Cost Optimization
- ✅ Enable caching (30-50% cost reduction)
- ✅ Use cheaper models for simple tasks
- ✅ Set daily budgets
- ✅ Monitor usage

---

## 📚 Documentation

- **Full Guide:** [`AI_ENGINE_V8_GUIDE.md`](AI_ENGINE_V8_GUIDE.md)
- **API Reference:** See guide
- **Examples:** See guide

---

## ✅ Checklist

**Setup:**
- [ ] Install `google-generativeai`
- [ ] (Optional) Set API key
- [ ] Test with demo code

**Usage:**
- [ ] Initialize engine
- [ ] Select data source
- [ ] Write clear prompt
- [ ] Check quality score
- [ ] Monitor costs

---

## 🆘 Support

**Issues:**
1. Check error logs
2. Read troubleshooting section
3. Check API key validity
4. Try fallback providers

**Updates:**
- Current version: 8.0.0
- Check `CHANGELOG.md` for changes

---

## 🎉 Quick Examples

### Example 1: Analyze CSV (1 minute)

```python
import asyncio
from advanced_ai_engine_v8 import quick_analyze

data = """id,product,sales
1,A,1000
2,B,1500"""

result = asyncio.run(quick_analyze(
    data=data,
    question="Tính tổng sales"
))

print(result)
```

### Example 2: Generate Code (2 minutes)

```python
from advanced_ai_engine_v8 import AdvancedAIEngine, AIConfig, AIProvider
import asyncio

async def main():
    config = AIConfig(provider=AIProvider.GOOGLE_GEMINI_25_FLASH)
    engine = AdvancedAIEngine(config)
    
    result = await engine.generate_pyspark_code(
        data_description="CSV: id, name, sales",
        operations=[
            "Load data",
            "Filter sales > 1000",
            "Group by name",
            "Sum sales",
            "Save result"
        ]
    )
    
    print(result.response)

asyncio.run(main())
```

---

**Ready to start?** 🚀

```bash
python advanced_ai_tab_v8.py
```
