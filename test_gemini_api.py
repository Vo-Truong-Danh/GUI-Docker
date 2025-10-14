#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Gemini API models"""

try:
    import google.generativeai as genai
    import os
    
    # Configure API
    api_key = os.getenv("GOOGLE_API_KEY") or "AIzaSyBAXWlXvoEgO36ZW7dQlxsq06y_5v_MEi8"
    print(f"🔑 Using API Key: {api_key[:20]}...")
    genai.configure(api_key=api_key)
    
    print("\n🔍 Listing Available Gemini Models...\n")
    
    # List ALL models with details
    print("📋 Available Models:")
    available_models = []
    for m in genai.list_models():
        print(f"\n  Model: {m.name}")
        print(f"    Display: {m.display_name}")
        print(f"    Methods: {m.supported_generation_methods}")
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"    ✅ Supports generateContent")
    
    print("\n" + "="*60)
    print(f"\n✅ Found {len(available_models)} compatible models:")
    for m in available_models:
        print(f"  • {m}")
    
    print("\n" + "="*60)
    
    # Test first available model
    if available_models:
        test_model = available_models[0]
        print(f"\n🧪 Testing: {test_model}")
        try:
            model = genai.GenerativeModel(test_model)
            response = model.generate_content("Say 'Hello World' if you work correctly.")
            print(f"  ✅ SUCCESS!")
            print(f"  Response: {response.text.strip()}")
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
    else:
        print("\n❌ No compatible models found!")
    
    print("\n" + "="*60)
    print("\n✅ Test complete!")
    print(f"\n💡 Recommended model: {available_models[0] if available_models else 'None'}")
    
except ImportError:
    print("❌ google-generativeai not installed!")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
