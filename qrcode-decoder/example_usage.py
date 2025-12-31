#!/usr/bin/env python3
"""
示例：如何使用QR Code Decoder

这个脚本展示了如何使用qr_decoder模块解码各种类型的二维码
"""

from qr_decoder import QRCodeDecoder, decode_qrcode, QRCodeType
from advanced_decoder import analyze_qrcode


def example_basic_usage():
    """基本用法示例"""
    print("="*60)
    print("示例1: 基本用法")
    print("="*60)

    # 假设有一个图片文件
    image_path = "your_qrcode_image.png"

    # 方式1: 使用便捷函数
    results = decode_qrcode(image_path)

    for result in results:
        if result.success:
            print(f"✓ 成功解码!")
            print(f"  类型: {result.qr_type.value}")
            print(f"  内容: {result.content}")
            print(f"  内容类型: {result.content_type}")
        else:
            print(f"✗ 无法解码")
            print(f"  类型: {result.qr_type.value}")
            print(f"  原因: {result.message}")


def example_check_miniprogram():
    """检测小程序码示例"""
    print("\n" + "="*60)
    print("示例2: 检测微信小程序码")
    print("="*60)

    image_path = "miniprogram_code.png"

    results = decode_qrcode(image_path)

    for result in results:
        if result.qr_type == QRCodeType.WECHAT_MINIPROGRAM:
            print("检测到微信小程序码!")
            print("这种码无法通过标准库解码")
            print("请使用微信扫一扫获取内容")
        elif result.success:
            print(f"这是普通二维码，内容: {result.content}")


def example_advanced_analysis():
    """高级分析示例"""
    print("\n" + "="*60)
    print("示例3: 高级分析")
    print("="*60)

    image_path = "unknown_code.png"

    analysis = analyze_qrcode(image_path)

    print(f"检测到码: {analysis.detected}")
    print(f"码类型: {analysis.code_type}")
    print(f"可解码: {analysis.is_decodable}")

    if analysis.content:
        print(f"内容: {analysis.content}")

    if analysis.recommendations:
        print("\n建议:")
        for rec in analysis.recommendations:
            print(f"  {rec}")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "="*60)
    print("示例4: 批量处理多张图片")
    print("="*60)

    from pathlib import Path

    # 获取目录下所有图片
    image_dir = Path("./images")
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}

    if not image_dir.exists():
        print(f"目录不存在: {image_dir}")
        return

    decoder = QRCodeDecoder()

    for img_path in image_dir.iterdir():
        if img_path.suffix.lower() in image_extensions:
            print(f"\n处理: {img_path.name}")
            results = decoder.decode(str(img_path))

            for result in results:
                if result.success:
                    print(f"  ✓ {result.content[:50]}...")
                elif result.qr_type == QRCodeType.WECHAT_MINIPROGRAM:
                    print(f"  ⚠ 小程序码 (无法解码)")
                else:
                    print(f"  ✗ 未检测到码")


def example_content_type_handling():
    """处理不同内容类型示例"""
    print("\n" + "="*60)
    print("示例5: 根据内容类型处理")
    print("="*60)

    results = decode_qrcode("qrcode.png")

    for result in results:
        if not result.success:
            continue

        content_type = result.content_type
        content = result.content

        if content_type == "url":
            print(f"检测到URL: {content}")
            # 可以用浏览器打开
            # import webbrowser
            # webbrowser.open(content)

        elif content_type == "wechat_url":
            print(f"检测到微信链接: {content}")
            # 微信相关处理

        elif content_type == "email":
            print(f"检测到邮箱: {content}")
            # 邮箱处理

        elif content_type == "phone":
            print(f"检测到电话: {content}")
            # 电话处理

        elif content_type == "wifi":
            print(f"检测到WiFi配置: {content}")
            # WiFi配置解析

        elif content_type == "vcard":
            print(f"检测到名片: {content[:100]}...")
            # 解析vCard

        else:
            print(f"检测到文本: {content}")


def main():
    """
    运行所有示例

    注意：这些示例需要实际的图片文件才能运行
    请将示例中的图片路径替换为实际的图片路径
    """
    print("QR Code Decoder 使用示例")
    print("注意: 请将示例中的图片路径替换为实际的图片路径")
    print()

    # 这里只展示代码结构，实际运行需要有效的图片文件
    # example_basic_usage()
    # example_check_miniprogram()
    # example_advanced_analysis()
    # example_batch_processing()
    # example_content_type_handling()

    print("请查看代码了解具体用法")


if __name__ == '__main__':
    main()
