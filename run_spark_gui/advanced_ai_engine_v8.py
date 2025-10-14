#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI Engine - V8.0 Enhanced Edition
Cải tiến:
- Multi-model support (GPT-4, Claude, Gemini, Local models)
- Smart fallback system
- Cost tracking & budgets
- Quality scoring
- Rate limiting
- Advanced caching với TTL
- Better error handling
- Async streaming
"""

import os
import json
import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import re
from collections import deque
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports với fallback
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic not available. Install: pip install anthropic")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini not available. Install: pip install google-generativeai")


# ============================================================================
# ENUMS & CONFIGURATION
# ============================================================================

class AIProvider(Enum):
    """AI Providers"""
    # OpenAI
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT4_TURBO = "openai_gpt4_turbo"
    OPENAI_GPT4O = "openai_gpt4o"
    OPENAI_GPT35 = "openai_gpt35"
    
    # Anthropic
    ANTHROPIC_CLAUDE_3_OPUS = "anthropic_claude3_opus"
    ANTHROPIC_CLAUDE_3_SONNET = "anthropic_claude3_sonnet"
    ANTHROPIC_CLAUDE_3_HAIKU = "anthropic_claude3_haiku"
    
    # Google
    GOOGLE_GEMINI_25_FLASH = "google_gemini_25_flash"
    GOOGLE_GEMINI_25_PRO = "google_gemini_25_pro"
    GOOGLE_GEMINI_15_FLASH = "google_gemini_15_flash"
    GOOGLE_GEMINI_15_PRO = "google_gemini_15_pro"
    
    # Local
    LOCAL_OLLAMA = "local_ollama"


class AnalysisType(Enum):
    """Analysis types"""
    QUICK = "quick"          # < 1MB
    STANDARD = "standard"    # 1-10MB
    DEEP = "deep"           # 10-100MB
    DISTRIBUTED = "distributed"  # > 100MB


@dataclass
class ModelConfig:
    """Model configuration"""
    provider: AIProvider
    model_name: str
    max_tokens: int
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_streaming: bool = True
    rate_limit_rpm: int = 60  # Requests per minute


# Model configurations
MODEL_CONFIGS = {
    AIProvider.OPENAI_GPT4: ModelConfig(
        AIProvider.OPENAI_GPT4, "gpt-4", 8192, 8192, 0.03, 0.06, True, 60
    ),
    AIProvider.OPENAI_GPT4_TURBO: ModelConfig(
        AIProvider.OPENAI_GPT4_TURBO, "gpt-4-turbo", 4096, 128000, 0.01, 0.03, True, 500
    ),
    AIProvider.OPENAI_GPT4O: ModelConfig(
        AIProvider.OPENAI_GPT4O, "gpt-4o", 4096, 128000, 0.005, 0.015, True, 500
    ),
    AIProvider.GOOGLE_GEMINI_25_FLASH: ModelConfig(
        AIProvider.GOOGLE_GEMINI_25_FLASH, "models/gemini-2.5-flash", 8192, 32000, 0.0, 0.0, True, 1000
    ),
    AIProvider.GOOGLE_GEMINI_25_PRO: ModelConfig(
        AIProvider.GOOGLE_GEMINI_25_PRO, "models/gemini-2.5-pro", 8192, 128000, 0.001, 0.002, True, 100
    ),
    AIProvider.ANTHROPIC_CLAUDE_3_OPUS: ModelConfig(
        AIProvider.ANTHROPIC_CLAUDE_3_OPUS, "claude-3-opus-20240229", 4096, 200000, 0.015, 0.075, True, 50
    ),
    AIProvider.ANTHROPIC_CLAUDE_3_SONNET: ModelConfig(
        AIProvider.ANTHROPIC_CLAUDE_3_SONNET, "claude-3-sonnet-20240229", 4096, 200000, 0.003, 0.015, True, 100
    ),
    AIProvider.ANTHROPIC_CLAUDE_3_HAIKU: ModelConfig(
        AIProvider.ANTHROPIC_CLAUDE_3_HAIKU, "claude-3-haiku-20240307", 4096, 200000, 0.00025, 0.00125, True, 200
    ),
}


@dataclass
class AIConfig:
    """AI Engine configuration"""
    # Primary model
    provider: AIProvider = AIProvider.GOOGLE_GEMINI_25_FLASH
    api_key: Optional[str] = None
    
    # Fallback models (auto-switch on error)
    fallback_providers: List[AIProvider] = field(default_factory=lambda: [
        AIProvider.GOOGLE_GEMINI_25_FLASH,
        AIProvider.ANTHROPIC_CLAUDE_3_HAIKU,
        AIProvider.OPENAI_GPT35
    ])
    
    # Performance
    max_tokens: int = 8192  # Increased for longer responses
    temperature: float = 0.0  # Zero for deterministic code (0.1→0.0)
    top_p: float = 0.9
    timeout: int = 120  # Increased timeout
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    
    # Rate limiting
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60
    
    # Cost control
    max_cost_per_request: float = 1.0  # USD
    daily_budget: float = 10.0  # USD
    
    # Quality control
    min_quality_score: float = 0.7
    enable_quality_check: bool = True
    
    # Advanced
    parallel_requests: int = 5
    chunk_size: int = 1000
    overlap_size: int = 200
    
    def __post_init__(self):
        """Auto-load API keys"""
        if not self.api_key:
            if self.provider.value.startswith("openai"):
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider.value.startswith("anthropic"):
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            elif self.provider.value.startswith("google"):
                self.api_key = os.getenv("GOOGLE_API_KEY")


@dataclass
class AnalysisResult:
    """Analysis result"""
    success: bool
    response: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0
    processing_time: float = 0.0
    confidence_score: float = 0.0
    quality_score: float = 0.0
    cost: float = 0.0
    error: Optional[str] = None
    cached: bool = False
    provider_used: Optional[str] = None
    retry_count: int = 0


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """Rate limiter with sliding window"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()
    
    async def acquire(self):
        """Acquire permission to make request"""
        with self.lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] < now - self.window_seconds:
                self.requests.popleft()
            
            # Check if can make request
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest = self.requests[0]
                wait_time = self.window_seconds - (now - oldest) + 0.1
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                return await self.acquire()
            
            # Add current request
            self.requests.append(now)
            return True


# ============================================================================
# COST TRACKER
# ============================================================================

class CostTracker:
    """Track API costs"""
    
    def __init__(self, daily_budget: float = 10.0):
        self.daily_budget = daily_budget
        self.costs = {}  # date -> cost
        self.lock = threading.Lock()
    
    def add_cost(self, cost: float) -> bool:
        """Add cost and check budget"""
        with self.lock:
            today = datetime.now().strftime("%Y-%m-%d")
            self.costs[today] = self.costs.get(today, 0.0) + cost
            
            if self.costs[today] > self.daily_budget:
                logger.error(f"Daily budget exceeded: ${self.costs[today]:.2f} / ${self.daily_budget:.2f}")
                return False
            
            return True
    
    def get_daily_cost(self) -> float:
        """Get today's cost"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.costs.get(today, 0.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cost statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        return {
            'today_cost': self.get_daily_cost(),
            'daily_budget': self.daily_budget,
            'remaining_budget': max(0, self.daily_budget - self.get_daily_cost()),
            'total_days': len(self.costs),
            'total_cost': sum(self.costs.values())
        }


# ============================================================================
# QUALITY SCORER
# ============================================================================

class QualityScorer:
    """Đánh giá chất lượng câu trả lời"""
    
    @staticmethod
    def score_response(response: str, question: str, data: Optional[str] = None) -> float:
        """
        Score response quality (0-1)
        
        Criteria:
        - Completeness (no truncation)
        - Code presence (for coding questions)
        - Structure (formatting, sections)
        - Length appropriateness
        - Relevance to question
        """
        score = 0.0
        
        # 1. COMPLETENESS CHECK (40%) - MOST IMPORTANT
        is_truncated = any([
            response.endswith('...'),
            response.endswith('*'),
            response.endswith('`'),
            response.count('```') % 2 != 0,  # Unclosed code block
            len(response) < 100,  # Too short
            response.endswith(':'),  # Ends mid-sentence
            'Đang tiếp tục' in response.lower(),
            'sẽ tiếp tục' in response.lower()
        ])
        
        if not is_truncated:
            score += 0.4
        
        # 2. Code presence (30% if coding related)
        if any(kw in question.lower() for kw in ['code', 'pyspark', 'python', 'sql', 'tạo']):
            has_complete_code = (
                '```python' in response and 
                response.count('```') >= 2 and
                ('def ' in response or 'import ' in response)
            )
            score += 0.3 if has_complete_code else 0.0
        else:
            score += 0.3
        
        # 3. Length check (15%)
        min_length = 300 if 'code' in question.lower() else 200
        length_score = min(len(response) / min_length, 1.0) * 0.15
        score += length_score
        
        # 4. Relevance (10%)
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words & response_words) / max(len(question_words), 1)
        score += min(overlap, 1.0) * 0.10
        
        # 5. Structure (5%)
        has_structure = bool(re.search(r'^\d+\.|\*|\-|#+', response, re.MULTILINE))
        score += 0.05 if has_structure else 0.0
        
        return min(score, 1.0)


# ============================================================================
# SMART CACHE
# ============================================================================

class SmartCache:
    """Smart cache with TTL and LRU"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def _generate_key(self, prompt: str, config: Dict[str, Any]) -> str:
        """Generate cache key"""
        data = f"{prompt}_{json.dumps(config, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get(self, prompt: str, config: Dict[str, Any]) -> Optional[AnalysisResult]:
        """Get from cache"""
        key = self._generate_key(prompt, config)
        
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if time.time() - entry['timestamp'] > self.ttl:
                del self.cache[key]
                del self.access_times[key]
                return None
            
            # Update access time
            self.access_times[key] = time.time()
            
            result = entry['result']
            result.cached = True
            return result
    
    def set(self, prompt: str, config: Dict[str, Any], result: AnalysisResult):
        """Set cache"""
        key = self._generate_key(prompt, config)
        
        with self.lock:
            # LRU eviction
            if len(self.cache) >= self.max_size:
                oldest = min(self.access_times.items(), key=lambda x: x[1])
                del self.cache[oldest[0]]
                del self.access_times[oldest[0]]
            
            self.cache[key] = {
                'result': result,
                'timestamp': time.time()
            }
            self.access_times[key] = time.time()
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()


# ============================================================================
# DATA ANALYZER
# ============================================================================

class DataAnalyzer:
    """Analyze data before AI processing"""
    
    @staticmethod
    def estimate_size(data: str) -> int:
        """Estimate data size in bytes"""
        return len(data.encode('utf-8'))
    
    @staticmethod
    def determine_analysis_type(size: int) -> AnalysisType:
        """Determine analysis type"""
        if size < 1_000_000:
            return AnalysisType.QUICK
        elif size < 10_000_000:
            return AnalysisType.STANDARD
        elif size < 100_000_000:
            return AnalysisType.DEEP
        else:
            return AnalysisType.DISTRIBUTED
    
    @staticmethod
    def chunk_data(data: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk data with overlap"""
        lines = data.split('\n')
        chunks = []
        
        for i in range(0, len(lines), chunk_size - overlap):
            chunk = '\n'.join(lines[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def extract_schema(data: str, max_lines: int = 100) -> Dict[str, Any]:
        """Extract data schema"""
        lines = data.split('\n')[:max_lines]
        
        schema = {
            'total_lines': len(data.split('\n')),
            'sample_lines': len(lines),
            'columns': [],
            'data_types': {}
        }
        
        # Detect delimiter
        if lines and ',' in lines[0]:
            delimiter = ','
        elif lines and '\t' in lines[0]:
            delimiter = '\t'
        else:
            return schema
        
        # Extract columns
        if lines:
            header = lines[0].split(delimiter)
            schema['columns'] = [c.strip() for c in header]
        
        return schema


# ============================================================================
# AI ADAPTERS
# ============================================================================

class BaseAIAdapter:
    """Base adapter"""
    
    def __init__(self, config: AIConfig, model_config: ModelConfig):
        self.config = config
        self.model_config = model_config
        self.rate_limiter = RateLimiter(model_config.rate_limit_rpm)
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> AnalysisResult:
        """Generate response"""
        raise NotImplementedError
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost"""
        input_cost = (input_tokens / 1000) * self.model_config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * self.model_config.cost_per_1k_output
        return input_cost + output_cost


class OpenAIAdapter(BaseAIAdapter):
    """OpenAI adapter"""
    
    def __init__(self, config: AIConfig, model_config: ModelConfig):
        super().__init__(config, model_config)
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")
        openai.api_key = config.api_key
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> AnalysisResult:
        """Generate with OpenAI"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model_config.model_name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            text = response.choices[0].message.content
            tokens = response.usage.total_tokens
            cost = self.calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens)
            
            return AnalysisResult(
                success=True,
                response=text,
                tokens_used=tokens,
                processing_time=time.time() - start_time,
                cost=cost,
                provider_used=self.model_config.provider.value,
                metadata={'model': self.model_config.model_name}
            )
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return AnalysisResult(
                success=False,
                response="",
                error=str(e),
                processing_time=time.time() - start_time
            )


class GeminiAdapter(BaseAIAdapter):
    """Gemini adapter"""
    
    def __init__(self, config: AIConfig, model_config: ModelConfig):
        super().__init__(config, model_config)
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")
        genai.configure(api_key=config.api_key)
        
        # System instruction to force code-only output
        system_instruction = """You are a CODE GENERATOR MACHINE. Output ONLY executable Python/PySpark code.

ABSOLUTE RULES:
1. NO explanations, NO tutorials, NO theory
2. NO "Giải thích", NO "Best practices", NO prose
3. ONLY code with brief comments
4. Start with ```python immediately
5. Maximum 50 lines of code
6. Simple, runnable, complete code

You are NOT a teacher. You are a code printer."""
        
        self.model = genai.GenerativeModel(
            model_config.model_name,
            system_instruction=system_instruction
        )
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> AnalysisResult:
        """Generate with Gemini"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            # Strict generation config for code-only output
            generation_config = genai.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=min(self.config.max_tokens, 2048),  # Limit to force conciseness
                top_p=0.95,
                top_k=40,
                candidate_count=1,
                stop_sequences=["```\n\n###", "```\n\n##", "---\n\n###"]  # Stop at explanations
            )
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=generation_config
            )
            
            return AnalysisResult(
                success=True,
                response=response.text,
                tokens_used=0,
                processing_time=time.time() - start_time,
                cost=0.0,  # Free tier
                provider_used=self.model_config.provider.value,
                metadata={'model': self.model_config.model_name}
            )
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return AnalysisResult(
                success=False,
                response="",
                error=str(e),
                processing_time=time.time() - start_time
            )


class AnthropicAdapter(BaseAIAdapter):
    """Anthropic adapter"""
    
    def __init__(self, config: AIConfig, model_config: ModelConfig):
        super().__init__(config, model_config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic not installed")
        self.client = anthropic.Anthropic(api_key=config.api_key)
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> AnalysisResult:
        """Generate with Claude"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            system_prompt = context or "You are a helpful AI assistant."
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model_config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            text = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens
            cost = self.calculate_cost(response.usage.input_tokens, response.usage.output_tokens)
            
            return AnalysisResult(
                success=True,
                response=text,
                tokens_used=tokens,
                processing_time=time.time() - start_time,
                cost=cost,
                provider_used=self.model_config.provider.value,
                metadata={'model': self.model_config.model_name}
            )
            
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            return AnalysisResult(
                success=False,
                response="",
                error=str(e),
                processing_time=time.time() - start_time
            )


# ============================================================================
# ADVANCED AI ENGINE V8
# ============================================================================

class AdvancedAIEngine:
    """
    Advanced AI Engine V8.0
    
    Features:
    - Multi-model support with auto-fallback
    - Cost tracking & budgets
    - Quality scoring
    - Rate limiting
    - Smart caching
    - Better error handling
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        
        # Components
        self.cache = SmartCache(self.config.cache_max_size, self.config.cache_ttl) if self.config.cache_enabled else None
        self.cost_tracker = CostTracker(self.config.daily_budget)
        self.quality_scorer = QualityScorer()
        self.data_analyzer = DataAnalyzer()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'providers_used': {},
            'fallback_count': 0
        }
        
        logger.info(f"AI Engine initialized with provider: {self.config.provider.value}")
    
    def _create_adapter(self, provider: AIProvider) -> Optional[BaseAIAdapter]:
        """Create adapter for provider"""
        try:
            model_config = MODEL_CONFIGS.get(provider)
            if not model_config:
                logger.error(f"No config for provider: {provider}")
                return None
            
            if provider.value.startswith("openai"):
                return OpenAIAdapter(self.config, model_config)
            elif provider.value.startswith("google"):
                return GeminiAdapter(self.config, model_config)
            elif provider.value.startswith("anthropic"):
                return AnthropicAdapter(self.config, model_config)
            else:
                logger.error(f"Unsupported provider: {provider}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create adapter for {provider}: {e}")
            return None
    
    async def _generate_with_fallback(self, prompt: str, context: Optional[str] = None) -> AnalysisResult:
        """Generate with automatic fallback"""
        providers = [self.config.provider] + self.config.fallback_providers
        
        for i, provider in enumerate(providers):
            logger.info(f"Trying provider: {provider.value}")
            
            adapter = self._create_adapter(provider)
            if not adapter:
                continue
            
            result = await adapter.generate(prompt, context)
            
            if result.success:
                if i > 0:
                    self.stats['fallback_count'] += 1
                    logger.info(f"Fallback successful with {provider.value}")
                return result
            else:
                logger.warning(f"Provider {provider.value} failed: {result.error}")
                if i < len(providers) - 1:
                    logger.info(f"Retrying with next provider...")
                    await asyncio.sleep(self.config.retry_delay)
        
        # All providers failed
        return AnalysisResult(
            success=False,
            response="",
            error="All providers failed",
            processing_time=0
        )
    
    async def analyze_data(self, data: str, question: str,
                          streaming: bool = False,
                          callback: Optional[Callable] = None) -> AnalysisResult:
        """
        Analyze data with AI
        
        Args:
            data: Data to analyze
            question: Question about data
            streaming: Use streaming
            callback: Streaming callback
        
        Returns:
            AnalysisResult
        """
        self.stats['total_requests'] += 1
        start_time = time.time()
        
        # Check cache
        if self.cache:
            cached = self.cache.get(question, {'data': data[:100]})
            if cached:
                self.stats['cache_hits'] += 1
                logger.info("✅ Cache hit!")
                return cached
        
        # Analyze data
        data_size = self.data_analyzer.estimate_size(data)
        analysis_type = self.data_analyzer.determine_analysis_type(data_size)
        logger.info(f"Data size: {data_size:,} bytes | Type: {analysis_type.value}")
        
        # Extract schema
        schema = self.data_analyzer.extract_schema(data)
        
        # Build context - MINIMAL (system instruction does the heavy lifting)
        context = f"""Data: {schema.get('total_lines', 'N/A')} rows, Columns: {', '.join(schema.get('columns', [])[:3])}

OUTPUT FORMAT:
```python
# code here
```

MAXIMUM 40 LINES."""
        
        # Build prompt - MORE FOCUSED
        if analysis_type == AnalysisType.QUICK:
            data_sample = data[:3000]  # Reduced sample size
        else:
            data_sample = data[:1500] + "\n...\n" + data[-1500:]
        
        prompt = f"""```csv
{data_sample}
```

Task: {question}

```python"""
        
        # Generate with fallback and retry for incomplete responses
        max_retries = 2
        for retry in range(max_retries):
            result = await self._generate_with_fallback(prompt, context)
            
            if not result.success:
                break
            
            # Quality check
            if self.config.enable_quality_check:
                quality_score = self.quality_scorer.score_response(result.response, question, data)
                result.quality_score = quality_score
                logger.info(f"Quality score: {quality_score:.2%}")
                
                # Retry if quality too low and truncated
                if quality_score < self.config.min_quality_score and retry < max_retries - 1:
                    logger.warning(f"⚠️ Low quality. Retrying {retry+1}/{max_retries}...")
                    prompt = f"RETRY:\n\n{prompt}\n\nMAX 30 LINES"
                    await asyncio.sleep(1)
                    continue
                else:
                    break
        
        if result.success:
            # Quality check
            if self.config.enable_quality_check:
                quality_score = self.quality_scorer.score_response(result.response, question, data)
                result.quality_score = quality_score
                logger.info(f"Quality score: {quality_score:.2%}")
                
                if quality_score < self.config.min_quality_score:
                    logger.warning(f"Low quality score: {quality_score:.2%} < {self.config.min_quality_score:.2%}")
            
            # Cost check
            if not self.cost_tracker.add_cost(result.cost):
                logger.error("Daily budget exceeded!")
                result.success = False
                result.error = "Daily budget exceeded"
                return result
            
            # Update stats
            self.stats['successful_requests'] += 1
            self.stats['total_cost'] += result.cost
            self.stats['total_tokens'] += result.tokens_used
            
            provider = result.provider_used or "unknown"
            self.stats['providers_used'][provider] = self.stats['providers_used'].get(provider, 0) + 1
            
            # Cache result
            if self.cache:
                self.cache.set(question, {'data': data[:100]}, result)
            
            logger.info(f"✅ Success! Time: {result.processing_time:.2f}s | Cost: ${result.cost:.4f} | Tokens: {result.tokens_used}")
        else:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ Failed: {result.error}")
        
        result.processing_time = time.time() - start_time
        return result
    
    async def generate_pyspark_code(self, data_description: str,
                                   operations: List[str],
                                   optimization_level: str = "standard") -> AnalysisResult:
        """
        Generate PySpark code
        
        Args:
            data_description: Data description
            operations: List of operations
            optimization_level: basic, standard, advanced
        
        Returns:
            AnalysisResult with generated code
        """
        context = """Bạn là chuyên gia PySpark. Tạo code Python ngắn gọn, chạy được ngay.

YÊU CẦU:
1. CHỈ TẠO CODE - không giải thích dài
2. Code HOÀN CHỈNH từ đầu đến cuối
3. Comments ngắn gọn
4. Best practices
5. KHÔNG CẮT CODE GIỮA CHỪNG
"""
        
        operations_text = '\n'.join([f"{i+1}. {op}" for i, op in enumerate(operations)])
        
        prompt = f"""MÔ TẢ: {data_description}

CÁC THAO TÁC:
{operations_text}

TẠO CODE PYTHON HOÀN CHỈNH (optimization: {optimization_level}):

```python
#!/usr/bin/env python3
# Code hoàn chỉnh ở đây
```"""
        
        return await self._generate_with_fallback(prompt, context)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        cache_hit_rate = (self.stats['cache_hits'] / self.stats['total_requests'] * 100
                         if self.stats['total_requests'] > 0 else 0)
        
        success_rate = (self.stats['successful_requests'] / self.stats['total_requests'] * 100
                       if self.stats['total_requests'] > 0 else 0)
        
        cost_stats = self.cost_tracker.get_stats()
        
        return {
            'requests': {
                'total': self.stats['total_requests'],
                'successful': self.stats['successful_requests'],
                'failed': self.stats['failed_requests'],
                'success_rate': f"{success_rate:.2f}%",
            },
            'cache': {
                'hits': self.stats['cache_hits'],
                'hit_rate': f"{cache_hit_rate:.2f}%",
            },
            'cost': cost_stats,
            'tokens': self.stats['total_tokens'],
            'providers': self.stats['providers_used'],
            'fallbacks': self.stats['fallback_count'],
            'primary_provider': self.config.provider.value
        }
    
    def clear_cache(self):
        """Clear cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Cache cleared")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def quick_analyze(data: str, question: str,
                       provider: AIProvider = AIProvider.GOOGLE_GEMINI_25_FLASH,
                       api_key: Optional[str] = None) -> str:
    """Quick analysis helper"""
    config = AIConfig(provider=provider, api_key=api_key)
    engine = AdvancedAIEngine(config)
    result = await engine.analyze_data(data, question)
    return result.response if result.success else f"Error: {result.error}"


def sync_analyze(data: str, question: str, **kwargs) -> str:
    """Sync wrapper"""
    return asyncio.run(quick_analyze(data, question, **kwargs))


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    async def demo():
        """Demo V8 engine"""
        print("🚀 Advanced AI Engine V8.0 Demo\n")
        
        # Sample data
        sample_data = """id,name,age,salary,department
1,John,30,50000,IT
2,Jane,25,45000,HR
3,Bob,35,60000,IT
4,Alice,28,48000,Sales
5,Charlie,32,55000,IT"""
        
        # Config with fallback
        config = AIConfig(
            provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
            fallback_providers=[
                AIProvider.GOOGLE_GEMINI_25_FLASH,
                AIProvider.ANTHROPIC_CLAUDE_3_HAIKU
            ],
            cache_enabled=True,
            daily_budget=5.0
        )
        
        engine = AdvancedAIEngine(config)
        
        # Test 1: Quick analysis
        print("1️⃣ Test Quick Analysis:")
        result = await engine.analyze_data(
            data=sample_data,
            question="Tính lương trung bình theo phòng ban và tạo code PySpark"
        )
        
        if result.success:
            print(f"✅ Success!")
            print(f"⏱️  Time: {result.processing_time:.2f}s")
            print(f"💰 Cost: ${result.cost:.4f}")
            print(f"🎯 Quality: {result.quality_score:.2%}")
            print(f"🤖 Provider: {result.provider_used}")
            print(f"💾 Cached: {result.cached}")
            print(f"\n📝 Response:\n{result.response[:500]}...")
        else:
            print(f"❌ Error: {result.error}")
        
        # Test 2: Generate code
        print("\n2️⃣ Test Generate Code:")
        result = await engine.generate_pyspark_code(
            data_description="CSV file: id, name, age, salary, department",
            operations=[
                "Đọc data từ HDFS",
                "Filter salary > 50000",
                "Group by department",
                "Calculate avg salary",
                "Sort by avg desc",
                "Save to Parquet"
            ],
            optimization_level="advanced"
        )
        
        if result.success:
            print(f"✅ Success!")
            print(f"⏱️  Time: {result.processing_time:.2f}s")
            print(f"\n📝 Code:\n{result.response[:600]}...")
        
        # Statistics
        print("\n📊 Statistics:")
        stats = engine.get_statistics()
        print(json.dumps(stats, indent=2))
    
    asyncio.run(demo())
