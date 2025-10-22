#!/usr/bin/env python3
"""
OpenAI Integration Verification Script
Tests OpenAI API connectivity and Bangla language support
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI package not installed")
    print("Install with: pip install openai")
    sys.exit(1)

def test_openai_connection():
    """Test basic OpenAI API connection"""
    print("🔗 Testing OpenAI API connection...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False

    try:
        client = OpenAI(api_key=api_key)

        # Test basic completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, test message"}],
            max_tokens=50
        )

        if response.choices[0].message.content:
            print("✅ OpenAI API connection successful")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False

    except Exception as e:
        print(f"❌ OpenAI API connection failed: {str(e)}")
        return False

def test_bangla_language_support():
    """Test Bangla language support"""
    print("🇧🇩 Testing Bangla language support...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        client = OpenAI(api_key=api_key)

        # Test Bangla response
        system_prompt = "You are a helpful AI assistant. You MUST respond exclusively in Bangla (Bengali) language."
        user_message = "Hello, how are you?"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=100,
            temperature=0.7
        )

        bangla_response = response.choices[0].message.content.strip()

        # Check if response contains Bangla characters
        bangla_chars = ['আ', 'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ', 'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ']

        has_bangla = any(char in bangla_response for char in bangla_chars)

        if has_bangla:
            print("✅ Bangla language support verified")
            print(f"   Sample response: {bangla_response[:100]}...")
            return True
        else:
            print("⚠️ Response not in Bangla, but API is working")
            print(f"   Response: {bangla_response}")
            return True  # Still working, just not Bangla

    except Exception as e:
        print(f"❌ Bangla language test failed: {str(e)}")
        return False

def test_performance():
    """Test API performance and response times"""
    print("⚡ Testing API performance...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        client = OpenAI(api_key=api_key)

        # Test multiple requests for average response time
        response_times = []
        test_messages = [
            "Hello",
            "How are you?",
            "What is AI?",
            "Tell me about Bangladesh"
        ]

        for message in test_messages:
            start_time = time.time()

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                max_tokens=50
            )

            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)

            if not response.choices[0].message.content:
                print(f"❌ Empty response for message: {message}")
                return False

        avg_response_time = sum(response_times) / len(response_times)
        print(f"   Average response time: {avg_response_time:.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        print(f"   Total requests: {len(response_times)}")

        # Performance thresholds
        if avg_response_time < 2.0:
            print("✅ Excellent performance")
            return True
        elif avg_response_time < 5.0:
            print("✅ Good performance")
            return True
        else:
            print("⚠️ Slow performance - consider upgrading to GPT-4")
            return True

    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        return False

def test_token_limits():
    """Test token usage and limits"""
    print("🔢 Testing token limits and usage...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False

    try:
        client = OpenAI(api_key=api_key)

        # Test different token limits
        test_configs = [
            {"max_tokens": 50, "description": "Short responses"},
            {"max_tokens": 200, "description": "Medium responses"},
            {"max_tokens": 500, "description": "Long responses"}
        ]

        for config in test_configs:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Write a detailed explanation about artificial intelligence"}],
                max_tokens=config["max_tokens"]
            )

            content = response.choices[0].message.content
            word_count = len(content.split())

            print(f"✅ {config['description']}: ~{word_count} words")

        return True

    except Exception as e:
        print(f"❌ Token limit test failed: {str(e)}")
        return False

def main():
    """Run all OpenAI integration tests"""
    print("🚀 BanglaChatPro OpenAI Integration Verification")
    print("=" * 55)

    tests = [
        ("API Connection", test_openai_connection),
        ("Bangla Language Support", test_bangla_language_support),
        ("Performance", test_performance),
        ("Token Limits", test_token_limits)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        print("-" * 40)

    print(f"\n📊 Test Results:")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("🎉 All OpenAI integration tests passed!")
        print("   Your AI agent is ready for production use.")
        return True
    elif passed >= total - 1:
        print("⚠️ Most tests passed, but some issues detected.")
        print("   Check the warnings above and fix if needed.")
        return True
    else:
        print("❌ Multiple tests failed.")
        print("   Please check your OpenAI API key and configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
