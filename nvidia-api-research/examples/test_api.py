#!/usr/bin/env python3
"""
NVIDIA NIM API 测试脚本

使用方法:
    export NVIDIA_API_KEY="your-api-key"
    python test_api.py

依赖:
    pip install openai
"""

import os
from openai import OpenAI


def get_client():
    """获取 NVIDIA API 客户端"""
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("请设置 NVIDIA_API_KEY 环境变量")

    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )


def test_chat_completion(client, model: str, prompt: str = "Hello!"):
    """测试对话补全"""
    print(f"\n测试模型: {model}")
    print("-" * 50)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        content = response.choices[0].message.content
        usage = response.usage

        print(f"响应: {content[:200]}...")
        print(f"Token 使用: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def test_embedding(client, model: str, text: str = "Hello world"):
    """测试嵌入生成"""
    print(f"\n测试嵌入模型: {model}")
    print("-" * 50)

    try:
        response = client.embeddings.create(
            model=model,
            input=[text],
            extra_body={"input_type": "query"}
        )

        embedding = response.data[0].embedding
        print(f"嵌入维度: {len(embedding)}")
        print(f"前5个值: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def list_models(client):
    """列出可用模型"""
    print("\n可用模型列表:")
    print("-" * 50)

    try:
        models = client.models.list()
        for model in models.data[:20]:  # 只显示前20个
            print(f"  - {model.id}")
        print(f"  ... 共 {len(models.data)} 个模型")
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("NVIDIA NIM API 测试")
    print("=" * 60)

    client = get_client()

    # 列出模型
    list_models(client)

    # 测试对话模型
    chat_models = [
        "meta/llama-3.3-70b-instruct",
        "qwen/qwq-32b",
        "microsoft/phi-4-mini-instruct",
    ]

    for model in chat_models:
        test_chat_completion(client, model)

    # 测试嵌入模型
    test_embedding(client, "nvidia/nv-embedqa-e5-v5")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
