#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test AI Engine V8.1 - Fix Truncated Responses
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_spark_gui'))

try:
    from advanced_ai_engine_v8 import (
        AdvancedAIEngine, AIConfig, AIProvider
    )
    ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    ENGINE_AVAILABLE = False


async def test_code_generation():
    """Test code generation with V8.1 improvements"""
    
    if not ENGINE_AVAILABLE:
        print("❌ AI Engine not available")
        return
    
    print("🧪 Testing AI Engine V8.1 - Code Generation Fix\n")
    print("="*70)
    
    # Config optimized for code generation
    config = AIConfig(
        provider=AIProvider.GOOGLE_GEMINI_25_FLASH,
        max_tokens=2048,  # V8.3: Limited to force conciseness
        temperature=0.0,  # V8.3: Zero for deterministic (0.1→0.0)
        cache_enabled=False,  # Fresh code each time
        min_quality_score=0.7,
        enable_quality_check=True
    )
    
    engine = AdvancedAIEngine(config)
    
    # Test 1: Simple code generation
    print("\n1️⃣ Test: Simple Code Generation")
    print("-" * 70)
    
    sample_data = """id,name,age,salary
1,John,30,50000
2,Jane,25,45000
3,Bob,35,60000"""
    
    question = """Read CSV, calculate average salary, print result.

CODE ONLY."""
    
    try:
        result = await engine.analyze_data(sample_data, question)
        
        if result.success:
            print(f"✅ Status: Success")
            print(f"⏱️  Time: {result.processing_time:.2f}s")
            print(f"💰 Cost: ${result.cost:.4f}")
            print(f"🎯 Quality: {result.quality_score:.1%}")
            print(f"📊 Tokens: {result.tokens_used}")
            print(f"🤖 Provider: {result.provider_used}")
            
            # Check for truncation
            is_complete = (
                result.quality_score >= 0.7 and
                not result.response.endswith('...') and
                result.response.count('```') >= 2
            )
            
            print(f"✅ Complete: {'Yes' if is_complete else 'No ⚠️'}")
            
            print(f"\n📝 Response:")
            print("=" * 70)
            print(result.response)
            print("=" * 70)
            
            if not is_complete:
                print("\n⚠️ WARNING: Response may be incomplete!")
        else:
            print(f"❌ Error: {result.error}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: PySpark code generation
    print("\n\n2️⃣ Test: PySpark Code Generation")
    print("-" * 70)
    
    question2 = """PySpark code to count word "snape" in text file (case-insensitive).

CODE ONLY. MAX 40 LINES."""
    
    try:
        result = await engine.analyze_data("", question2)
        
        if result.success:
            print(f"✅ Status: Success")
            print(f"⏱️  Time: {result.processing_time:.2f}s")
            print(f"🎯 Quality: {result.quality_score:.1%}")
            
            is_complete = (
                result.quality_score >= 0.7 and
                'def ' in result.response and
                'if __name__' in result.response
            )
            
            print(f"✅ Complete: {'Yes' if is_complete else 'No ⚠️'}")
            
            print(f"\n📝 Response (first 1000 chars):")
            print("=" * 70)
            print(result.response[:1000])
            if len(result.response) > 1000:
                print(f"\n... ({len(result.response)-1000} more chars)")
            print("=" * 70)
        else:
            print(f"❌ Error: {result.error}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Statistics
    print("\n\n📊 Engine Statistics")
    print("=" * 70)
    stats = engine.get_statistics()
    
    print(f"Total requests: {stats['requests']['total']}")
    print(f"Successful: {stats['requests']['successful']}")
    print(f"Failed: {stats['requests']['failed']}")
    print(f"Success rate: {stats['requests']['success_rate']}")
    print(f"Today cost: ${stats['cost']['today_cost']:.4f}")
    print(f"Budget left: ${stats['cost']['remaining_budget']:.2f}")
    
    print("\n✅ Tests completed!")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║             🤖 AI ENGINE V8.3 - SYSTEM INSTRUCTION FIX           ║
║                                                                   ║
║  V8.3 Changes (EXTREME):                                          ║
║  • temperature: 0.1 → 0.0 (100% deterministic)                   ║
║  • max_tokens: 8192 → 2048 (force conciseness)                   ║
║  • System instruction in GenerativeModel                          ║
║  • stop_sequences to prevent explanations                        ║
║  • English prompts (simpler for AI)                              ║
║                                                                   ║
║  System instruction: "You are CODE GENERATOR MACHINE"            ║
║  Rule: NO explanations, ONLY code, MAX 50 lines                  ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(test_code_generation())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
