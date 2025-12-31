"""
Advanced QR Code Decoder
高级二维码解码器 - 支持更多解码策略和详细分析
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pyzbar import pyzbar
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import struct


@dataclass
class CodeAnalysis:
    """码分析结果"""
    detected: bool
    code_type: str
    is_decodable: bool
    content: Optional[str]
    encoding_info: Dict[str, Any]
    visual_features: Dict[str, Any]
    recommendations: List[str]


class AdvancedQRDecoder:
    """高级二维码解码器"""

    def __init__(self):
        self.cv_detector = cv2.QRCodeDetector()

    def analyze_image(self, image_path: str) -> CodeAnalysis:
        """
        全面分析图片中的码

        Args:
            image_path: 图片路径

        Returns:
            详细的分析结果
        """
        img_cv = cv2.imread(image_path)
        img_pil = Image.open(image_path)

        if img_cv is None:
            return CodeAnalysis(
                detected=False,
                code_type="unknown",
                is_decodable=False,
                content=None,
                encoding_info={},
                visual_features={},
                recommendations=["无法读取图片文件"]
            )

        # 1. 尝试标准解码
        standard_result = self._try_standard_decode(img_cv, img_pil)
        if standard_result['success']:
            return CodeAnalysis(
                detected=True,
                code_type=standard_result['type'],
                is_decodable=True,
                content=standard_result['content'],
                encoding_info=standard_result.get('encoding_info', {}),
                visual_features=self._analyze_visual_features(img_cv),
                recommendations=[]
            )

        # 2. 分析视觉特征
        visual_features = self._analyze_visual_features(img_cv)

        # 3. 检测是否是小程序码
        if self._is_miniprogram_code(img_cv, visual_features):
            return CodeAnalysis(
                detected=True,
                code_type="wechat_miniprogram_code",
                is_decodable=False,
                content=None,
                encoding_info={
                    "format": "WeChat Mini Program Code (Sunflower Code)",
                    "encoding": "Proprietary encrypted",
                    "specification": "Not publicly documented"
                },
                visual_features=visual_features,
                recommendations=[
                    "微信小程序码无法通过标准库解码",
                    "解码方法:",
                    "  1. 使用微信App扫一扫功能",
                    "  2. 使用微信开放平台API (需开发者权限):",
                    "     - 调用 wxacode.get 接口",
                    "     - 需要小程序的 AppID 和 AppSecret",
                    "  3. 如果是你自己的小程序，可以通过小程序后台查看"
                ]
            )

        # 4. 尝试增强解码
        enhanced_result = self._try_enhanced_decode(img_cv, img_pil)
        if enhanced_result['success']:
            return CodeAnalysis(
                detected=True,
                code_type=enhanced_result['type'],
                is_decodable=True,
                content=enhanced_result['content'],
                encoding_info=enhanced_result.get('encoding_info', {}),
                visual_features=visual_features,
                recommendations=["使用图像增强后成功解码"]
            )

        # 5. 返回未能解码的分析结果
        return CodeAnalysis(
            detected=visual_features.get('has_code_pattern', False),
            code_type="unknown",
            is_decodable=False,
            content=None,
            encoding_info={},
            visual_features=visual_features,
            recommendations=self._generate_recommendations(visual_features)
        )

    def _try_standard_decode(self, img_cv: np.ndarray, img_pil: Image.Image) -> dict:
        """尝试标准解码方法"""
        # pyzbar
        decoded = pyzbar.decode(img_pil)
        if decoded:
            obj = decoded[0]
            return {
                'success': True,
                'type': obj.type,
                'content': obj.data.decode('utf-8', errors='ignore'),
                'encoding_info': {
                    'format': obj.type,
                    'quality': obj.quality if hasattr(obj, 'quality') else 'N/A'
                }
            }

        # OpenCV
        data, points, _ = self.cv_detector.detectAndDecode(img_cv)
        if data:
            return {
                'success': True,
                'type': 'QRCODE',
                'content': data,
                'encoding_info': {'format': 'QR Code'}
            }

        return {'success': False}

    def _try_enhanced_decode(self, img_cv: np.ndarray, img_pil: Image.Image) -> dict:
        """使用图像增强后尝试解码"""
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 增强策略列表
        strategies = [
            ('adaptive_threshold', lambda: cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
            ('otsu', lambda: cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
            ('contrast_enhance', lambda: self._enhance_contrast(gray)),
            ('denoise', lambda: cv2.fastNlMeansDenoising(gray)),
            ('sharpen', lambda: self._sharpen(gray)),
            ('resize_up', lambda: cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)),
            ('morphology', lambda: self._morphology_enhance(gray)),
        ]

        for name, strategy in strategies:
            try:
                processed = strategy()
                pil_img = Image.fromarray(processed)
                decoded = pyzbar.decode(pil_img)
                if decoded:
                    obj = decoded[0]
                    return {
                        'success': True,
                        'type': obj.type,
                        'content': obj.data.decode('utf-8', errors='ignore'),
                        'encoding_info': {
                            'format': obj.type,
                            'enhancement': name
                        }
                    }
            except Exception:
                continue

        return {'success': False}

    def _enhance_contrast(self, gray: np.ndarray) -> np.ndarray:
        """增强对比度"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def _sharpen(self, gray: np.ndarray) -> np.ndarray:
        """锐化"""
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        return cv2.filter2D(gray, -1, kernel)

    def _morphology_enhance(self, gray: np.ndarray) -> np.ndarray:
        """形态学增强"""
        kernel = np.ones((3, 3), np.uint8)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    def _analyze_visual_features(self, img: np.ndarray) -> dict:
        """分析图片的视觉特征"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        features = {
            'image_size': (w, h),
            'has_code_pattern': False,
            'is_circular': False,
            'has_finder_patterns': False,
            'dominant_shape': 'unknown',
            'estimated_code_type': 'unknown'
        }

        # 检测圆形
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 50,
            param1=50, param2=30,
            minRadius=30, maxRadius=min(w, h) // 2
        )
        if circles is not None:
            features['is_circular'] = True
            features['circle_count'] = len(circles[0])

        # 检测矩形/方形
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        rect_count = 0
        square_count = 0
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
            if len(approx) == 4:
                rect_count += 1
                x, y, w_rect, h_rect = cv2.boundingRect(approx)
                aspect_ratio = float(w_rect) / h_rect
                if 0.9 < aspect_ratio < 1.1:
                    square_count += 1

        features['rectangle_count'] = rect_count
        features['square_count'] = square_count

        # 检测QR码定位图案
        features['has_finder_patterns'] = self._detect_finder_patterns(gray)

        # 判断码类型
        if features['is_circular'] and not features['has_finder_patterns']:
            features['estimated_code_type'] = 'miniprogram_code'
            features['has_code_pattern'] = True
        elif features['has_finder_patterns']:
            features['estimated_code_type'] = 'qr_code'
            features['has_code_pattern'] = True
        elif rect_count > 0:
            features['has_code_pattern'] = True

        return features

    def _detect_finder_patterns(self, gray: np.ndarray) -> bool:
        """检测QR码的定位图案（三个角的方形图案）"""
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if hierarchy is None:
            return False

        # QR码定位图案的特征：嵌套的方形轮廓
        finder_pattern_count = 0

        for i, cnt in enumerate(contours):
            # 检查是否有嵌套轮廓
            if hierarchy[0][i][2] != -1:  # 有子轮廓
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
                if len(approx) == 4:  # 四边形
                    area = cv2.contourArea(cnt)
                    if area > 100:  # 面积足够大
                        # 检查内部嵌套
                        child_idx = hierarchy[0][i][2]
                        if child_idx != -1:
                            child_cnt = contours[child_idx]
                            child_peri = cv2.arcLength(child_cnt, True)
                            child_approx = cv2.approxPolyDP(child_cnt, 0.04 * child_peri, True)
                            if len(child_approx) == 4:
                                finder_pattern_count += 1

        return finder_pattern_count >= 3

    def _is_miniprogram_code(self, img: np.ndarray, features: dict) -> bool:
        """判断是否是微信小程序码"""
        # 小程序码的特征：
        # 1. 整体呈圆形
        # 2. 没有QR码的定位图案
        # 3. 内部有放射状的点阵图案

        if not features.get('is_circular', False):
            return False

        if features.get('has_finder_patterns', False):
            return False

        # 进一步检查内部图案
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 统计小轮廓数量（小程序码有很多小点）
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        small_contours = sum(1 for cnt in contours if 5 < cv2.contourArea(cnt) < 500)

        return small_contours > 100

    def _generate_recommendations(self, features: dict) -> List[str]:
        """根据视觉特征生成建议"""
        recommendations = []

        if features.get('is_circular', False):
            recommendations.append("检测到圆形图案，可能是:")
            recommendations.append("  - 微信小程序码 (无法用标准库解码)")
            recommendations.append("  - 其他专有格式的圆形码")

        if not features.get('has_code_pattern', False):
            recommendations.append("未检测到明显的码图案，可能原因:")
            recommendations.append("  - 图片质量不佳")
            recommendations.append("  - 码被遮挡或裁剪")
            recommendations.append("  - 图片中不包含二维码")

        if features.get('estimated_code_type') == 'miniprogram_code':
            recommendations.extend([
                "",
                "【关于微信小程序码】",
                "小程序码（也叫太阳码）是微信专有格式，特点:",
                "  1. 圆形外观，中心有三个定位点",
                "  2. 使用专有加密编码",
                "  3. 只能通过微信解析",
                "",
                "获取小程序码内容的方法:",
                "  1. 微信扫一扫",
                "  2. 微信开发者工具",
                "  3. 调用微信官方API (需要开发者权限)"
            ])

        return recommendations


def analyze_qrcode(image_path: str) -> CodeAnalysis:
    """
    分析二维码的便捷函数

    Args:
        image_path: 图片路径

    Returns:
        详细的分析结果
    """
    decoder = AdvancedQRDecoder()
    return decoder.analyze_image(image_path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python advanced_decoder.py <image_path>")
        sys.exit(1)

    result = analyze_qrcode(sys.argv[1])

    print("\n" + "="*60)
    print("二维码分析结果")
    print("="*60)
    print(f"检测到码: {'是' if result.detected else '否'}")
    print(f"码类型: {result.code_type}")
    print(f"可解码: {'是' if result.is_decodable else '否'}")

    if result.content:
        print(f"内容: {result.content}")

    if result.encoding_info:
        print("\n编码信息:")
        for k, v in result.encoding_info.items():
            print(f"  {k}: {v}")

    if result.visual_features:
        print("\n视觉特征:")
        for k, v in result.visual_features.items():
            print(f"  {k}: {v}")

    if result.recommendations:
        print("\n建议和说明:")
        for rec in result.recommendations:
            print(f"  {rec}")
