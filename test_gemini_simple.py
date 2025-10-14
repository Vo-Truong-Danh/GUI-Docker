#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Gemini 2.5 Flash model (Free Tier)"""

try:
    import google.generativeai as genai
    
    # Configure
    api_key = "AIzaSyBAXWlXvoEgO36ZW7dQlxsq06y_5v_MEi8"
    genai.configure(api_key=api_key)
    
    print("🧪 Testing Free Tier Models...\n")
    
    # Test free tier models (không bị quota limit)
    free_models = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest",
        "models/gemini-2.5-flash-lite",
    ]
    
    for model_name in free_models:
        print(f"Testing: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'OK' if working")
            print(f"  ✅ SUCCESS: {response.text.strip()}\n")
            break  # Tìm được model hoạt động rồi, dừng lại
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"  ⚠️  QUOTA LIMIT (đợi 1 phút)\n")
            elif "404" in error_msg:
                print(f"  ❌ NOT FOUND\n")
            else:
                print(f"  ❌ {error_msg[:100]}\n")
    
    print("="*60)
    print("💡 Recommended for app: models/gemini-2.5-flash")
    print("   (Free, fast, no quota issues)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
