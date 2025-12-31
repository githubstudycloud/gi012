"""
QR Code Decoder Module
支持多种二维码类型的解码和识别
"""

import cv2
import numpy as np
from PIL import Image
from pyzbar import pyzbar
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import math


class QRCodeType(Enum):
    """二维码类型枚举"""
    STANDARD_QR = "standard_qr"           # 标准QR码
    WECHAT_MINIPROGRAM = "wechat_mini"    # 微信小程序码（圆形太阳码）
    WECHAT_QR = "wechat_qr"               # 微信普通二维码
    BARCODE = "barcode"                    # 条形码
    DATAMATRIX = "datamatrix"             # DataMatrix码
    PDF417 = "pdf417"                      # PDF417码
    AZTEC = "aztec"                        # Aztec码
    UNKNOWN = "unknown"                    # 未知类型


@dataclass
class QRCodeResult:
    """二维码解码结果"""
    success: bool                          # 是否成功解码
    qr_type: QRCodeType                    # 二维码类型
    content: Optional[str]                 # 解码内容
    content_type: Optional[str]            # 内容类型 (url, text, vcard, etc.)
    rect: Optional[Tuple[int, int, int, int]]  # 位置 (x, y, width, height)
    confidence: float                      # 置信度
    message: str                           # 附加信息


class QRCodeDecoder:
    """二维码解码器"""

    def __init__(self):
        # OpenCV QR检测器
        self.cv_detector = cv2.QRCodeDetector()
        # WeChat专用检测器 (如果可用)
        try:
            self.wechat_detector = cv2.wechat_qrcode_WeChatQRCode()
            self.has_wechat_detector = True
        except:
            self.has_wechat_detector = False

    def decode(self, image_path: str) -> List[QRCodeResult]:
        """
        解码图片中的所有二维码

        Args:
            image_path: 图片路径

        Returns:
            解码结果列表
        """
        results = []

        # 读取图片
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            return [QRCodeResult(
                success=False,
                qr_type=QRCodeType.UNKNOWN,
                content=None,
                content_type=None,
                rect=None,
                confidence=0.0,
                message=f"无法读取图片: {image_path}"
            )]

        img_pil = Image.open(image_path)

        # 1. 首先检测是否是小程序码
        miniprogram_result = self._detect_miniprogram_code(img_cv)
        if miniprogram_result:
            results.append(miniprogram_result)

        # 2. 使用pyzbar解码 (支持多种格式)
        pyzbar_results = self._decode_with_pyzbar(img_pil)
        results.extend(pyzbar_results)

        # 3. 使用OpenCV解码
        if not pyzbar_results:
            opencv_results = self._decode_with_opencv(img_cv)
            results.extend(opencv_results)

        # 4. 使用WeChat检测器 (如果可用)
        if self.has_wechat_detector and not results:
            wechat_results = self._decode_with_wechat(img_cv)
            results.extend(wechat_results)

        # 5. 如果没有找到任何码，进行预处理后重试
        if not results:
            preprocessed_results = self._decode_with_preprocessing(img_cv, img_pil)
            results.extend(preprocessed_results)

        # 去重
        results = self._deduplicate_results(results)

        if not results:
            results.append(QRCodeResult(
                success=False,
                qr_type=QRCodeType.UNKNOWN,
                content=None,
                content_type=None,
                rect=None,
                confidence=0.0,
                message="未检测到任何二维码或条形码"
            ))

        return results

    def _detect_miniprogram_code(self, img: np.ndarray) -> Optional[QRCodeResult]:
        """
        检测微信小程序码（圆形太阳码）

        小程序码特征：
        1. 圆形外观
        2. 中心有三个定位点呈三角形排列
        3. 使用微信专有编码，无法用标准库解码
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 检测圆形
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=50,
            param2=30,
            minRadius=30,
            maxRadius=min(img.shape[0], img.shape[1]) // 2
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                x, y, r = circle

                # 提取圆形区域
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)
                roi = cv2.bitwise_and(gray, gray, mask=mask)

                # 检测内部是否有类似小程序码的特征
                if self._has_miniprogram_pattern(roi, x, y, r):
                    return QRCodeResult(
                        success=False,  # 无法解码内容
                        qr_type=QRCodeType.WECHAT_MINIPROGRAM,
                        content=None,
                        content_type="wechat_miniprogram",
                        rect=(int(x-r), int(y-r), int(2*r), int(2*r)),
                        confidence=0.8,
                        message="检测到微信小程序码（圆形太阳码）。"
                                "此类型二维码使用微信专有加密编码，"
                                "无法通过标准库解码。"
                                "只能通过微信扫一扫或调用微信官方API解析。"
                    )

        return None

    def _has_miniprogram_pattern(self, roi: np.ndarray, cx: int, cy: int, r: int) -> bool:
        """检测是否有小程序码的图案特征"""
        # 二值化
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 查找轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # 小程序码通常有很多小的点状图案
        small_contours = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 10 < area < (r * r * 0.01):  # 小面积轮廓
                small_contours += 1

        # 如果有足够多的小轮廓，可能是小程序码
        return small_contours > 50

    def _decode_with_pyzbar(self, img: Image.Image) -> List[QRCodeResult]:
        """使用pyzbar库解码"""
        results = []

        # 解码
        decoded = pyzbar.decode(img)

        for obj in decoded:
            qr_type = self._map_pyzbar_type(obj.type)
            content = obj.data.decode('utf-8', errors='ignore')
            content_type = self._detect_content_type(content)

            rect = obj.rect
            results.append(QRCodeResult(
                success=True,
                qr_type=qr_type,
                content=content,
                content_type=content_type,
                rect=(rect.left, rect.top, rect.width, rect.height),
                confidence=1.0,
                message=f"使用pyzbar成功解码 {obj.type}"
            ))

        return results

    def _decode_with_opencv(self, img: np.ndarray) -> List[QRCodeResult]:
        """使用OpenCV解码"""
        results = []

        # 尝试标准检测
        data, points, _ = self.cv_detector.detectAndDecode(img)

        if data:
            rect = None
            if points is not None:
                pts = points[0]
                x = int(min(pts[:, 0]))
                y = int(min(pts[:, 1]))
                w = int(max(pts[:, 0]) - x)
                h = int(max(pts[:, 1]) - y)
                rect = (x, y, w, h)

            content_type = self._detect_content_type(data)
            results.append(QRCodeResult(
                success=True,
                qr_type=QRCodeType.STANDARD_QR,
                content=data,
                content_type=content_type,
                rect=rect,
                confidence=1.0,
                message="使用OpenCV成功解码"
            ))

        return results

    def _decode_with_wechat(self, img: np.ndarray) -> List[QRCodeResult]:
        """使用OpenCV WeChat检测器解码"""
        results = []

        if not self.has_wechat_detector:
            return results

        try:
            data_list, points_list = self.wechat_detector.detectAndDecode(img)

            for i, data in enumerate(data_list):
                if data:
                    rect = None
                    if points_list and len(points_list) > i:
                        pts = points_list[i]
                        x = int(min(pts[:, 0]))
                        y = int(min(pts[:, 1]))
                        w = int(max(pts[:, 0]) - x)
                        h = int(max(pts[:, 1]) - y)
                        rect = (x, y, w, h)

                    content_type = self._detect_content_type(data)
                    results.append(QRCodeResult(
                        success=True,
                        qr_type=QRCodeType.WECHAT_QR,
                        content=data,
                        content_type=content_type,
                        rect=rect,
                        confidence=1.0,
                        message="使用WeChat检测器成功解码"
                    ))
        except Exception as e:
            pass

        return results

    def _decode_with_preprocessing(self, img_cv: np.ndarray, img_pil: Image.Image) -> List[QRCodeResult]:
        """对图片进行预处理后再解码"""
        results = []

        # 转灰度
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 预处理方法列表
        preprocessors = [
            # 自适应阈值
            lambda: cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2),
            # OTSU阈值
            lambda: cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 增强对比度
            lambda: cv2.equalizeHist(gray),
            # 高斯模糊后二值化
            lambda: cv2.threshold(cv2.GaussianBlur(gray, (5, 5), 0), 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            # 形态学操作
            lambda: cv2.morphologyEx(
                cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8)
            ),
        ]

        for preprocess in preprocessors:
            try:
                processed = preprocess()

                # 使用pyzbar
                pil_processed = Image.fromarray(processed)
                decoded = pyzbar.decode(pil_processed)

                for obj in decoded:
                    qr_type = self._map_pyzbar_type(obj.type)
                    content = obj.data.decode('utf-8', errors='ignore')

                    # 检查是否已存在相同内容
                    if not any(r.content == content for r in results):
                        content_type = self._detect_content_type(content)
                        rect = obj.rect
                        results.append(QRCodeResult(
                            success=True,
                            qr_type=qr_type,
                            content=content,
                            content_type=content_type,
                            rect=(rect.left, rect.top, rect.width, rect.height),
                            confidence=0.9,
                            message=f"使用图像预处理后成功解码"
                        ))

                if results:
                    break

            except Exception:
                continue

        return results

    def _map_pyzbar_type(self, pyzbar_type: str) -> QRCodeType:
        """映射pyzbar类型到QRCodeType"""
        type_map = {
            'QRCODE': QRCodeType.STANDARD_QR,
            'EAN13': QRCodeType.BARCODE,
            'EAN8': QRCodeType.BARCODE,
            'UPCA': QRCodeType.BARCODE,
            'UPCE': QRCodeType.BARCODE,
            'CODE128': QRCodeType.BARCODE,
            'CODE39': QRCodeType.BARCODE,
            'CODE93': QRCodeType.BARCODE,
            'DATAMATRIX': QRCodeType.DATAMATRIX,
            'PDF417': QRCodeType.PDF417,
            'AZTEC': QRCodeType.AZTEC,
        }
        return type_map.get(pyzbar_type, QRCodeType.UNKNOWN)

    def _detect_content_type(self, content: str) -> str:
        """检测内容类型"""
        if not content:
            return "empty"

        content_lower = content.lower()

        # URL
        if content_lower.startswith(('http://', 'https://', 'www.')):
            return "url"

        # 微信相关
        if 'weixin.qq.com' in content_lower or content_lower.startswith('wxp://'):
            return "wechat_url"

        # 支付宝
        if 'alipay' in content_lower or content_lower.startswith('alipays://'):
            return "alipay_url"

        # 邮件
        if content_lower.startswith('mailto:'):
            return "email"

        # 电话
        if content_lower.startswith('tel:'):
            return "phone"

        # WiFi
        if content_lower.startswith('wifi:'):
            return "wifi"

        # vCard
        if content_lower.startswith('begin:vcard'):
            return "vcard"

        # 纯数字（可能是会员码等）
        if content.isdigit():
            return "numeric"

        return "text"

    def _deduplicate_results(self, results: List[QRCodeResult]) -> List[QRCodeResult]:
        """去除重复结果"""
        seen_contents = set()
        unique_results = []

        for result in results:
            key = (result.content, result.qr_type)
            if key not in seen_contents:
                seen_contents.add(key)
                unique_results.append(result)

        return unique_results


def decode_qrcode(image_path: str) -> List[QRCodeResult]:
    """
    便捷函数：解码图片中的二维码

    Args:
        image_path: 图片路径

    Returns:
        解码结果列表
    """
    decoder = QRCodeDecoder()
    return decoder.decode(image_path)
