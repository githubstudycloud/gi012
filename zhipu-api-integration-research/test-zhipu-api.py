#!/usr/bin/env python3
"""
智谱 API 连接测试脚本
测试 API 是否可以正常访问

使用前请先设置环境变量:
  export ZHIPU_API_KEY="your-api-key"
"""

import os
import sys

def test_with_openai_sdk():
    """使用 OpenAI SDK 测试智谱 API"""
    try:
        from openai import OpenAI
    except ImportError:
        print("请先安装 openai 库: pip install openai")
        return False

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("错误: 未设置 ZHIPU_API_KEY 环境变量")
        return False

    print("正在测试智谱 API 连接...")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")

    # 测试通用端点
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.z.ai/api/paas/v4"
    )

    try:
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ],
            max_tokens=100
        )
        print("\n✅ 连接成功!")
        print(f"模型响应: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False


def test_with_requests():
    """使用 requests 库直接测试 API"""
    try:
        import requests
    except ImportError:
        print("请先安装 requests 库: pip install requests")
        return False

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("错误: 未设置 ZHIPU_API_KEY 环境变量")
        return False

    print("正在使用 requests 测试智谱 API...")

    url = "https://api.z.ai/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "glm-4.7",
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ],
        "max_tokens": 50
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        print("\n✅ 连接成功!")
        print(f"响应: {result}")
        return True
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False


def list_available_models():
    """列出可用模型"""
    print("\n可用的智谱模型:")
    print("  - glm-4.7      (最新旗舰模型, 358B MoE)")
    print("  - glm-4.6      (355B MoE, 200K 上下文)")
    print("  - glm-4.5-air  (轻量版本)")
    print("  - glm-4-plus   (增强版)")
    print("  - glm-4        (基础版)")


if __name__ == "__main__":
    print("=" * 50)
    print("智谱 API 测试工具")
    print("=" * 50)

    list_available_models()
    print()

    # 优先使用 OpenAI SDK
    success = test_with_openai_sdk()

    if not success:
        print("\n尝试使用 requests 库...")
        test_with_requests()

    print("\n" + "=" * 50)
