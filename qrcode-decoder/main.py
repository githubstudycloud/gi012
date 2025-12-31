#!/usr/bin/env python3
"""
QR Code Decoder - 二维码解码工具
支持标准QR码、条形码解码，并能识别微信小程序码

用法:
    python main.py <image_path>
    python main.py <image_path> --json
    python main.py <image_path> --save-roi
"""

import sys
import json
import argparse
from pathlib import Path
from qr_decoder import QRCodeDecoder, QRCodeResult, QRCodeType


def print_result(result: QRCodeResult, index: int = 0):
    """格式化打印解码结果"""
    print(f"\n{'='*60}")
    print(f"结果 #{index + 1}")
    print(f"{'='*60}")

    status = "✓ 成功" if result.success else "✗ 失败"
    print(f"状态: {status}")
    print(f"类型: {get_type_name(result.qr_type)}")

    if result.content:
        print(f"内容: {result.content}")
        print(f"内容类型: {result.content_type}")

    if result.rect:
        print(f"位置: x={result.rect[0]}, y={result.rect[1]}, "
              f"w={result.rect[2]}, h={result.rect[3]}")

    print(f"置信度: {result.confidence:.2%}")
    print(f"说明: {result.message}")


def get_type_name(qr_type: QRCodeType) -> str:
    """获取类型的中文名称"""
    names = {
        QRCodeType.STANDARD_QR: "标准QR码",
        QRCodeType.WECHAT_MINIPROGRAM: "微信小程序码 (圆形太阳码)",
        QRCodeType.WECHAT_QR: "微信二维码",
        QRCodeType.BARCODE: "条形码",
        QRCodeType.DATAMATRIX: "DataMatrix码",
        QRCodeType.PDF417: "PDF417码",
        QRCodeType.AZTEC: "Aztec码",
        QRCodeType.UNKNOWN: "未知类型",
    }
    return names.get(qr_type, str(qr_type))


def result_to_dict(result: QRCodeResult) -> dict:
    """将结果转换为字典"""
    return {
        "success": result.success,
        "type": result.qr_type.value,
        "type_name": get_type_name(result.qr_type),
        "content": result.content,
        "content_type": result.content_type,
        "rect": result.rect,
        "confidence": result.confidence,
        "message": result.message,
    }


def main():
    parser = argparse.ArgumentParser(
        description='QR Code Decoder - 二维码解码工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python main.py image.png
    python main.py image.jpg --json
    python main.py screenshot.png --save-roi

支持的码类型:
    - 标准QR码 (可解码)
    - 条形码 EAN-13/EAN-8/UPC-A/UPC-E/Code128/Code39 (可解码)
    - DataMatrix码 (可解码)
    - PDF417码 (可解码)
    - 微信小程序码/太阳码 (仅识别，无法解码)

关于微信小程序码:
    圆形的微信小程序码（也叫太阳码）使用微信专有的加密编码，
    无法通过任何开源库解码。只能通过以下方式获取内容:
    1. 使用微信扫一扫
    2. 调用微信官方API (需要小程序开发者权限)
        """
    )

    parser.add_argument('image', help='要解码的图片路径')
    parser.add_argument('--json', action='store_true', help='以JSON格式输出结果')
    parser.add_argument('--save-roi', action='store_true', help='保存检测到的区域图片')

    args = parser.parse_args()

    # 检查文件存在
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"错误: 文件不存在 - {args.image}", file=sys.stderr)
        sys.exit(1)

    # 解码
    decoder = QRCodeDecoder()
    results = decoder.decode(str(image_path))

    # 输出结果
    if args.json:
        output = {
            "file": str(image_path),
            "results": [result_to_dict(r) for r in results]
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"\n处理文件: {image_path}")
        print(f"检测到 {len(results)} 个结果")

        for i, result in enumerate(results):
            print_result(result, i)

        # 总结
        print(f"\n{'='*60}")
        print("总结")
        print(f"{'='*60}")

        success_count = sum(1 for r in results if r.success)
        miniprogram_count = sum(1 for r in results if r.qr_type == QRCodeType.WECHAT_MINIPROGRAM)

        print(f"成功解码: {success_count} 个")

        if miniprogram_count > 0:
            print(f"\n⚠️  检测到 {miniprogram_count} 个微信小程序码")
            print("   小程序码使用微信专有加密，无法通过标准库解码")
            print("   请使用微信扫一扫获取内容")

    # 保存ROI
    if args.save_roi:
        import cv2
        img = cv2.imread(str(image_path))
        for i, result in enumerate(results):
            if result.rect:
                x, y, w, h = result.rect
                roi = img[y:y+h, x:x+w]
                roi_path = image_path.stem + f"_roi_{i}.png"
                cv2.imwrite(roi_path, roi)
                print(f"保存ROI: {roi_path}")

    # 返回码
    if any(r.success for r in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
